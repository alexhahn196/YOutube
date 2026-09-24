#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Immobilienfotos automatisch für ein Exposé aufbereiten.

Aufruf:
    python process_real_estate_photos.py ./input_photos

Die fertigen Bilder landen in ./input_photos/output_expose/ (änderbar mit -o).
Originale werden nie verändert.

Pipeline (die Reihenfolge ist bewusst gewählt):
  1. Laden       EXIF-Ausrichtung anwenden, Farbprofil -> sRGB, Transparenz -> weiß
  2. Rauschen    Farbrauschen sanft glätten; Helligkeitsrauschen nur bei deutlich
                 verrauschten Bildern und nur teilweise (Risse/Flecken bleiben).
                 Läuft VOR der Geometrie, solange das Rauschen noch pixelgenau ist.
  3. Geometrie   Objektivverzeichnung (Plumb-Line-Schätzung), Horizont (Roll) und
                 stürzende Linien (Pitch) über den Fluchtpunkt der Senkrechten,
                 alles in EINEM Resampling-Schritt. Zuschnitt nur so weit, dass
                 keine leeren Ränder entstehen; Seitenverhältnis bleibt erhalten.
  4. Ton/Farbe   Weißabgleich (auf neutralen Flächen, mischlicht-schonend),
                 Belichtung, Schatten aufhellen / Lichter absenken (kantenerhaltend,
                 moderat, ohne Farbkanal-Ausbrennen), Schwarz- und Weißpunkt, sanfte
                 S-Kurve, Dynamik (Vibrance) statt Sättigung.
  5. Schärfe     leichte Ausgabeschärfung, nur Helligkeit, mit Rauschschwelle.
  6. Speichern   JPEG (Qualität 92, 4:4:4), EXIF/XMP/Farbprofil übernommen.

Grundsatz: nur klassische fotografische Korrekturen. Es werden keine Bildinhalte
erzeugt, entfernt, retuschiert oder verschoben. Jede Korrektur, deren
automatische Schätzung unsicher ist, wird übersprungen statt geraten.
"""

from __future__ import annotations

import argparse
import io
import json
import logging
import math
import os
import re
import sys
import tempfile
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from concurrent.futures.process import BrokenProcessPool
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageCms, ImageOps, UnidentifiedImageError
except ImportError as exc:  # pragma: no cover - reine Nutzerhilfe
    sys.stderr.write(
        f"Fehlende Bibliothek: {exc}\n"
        "Bitte zuerst installieren:  pip install -r requirements.txt\n"
    )
    sys.exit(2)

__version__ = "1.3.1"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
DEFAULT_OUTPUT_DIRNAME = "output_expose"
LOG_FILENAME = "verarbeitung.log"
COMPARE_DIRNAME = "_vergleich"
MANIFEST_NAME = ".expose_manifest.json"
OUTPUT_MARKER = b"process_real_estate_photos"          # JPEG-Kommentar: "diese Datei stammt von uns"
MAX_MEGAPIXELS = 120                                   # größere Bilder sprengen den Arbeitsspeicher
NAS_SYSTEM_DIRS = {"@eaDir", "#recycle", "#snapshot", "@Recycle", "@Recently-Snapshot",
                   "@__thumb", "@tmp", "#Recycle"}

# Schutz vor Dekompressionsbomben, aber groß genug für Panoramen.
Image.MAX_IMAGE_PIXELS = 250_000_000

LUMA_REC709 = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

log = logging.getLogger("expose")

_UMASK = os.umask(0)
os.umask(_UMASK)


class SkipImage(Exception):
    """Datei ist kein geeignetes Foto (zu klein, falsches Format …)."""


# --------------------------------------------------------------------------- #
# Einstellungen
# --------------------------------------------------------------------------- #

@dataclass
class Settings:
    # Ausgabe
    jpeg_quality: int = 92
    max_long_edge: Optional[int] = None      # optional verkleinern, nie vergrößern
    min_size: int = 320                      # kürzere Kante darunter = "nicht geeignet"
    strip_gps: bool = False
    compare: bool = False

    # Rauschen
    denoise: bool = True
    denoise_strength: float = 1.0

    # Geometrie
    lens: bool = True
    lens_k: Optional[float] = None           # manueller Verzeichnungskoeffizient
    perspective: bool = True
    vertical_strength: float = 1.0           # 1.0 = Senkrechten ganz gerade
    focal35: Optional[float] = None          # KB-Brennweite; None = EXIF oder 24 mm
    max_roll_deg: float = 8.0
    max_pitch_deg: float = 25.0
    max_side_loss: float = 0.10              # max. Beschnitt je Bildseite (ungünstigste Stelle)
    max_side_loss_explicit: bool = False     # per --max-crop gesetzt -> gilt auch fürs Drehen
    min_keep_area: float = 0.72              # min. erhaltener Bildinhalt

    # Ton & Farbe (gleiche Zielwerte für alle Bilder = einheitlicher Look)
    wb_strength: float = 0.8                 # 0 = aus, 1 = voll neutralisieren
    wb_max_ratio: float = 1.25               # max. Verhältnis der Kanal-Faktoren
    warmth: float = 0.015                    # leicht warm = freundlich
    target_key_ev: float = -2.25             # Ziel-Mittelhelligkeit (log2, linear)
    max_ev_up: float = 1.3
    max_ev_up_clean: float = 1.8             # bei rauscharmen Bildern darf mehr aufgehellt werden
    max_ev_down: float = 0.5
    shadow_compress: float = 0.72            # <1 hellt Schatten auf
    highlight_compress: float = 0.85         # <1 senkt Lichter
    max_shadow_lift_ev: float = 1.0
    max_highlight_cut_ev: float = 0.8
    highlight_knee_ev: float = 1.5           # Lichter erst ab hier absenken
    contrast: float = 0.20
    vibrance: float = 0.15
    sharpen: float = 1.0


# --------------------------------------------------------------------------- #
# Allgemeine Helfer
# --------------------------------------------------------------------------- #

def smoothstep(e0: float, e1: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def resize_long_edge(img: np.ndarray, long_edge: int, interp=cv2.INTER_AREA):
    h, w = img.shape[:2]
    s = long_edge / max(h, w)
    if s >= 1.0:
        return img, 1.0
    size = (max(1, int(round(w * s))), max(1, int(round(h * s))))
    return cv2.resize(img, size, interpolation=interp), s


def to_u8(img: np.ndarray) -> np.ndarray:
    return np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)


def srgb_to_linear(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0).astype(np.float32)
    hi = cv2.pow((x + 0.055) / 1.055, 2.4)
    return np.where(x <= 0.04045, x / 12.92, hi).astype(np.float32)


def linear_to_srgb(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0).astype(np.float32)
    hi = 1.055 * cv2.pow(x, 1.0 / 2.4) - 0.055
    return np.where(x <= 0.0031308, x * 12.92, hi).astype(np.float32)


def luminance(lin_rgb: np.ndarray) -> np.ndarray:
    return cv2.transform(lin_rgb, LUMA_REC709.reshape(1, 3))


# --------------------------------------------------------------------------- #
# 1. Laden
# --------------------------------------------------------------------------- #

@dataclass
class LoadedImage:
    rgb: np.ndarray                  # float32, HxWx3, sRGB-kodiert, 0..1
    is_gray: bool
    high_bit_depth: bool
    exif: Optional[Image.Exif]
    xmp: Optional[bytes]
    icc_out: Optional[bytes]
    dpi: Optional[tuple]
    focal35: Optional[float]
    notes: list = field(default_factory=list)


_ORIENTATION_OPS = {
    2: lambda a: a[:, ::-1],
    3: lambda a: a[::-1, ::-1],
    4: lambda a: a[::-1, :],
    5: lambda a: np.swapaxes(a, 0, 1),
    6: lambda a: np.rot90(a, -1),
    7: lambda a: np.rot90(np.swapaxes(a, 0, 1), 2),
    8: lambda a: np.rot90(a, 1),
}


def apply_orientation(arr: np.ndarray, orientation: int) -> np.ndarray:
    """EXIF-Orientation (1-8) auf ein numpy-Bild anwenden (wie ImageOps.exif_transpose)."""
    op = _ORIENTATION_OPS.get(int(orientation or 1))
    return np.ascontiguousarray(op(arr)) if op else arr


def _png_bit_depth(path: Path) -> int:
    with open(path, "rb") as fh:
        head = fh.read(26)
    if len(head) >= 26 and head[:8] == b"\x89PNG\r\n\x1a\n" and head[12:16] == b"IHDR":
        return head[24]
    return 8


def _load_png16(path: Path) -> tuple[np.ndarray, bool]:
    data = np.fromfile(str(path), dtype=np.uint8)
    arr = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if arr is None:
        raise ValueError("16-Bit-PNG konnte nicht dekodiert werden")
    scale = 65535.0 if arr.dtype == np.uint16 else 255.0
    arr = arr.astype(np.float32) / scale
    if arr.ndim == 2:
        return np.dstack([arr, arr, arr]), True
    if arr.shape[2] == 4:
        alpha = arr[:, :, 3:4]
        arr = arr[:, :, :3] * alpha + (1.0 - alpha)       # auf Weiß
    elif arr.shape[2] == 2:
        alpha = arr[:, :, 1:2]
        g = arr[:, :, 0:1] * alpha + (1.0 - alpha)
        return np.dstack([g, g, g]), True
    return cv2.cvtColor(arr[:, :, :3], cv2.COLOR_BGR2RGB), False


def _flatten_to_rgb(im: Image.Image) -> tuple[Image.Image, bool]:
    """Beliebigen Pillow-Modus nach RGB/L bringen, Transparenz auf Weiß legen."""
    gray_modes = {"1", "L", "LA", "I", "I;16", "I;16B", "I;16L", "F"}
    is_gray = im.mode in gray_modes
    if im.mode == "P":
        im = im.convert("RGBA" if "transparency" in im.info else "RGB")
    if im.mode in ("I", "I;16", "I;16B", "I;16L", "F"):
        arr = np.asarray(im, dtype=np.float32)
        peak = 65535.0 if arr.max() > 255 else 255.0
        im = Image.fromarray(np.clip(arr / peak * 255.0 + 0.5, 0, 255).astype(np.uint8), "L")
    if im.mode in ("RGBA", "LA", "PA", "RGBa", "La"):
        rgba = im.convert("RGBA")
        white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        im = Image.alpha_composite(white, rgba)
    if im.mode == "CMYK":
        im = im.convert("RGB")
    if im.mode != "RGB":
        im = im.convert("RGB")
    return im, is_gray


def _icc_description(profile) -> str:
    try:
        return (ImageCms.getProfileDescription(profile) or "").strip()
    except Exception:
        return ""


def _srgb_profile_bytes() -> Optional[bytes]:
    try:
        return ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    except Exception:
        return None


def _convert_to_srgb(im: Image.Image, icc: Optional[bytes], notes: list):
    """Bild mit eingebettetem Profil (z. B. Display P3, Adobe RGB, CMYK) nach sRGB."""
    srgb_bytes = _srgb_profile_bytes()
    if not icc:
        return im, srgb_bytes
    try:
        src = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        desc = _icc_description(src)
        if "srgb" in desc.lower() and im.mode == "RGB":
            return im, icc
        intent = getattr(getattr(ImageCms, "Intent", None), "RELATIVE_COLORIMETRIC", 1)
        converted = ImageCms.profileToProfile(
            im, src, ImageCms.createProfile("sRGB"),
            renderingIntent=intent, outputMode="RGB",
        )
        notes.append(f"Farbprofil '{desc or 'unbekannt'}' nach sRGB konvertiert")
        return converted, srgb_bytes
    except Exception as exc:
        notes.append(f"Farbprofil nicht konvertierbar ({exc}); Originalprofil bleibt eingebettet")
        return im, icc


def _xmp_reset_orientation(xmp) -> Optional[bytes]:
    if not xmp:
        return None
    if isinstance(xmp, str):
        xmp = xmp.encode("utf-8")
    xmp = re.sub(rb'(tiff:Orientation\s*=\s*["\'])\d(["\'])', rb"\g<1>1\g<2>", xmp)
    xmp = re.sub(rb"(<tiff:Orientation>)\s*\d\s*(</tiff:Orientation>)", rb"\g<1>1\g<2>", xmp)
    return xmp


def _xmp_strip_gps(xmp: Optional[bytes]) -> Optional[bytes]:
    """GPS-Angaben auch aus XMP entfernen (Lightroom/Photoshop schreiben sie dort doppelt)."""
    if not xmp:
        return xmp
    xmp = re.sub(rb'\s+exif:GPS\w+\s*=\s*"[^"]*"', b"", xmp)
    xmp = re.sub(rb"\s+exif:GPS\w+\s*=\s*'[^']*'", b"", xmp)
    xmp = re.sub(rb"<exif:GPS(\w+)\b[^>]*>.*?</exif:GPS\1>", b"", xmp, flags=re.S)
    return re.sub(rb"<exif:GPS\w+\b[^>]*/>", b"", xmp)


def _looks_gray(rgb: np.ndarray) -> bool:
    small, _ = resize_long_edge(rgb, 256)
    return float(np.abs(small - small.mean(axis=2, keepdims=True)).max()) < 2.0 / 255.0


def load_image(path: Path, settings: Settings) -> LoadedImage:
    notes: list = []
    with Image.open(path) as im:
        fmt = im.format
        if fmt not in ("JPEG", "MPO", "PNG"):
            raise SkipImage(f"Dateiinhalt ist {fmt or 'unbekannt'}, kein JPEG/PNG")
        if OUTPUT_MARKER in (im.info.get("comment") or b""):
            raise SkipImage("ist bereits ein Ergebnis dieses Skripts (würde doppelt bearbeitet)")
        megapixels = im.width * im.height / 1e6
        if megapixels > MAX_MEGAPIXELS:
            raise SkipImage(f"Bild ist zu groß ({megapixels:.0f} Megapixel, maximal {MAX_MEGAPIXELS})")
        if getattr(im, "n_frames", 1) > 1:
            im.seek(0)
            if fmt == "PNG":
                notes.append("animiertes PNG: nur das erste Bild wird verarbeitet")

        exif = im.getexif()
        try:  # Unter-IFDs laden, solange die Datei offen ist
            exif.get_ifd(0x8769)
            exif.get_ifd(0x8825)
        except Exception:
            pass
        orientation = int(exif.get(0x0112, 1) or 1)
        if orientation not in range(1, 9):
            orientation = 1
        icc = im.info.get("icc_profile")
        xmp = im.info.get("xmp")
        dpi = im.info.get("dpi")

        focal35 = None
        try:
            f35 = exif.get_ifd(0x8769).get(0xA405)
            if f35 and float(f35) > 5:
                focal35 = float(f35)
        except Exception:
            pass

        high_bit = fmt == "PNG" and _png_bit_depth(path) == 16
        if high_bit and icc and im.mode in ("RGB", "RGBA"):
            try:
                desc = _icc_description(ImageCms.ImageCmsProfile(io.BytesIO(icc))).lower()
            except Exception:
                desc = ""
            if "srgb" not in desc:
                # Farbraumumrechnung (z. B. Adobe RGB -> sRGB) ist wichtiger als 16 Bit
                high_bit = False
        if high_bit:
            rgb, is_gray = _load_png16(path)
            rgb = apply_orientation(rgb, orientation)
            icc_out = icc
            if icc:
                notes.append("16-Bit-PNG: eingebettetes Farbprofil wird unverändert übernommen")
        else:
            im.load()
            if im.mode == "CMYK" and icc:
                im, icc_out = _convert_to_srgb(im, icc, notes)
                icc = None
            im = ImageOps.exif_transpose(im)
            im, is_gray = _flatten_to_rgb(im)
            if icc:
                im, icc_out = _convert_to_srgb(im, icc, notes)
            else:
                icc_out = _srgb_profile_bytes()
            rgb = np.asarray(im, dtype=np.float32) / 255.0

    h, w = rgb.shape[:2]
    if min(h, w) < settings.min_size:
        raise SkipImage(f"zu klein ({w}×{h} px, Minimum {settings.min_size} px)")
    if not is_gray and _looks_gray(rgb):
        is_gray = True
    if orientation != 1:
        notes.append(f"EXIF-Ausrichtung {orientation} angewendet")

    out_exif = exif if len(exif) else None
    if out_exif is not None:
        out_exif[0x0112] = 1
        if settings.strip_gps and 0x8825 in out_exif:
            del out_exif[0x8825]

    return LoadedImage(
        rgb=np.ascontiguousarray(rgb, dtype=np.float32),
        is_gray=is_gray,
        high_bit_depth=high_bit,
        exif=out_exif,
        xmp=_xmp_strip_gps(_xmp_reset_orientation(xmp)) if settings.strip_gps else _xmp_reset_orientation(xmp),
        icc_out=None if is_gray else icc_out,
        dpi=dpi,
        focal35=focal35,
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# 2. Rauschreduzierung
# --------------------------------------------------------------------------- #

def estimate_noise_sigma(gray_u8: np.ndarray) -> float:
    """Rauschen (8-Bit-Einheiten) nach Immerkær, nur auf strukturarmen Flächen
    gemessen, damit Kanten und Texturen nicht als Rauschen zählen."""
    g = gray_u8.astype(np.float32)
    kernel = np.array([[1, -2, 1], [-2, 4, -2], [1, -2, 1]], np.float32)
    resp = cv2.filter2D(g, -1, kernel, borderType=cv2.BORDER_REFLECT)
    mag = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
    # ausgebrannte/abgesoffene Flächen haben kein Rauschen und würden den Wert verfälschen
    valid = cv2.erode(((gray_u8 > 5) & (gray_u8 < 247)).astype(np.uint8), np.ones((3, 3), np.uint8)) > 0
    if valid.mean() < 0.05:
        valid = np.ones_like(valid)
    flat = valid & (mag <= np.percentile(mag[valid], 50))
    return float(math.sqrt(math.pi / 2) * np.abs(resp[flat]).mean() / 6.0)


def denoise_image(img: np.ndarray, high_bit: bool, s: Settings):
    """Rauschen mildern, ohne Schäden zu verstecken.

    Farbrauschen (Chroma) wird sanft geglättet - das verändert keine Strukturen.
    Helligkeitsrauschen wird nur bei deutlich verrauschten Bildern und nur
    teilweise reduziert: Volles Non-Local-Means würde feine Risse, Fugen und
    kleine Flecken mit wegglätten."""
    # Das Rauschen wird immer gemessen (es steuert auch, wie stark aufgehellt werden darf).
    sigma = estimate_noise_sigma(cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2GRAY))
    info = {"sigma": round(sigma, 2), "applied": ""}
    if not s.denoise or s.denoise_strength <= 0:
        info["applied"] = "abgeschaltet"
        return img, info
    if sigma < 0.6:
        return img, info
    strength = float(s.denoise_strength)
    ycc = cv2.cvtColor(np.ascontiguousarray(img, dtype=np.float32), cv2.COLOR_RGB2YCrCb)
    for c in (1, 2):
        ycc[:, :, c] = cv2.GaussianBlur(ycc[:, :, c], (0, 0), 1.5 * strength)
    info["applied"] = "Farbrauschen geglättet"
    if sigma > 2.0:
        y = ycc[:, :, 0].copy()
        if high_bit:  # 16-Bit-Daten nicht auf 8 Bit quantisieren
            ny = cv2.bilateralFilter(y, d=5, sigmaColor=2.0 * sigma / 255.0, sigmaSpace=2.0)
        else:
            search = 21 if y.size <= 6_000_000 else 15
            h = float(np.clip(0.85 * sigma * strength, 1.0, 6.0))
            ny = cv2.fastNlMeansDenoising(to_u8(y), None, h, 7, search).astype(np.float32) / 255.0
        ycc[:, :, 0] = y + min(0.4 * strength, 1.0) * (ny - y)
        info["applied"] += ", Helligkeitsrauschen teilweise reduziert"
    return np.clip(cv2.cvtColor(ycc, cv2.COLOR_YCrCb2RGB), 0, 1).astype(np.float32), info


# --------------------------------------------------------------------------- #
# 3. Geometrie
#
# Koordinaten: "normiert" = (Pixel - Bildmitte) / halbe Bilddiagonale.
# Objektiv: Divisionsmodell  p_u = p_d / (1 + k·|p_d|²)   (k < 0 = tonnenförmig)
# Perspektive: Homographie H = K·R·K⁻¹ (virtuelle Drehung der Kamera), die den
# Fluchtpunkt der Senkrechten ins Unendliche legt -> Senkrechten werden parallel
# und lotrecht, der Horizont waagrecht.
# --------------------------------------------------------------------------- #

def _norm_params(w: int, h: int):
    return (w - 1) / 2.0, (h - 1) / 2.0, 0.5 * math.hypot(w, h)


def undistort_points(pn: np.ndarray, k: float) -> np.ndarray:
    if k == 0:
        return pn
    r2 = (pn ** 2).sum(axis=-1, keepdims=True)
    return pn / (1.0 + k * r2)


def distort_points(ux: np.ndarray, uy: np.ndarray, k: float):
    """Inverse des Divisionsmodells (geschlossen). Gibt (dx, dy, gültig) zurück."""
    if k == 0:
        return ux, uy, np.ones(ux.shape, dtype=bool)
    r2 = ux * ux + uy * uy
    disc = 1.0 - 4.0 * k * r2
    valid = disc >= 0
    s = 2.0 / (1.0 + np.sqrt(np.maximum(disc, 0.0)))
    return ux * s, uy * s, valid


def _split_at_corners(pts: np.ndarray, step: int = 6, max_turn_deg: float = 30.0):
    n = len(pts)
    if n < 3 * step:
        return [pts]
    d = pts[step:] - pts[:-step]
    ang = np.arctan2(d[:, 1], d[:, 0])
    turn = np.abs(np.angle(np.exp(1j * (ang[step:] - ang[:-step]))))
    corner = np.zeros(n, dtype=bool)
    corner[step:n - step] = turn > np.deg2rad(max_turn_deg)
    pieces, start = [], None
    for i, c in enumerate(corner):
        if not c and start is None:
            start = i
        elif c and start is not None:
            pieces.append(pts[start:i])
            start = None
    if start is not None:
        pieces.append(pts[start:])
    return pieces


def _edge_chains(gray: np.ndarray, min_len: float):
    blur = cv2.GaussianBlur(gray, (0, 0), 1.0)
    gx = cv2.Sobel(blur, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(blur, cv2.CV_32F, 0, 1, ksize=3)
    hi = max(30.0, float(np.percentile(cv2.magnitude(gx, gy), 90)))
    edges = cv2.Canny(blur, 0.4 * hi, hi, L2gradient=True)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    chains = []
    for cnt in contours:
        if len(cnt) < min_len:
            continue
        for piece in _split_at_corners(cnt[:, 0, :].astype(np.float64)):
            if len(piece) < min_len:
                continue
            seg_len = float(np.linalg.norm(piece[-1] - piece[0]))
            if seg_len >= min_len:
                chains.append(piece)
    return chains


def _chain_line_rms(pts: np.ndarray, ids: np.ndarray, counts: np.ndarray) -> np.ndarray:
    n = len(counts)
    x, y = pts[:, 0], pts[:, 1]
    mx = np.bincount(ids, x, n) / counts
    my = np.bincount(ids, y, n) / counts
    cxx = np.bincount(ids, x * x, n) / counts - mx * mx
    cyy = np.bincount(ids, y * y, n) / counts - my * my
    cxy = np.bincount(ids, x * y, n) / counts - mx * my
    lam = 0.5 * (cxx + cyy) - np.sqrt((0.5 * (cxx - cyy)) ** 2 + cxy ** 2)
    return np.sqrt(np.maximum(lam, 0.0))


def estimate_lens_distortion(gray_small: np.ndarray):
    """Blinde Plumb-Line-Schätzung eines radialen Koeffizienten.

    Gerade Kanten (Türzargen, Fensterrahmen, Raumecken) müssen nach der Korrektur
    gerade sein. Gesucht wird das k, das möglichst viele lange Kanten begradigt.
    Nur bei deutlicher, konsistenter Verbesserung wird korrigiert - Smartphones
    korrigieren die Verzeichnung meist schon selbst.
    """
    h, w = gray_small.shape
    cx, cy, R = _norm_params(w, h)
    chains = _edge_chains(gray_small, min_len=0.06 * max(w, h))
    info = {"k": 0.0, "chains": len(chains), "reason": ""}
    if len(chains) < 8:
        info["reason"] = "zu wenige lange Kanten"
        return 0.0, info

    pts_list, ids_list, lengths = [], [], []
    for i, ch in enumerate(chains):
        if len(ch) > 80:
            ch = ch[np.linspace(0, len(ch) - 1, 80).astype(int)]
        pn = (ch - (cx, cy)) / R
        pts_list.append(pn)
        ids_list.append(np.full(len(pn), i))
        lengths.append(np.linalg.norm(pn[-1] - pn[0]))
    P = np.concatenate(pts_list)
    ids = np.concatenate(ids_list)
    counts = np.bincount(ids).astype(np.float64)
    lengths = np.asarray(lengths)

    ks = np.round(np.arange(-0.20, 0.2001, 0.005), 4)
    r2 = (P ** 2).sum(axis=1, keepdims=True)
    rms = np.stack([_chain_line_rms(P / (1.0 + k * r2), ids, counts) * R for k in ks])
    i0 = int(np.argmin(np.abs(ks)))

    keep = (rms.min(axis=0) <= 1.0) & (rms[i0] <= 8.0)
    # Kanten nahe der Bildmitte tragen kaum Information über k
    mid_r = np.array([np.sqrt((p ** 2).sum(axis=1)).mean() for p in pts_list])
    informative = keep & (mid_r > 0.35)
    if informative.sum() < 6:
        info["reason"] = "zu wenige gerade Randkanten"
        return 0.0, info

    tau = 1.5
    wts = lengths[keep]
    cost = (np.minimum(rms[:, keep], tau) ** 2 * wts).sum(axis=1) / wts.sum()
    ib = int(np.argmin(cost))
    k_best = float(ks[ib])
    if 0 < ib < len(ks) - 1:  # parabolische Verfeinerung
        c0, c1, c2 = cost[ib - 1], cost[ib], cost[ib + 1]
        den = c0 - 2 * c1 + c2
        if den > 1e-12:
            k_best += float(0.5 * (c0 - c2) / den * (ks[1] - ks[0]))
    gain = float(cost[i0] / max(cost[ib], 1e-9))
    info.update(k_raw=round(k_best, 4), gain=round(gain, 2), used=int(keep.sum()))

    if ib in (0, len(ks) - 1):
        info["reason"] = "Schätzung am Suchrand (unplausibel)"
        return 0.0, info
    if abs(k_best) < 0.02:
        info["reason"] = "Verzeichnung vernachlässigbar"
        return 0.0, info
    if k_best > 0:
        # Weitwinkel verzeichnen tonnenförmig; "kissenförmig" ist bei Immobilien-
        # fotos fast immer eine Fehlschätzung (z. B. durch Dachschrägen).
        info["reason"] = "kissenförmige Schätzung, für Weitwinkel unplausibel"
        return 0.0, info
    if gain < 1.10:
        info["reason"] = "Verbesserung nicht eindeutig"
        return 0.0, info
    info["k"] = round(k_best, 4)
    return k_best, info


def _remap_normalized(img: np.ndarray, k: float, H: np.ndarray,
                      rect: tuple, out_size: tuple, interp=cv2.INTER_LANCZOS4):
    """Ausgabebild aus dem Quellbild berechnen (ein einziges Resampling).

    rect = (x0, y0, w, h) in normierten Leinwand-Koordinaten."""
    src_h, src_w = img.shape[:2]
    cx, cy, R = _norm_params(src_w, src_h)
    out_w, out_h = out_size
    x0, y0, rw, rh = rect
    Hinv = np.linalg.inv(H)
    xs = (x0 + (np.arange(out_w) + 0.5) / out_w * rw).astype(np.float64)
    map_x = np.empty((out_h, out_w), np.float32)
    map_y = np.empty((out_h, out_w), np.float32)
    for r0 in range(0, out_h, 256):
        r1 = min(out_h, r0 + 256)
        ys = y0 + (np.arange(r0, r1) + 0.5) / out_h * rh
        qx, qy = np.meshgrid(xs, ys)
        X = Hinv[0, 0] * qx + Hinv[0, 1] * qy + Hinv[0, 2]
        Y = Hinv[1, 0] * qx + Hinv[1, 1] * qy + Hinv[1, 2]
        Z = Hinv[2, 0] * qx + Hinv[2, 1] * qy + Hinv[2, 2]
        dx, dy, _ = distort_points(X / Z, Y / Z, k)
        map_x[r0:r1] = dx * R + cx
        map_y[r0:r1] = dy * R + cy
    out = cv2.remap(img, map_x, map_y, interpolation=interp, borderMode=cv2.BORDER_REPLICATE)
    return out


def _find_segments(gray: np.ndarray, min_len: float) -> np.ndarray:
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    lines = lsd.detect(gray)[0]
    if lines is None:
        return np.zeros((0, 4), np.float64)
    seg = lines.reshape(-1, 4).astype(np.float64)
    length = np.hypot(seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1])
    return seg[length >= min_len]


def _rotation_from_up(u: np.ndarray, pitch_factor: float = 1.0):
    """Drehung, die die Welt-Senkrechte u (Kamerakoordinaten) lotrecht stellt."""
    u = u / np.linalg.norm(u)
    if u[1] > 0:
        u = -u
    beta = math.atan2(u[0], -u[1])             # Roll
    rho = math.hypot(u[0], u[1])
    gamma = math.atan2(u[2], rho)              # Pitch
    return beta, gamma


def rotation_matrix(roll: float, pitch: float) -> np.ndarray:
    a = -roll
    Rz = np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])
    g = pitch
    Rx = np.array([[1, 0, 0], [0, math.cos(g), -math.sin(g)], [0, math.sin(g), math.cos(g)]])
    return Rx @ Rz


def estimate_verticals(gray_u: np.ndarray, f_n: float, s: Settings):
    """Fluchtpunkt der Senkrechten per RANSAC -> Roll (Horizont) und Pitch (stürzende Linien)."""
    h, w = gray_u.shape
    cx, cy, R = _norm_params(w, h)
    info = {"ok": False, "roll": 0.0, "pitch": 0.0, "lines": 0, "mode": "", "reason": ""}
    seg = _find_segments(gray_u, min_len=0.04 * max(w, h))
    if len(seg) == 0:
        info["reason"] = "keine Linien gefunden"
        return info

    p1 = (seg[:, 0:2] - (cx, cy)) / R
    p2 = (seg[:, 2:4] - (cx, cy)) / R
    d = p2 - p1
    length = np.hypot(d[:, 0], d[:, 1])
    d = d / length[:, None]
    tilt = np.degrees(np.arctan2(np.abs(d[:, 0]), np.abs(d[:, 1])))   # 0° = senkrecht

    vert = tilt <= 25.0
    p1v, p2v, dv, lv = p1[vert], p2[vert], d[vert], length[vert]
    midv = 0.5 * (p1v + p2v)

    def angles(v):
        r, p = _rotation_from_up(np.array([v[0] / f_n, v[1] / f_n, v[2]]))
        return math.degrees(r), math.degrees(p)

    def evaluate(res):
        """Roll/Pitch aus einem RANSAC-Ergebnis ableiten; None + Grund, wenn unbrauchbar."""
        v, inl, spread = res
        info["lines"] = int(inl.sum())
        wts = lv[inl]
        if inl.sum() < 4 or float(wts.sum()) < 0.5:
            return None, "zu wenige verlässliche senkrechte Linien", False
        mean_x = float((midv[inl, 0] * wts).sum() / wts.sum())
        if spread >= 0.12:
            roll_d, pitch_d = angles(v)
            mode = "Fluchtpunkt"
            delta = _vp_instability(p1v, p2v, lv, midv, inl, angles, (roll_d, pitch_d))
            if delta > 2.5:
                return None, f"Fluchtpunkt instabil (hängt an einzelnen Linien, Abweichung {delta:.1f}°)", True
            pitch_gate = pitch_d
            if abs(pitch_d) > s.max_pitch_deg:
                # Der Roll-Winkel hängt nicht von der angenommenen Brennweite ab.
                pitch_d, mode = 0.0, "Fluchtpunkt, Neigung zu groß – nur Horizont"
        elif abs(mean_x) <= 0.05:
            # Linien nur in der Bildmitte: dort ist die Neigung der Senkrechten
            # reine Verkippung (Roll), keine Perspektive.
            dd = dv[inl] * np.sign(dv[inl][:, 1:2] + 1e-12)
            mean = (dd * wts[:, None]).sum(axis=0)
            roll_r, _ = _rotation_from_up(np.array([mean[0], mean[1], 0.0]))
            roll_d, pitch_d, mode = math.degrees(roll_r), 0.0, "nur Horizont (Linien zu einseitig)"
            pitch_gate = 0.0
        else:
            # Linien nur am Bildrand: ihre Schräge kann Perspektive statt
            # Verkippung sein -> keine Drehung daraus ableiten.
            return None, "Senkrechten nur am Bildrand", False
        if abs(roll_d) > s.max_roll_deg:
            return None, f"Roll {roll_d:.1f}° unplausibel groß", True
        # Gegenprobe mit ALLEN fast senkrechten Linien: Eine echte Korrektur macht
        # sie insgesamt deutlich gerader. Schräge Dachkanten o. Ä. können einen
        # Schein-Fluchtpunkt liefern - dann würden andere Senkrechten schiefer.
        # (geprüft wird der gemessene Fluchtpunkt, auch wenn nur der Horizont korrigiert wird)
        before, after = _verticality(p1v, p2v, lv, f_n, roll_d, pitch_gate)
        if after > 0.85 * before:
            return None, (f"Korrektur würde die Senkrechten nicht verbessern "
                          f"(mittlere Schräge {before:.1f}° -> {after:.1f}°)"), True
        return {"roll": roll_d, "pitch": pitch_d, "mode": mode}, "", False

    candidates = []
    res1 = _vp_ransac(p1v, p2v, dv, lv) if len(lv) >= 3 else None
    if res1 is not None:
        # Zweiter Durchgang: Konvergierende Sparren einer Dachschräge können mehr
        # Linien sammeln als die echten Senkrechten. Ergibt der Sieger eine
        # unplausible Neigung, wird unter den übrigen Linien weitergesucht - der
        # neue Kandidat muss aber selbst tragfähig sein, sonst bleibt es beim
        # ersten (dann nur Horizont).
        if abs(angles(res1[0])[1]) > s.max_pitch_deg and (~res1[1]).sum() >= 3:
            rest = ~res1[1]
            res2 = _vp_ransac(p1v[rest], p2v[rest], dv[rest], lv[rest])
            if res2 is not None:
                full = np.zeros(len(lv), dtype=bool)
                full[np.nonzero(rest)[0][res2[1]]] = True
                if (abs(angles(res2[0])[1]) <= s.max_pitch_deg and full.sum() >= 4
                        and lv[full].sum() >= 0.5 and res2[2] >= 0.12):
                    candidates.append((res2[0], full, res2[2]))
        candidates.append(res1)
    hard = False
    for res in candidates:
        result, reason, rejected = evaluate(res)
        if result is not None:
            info.update(ok=True, **result)
            return info
        info["reason"] = info["reason"] or reason
        hard = hard or rejected
    if hard:
        # Ein Fluchtpunkt wurde gefunden, aber als unplausibel verworfen: dann auch
        # nicht über waagrechte Linien drehen (die sind dann meist ebenso trügerisch).
        return info

    # Rückfall: lange, fast waagrechte Linien nahe der Bildmitte (Horizont)
    horiz = (tilt >= 84.0) & (length >= 0.25) & (np.abs((p1[:, 1] + p2[:, 1]) / 2) <= 0.25)
    if horiz.sum() >= 3 and length[horiz].sum() >= 1.0:
        dh = d[horiz] * np.sign(d[horiz][:, 0:1] + 1e-12)
        ang = np.degrees(np.arctan2(dh[:, 1], dh[:, 0]))
        wts = length[horiz]
        order = np.argsort(ang)
        cum = np.cumsum(wts[order])
        med = float(ang[order][np.searchsorted(cum, cum[-1] / 2)])
        mad = float(np.median(np.abs(ang - med)))
        if mad <= 0.6 and 0.2 <= abs(med) <= 4.0:
            a = math.radians(med)
            u = np.array([-math.sin(a), math.cos(a), 0.0])
            roll, _ = _rotation_from_up(u)
            info.update(ok=True, roll=math.degrees(roll), pitch=0.0,
                        lines=int(horiz.sum()), mode="Horizont (waagrechte Linien)")
            return info
    info["reason"] = info["reason"] or "zu wenige verlässliche senkrechte Linien"
    return info


def _verticality(p1, p2, length, f_n, roll_deg, pitch_deg):
    """Mittlere Schräge (Grad, je Linie max. 10°, längengewichtet) fast senkrechter
    Linien vor und nach einer Korrektur um roll/pitch."""
    K = np.diag([f_n, f_n, 1.0])
    H = K @ rotation_matrix(math.radians(roll_deg), math.radians(pitch_deg)) @ np.linalg.inv(K)

    def mapped(p):
        q = (H @ np.hstack([p, np.ones((len(p), 1))]).T).T
        return q[:, :2] / q[:, 2:3]

    def mean_tilt(a, b):
        d = b - a
        d = d * np.sign(d[:, 1:2] + 1e-12)
        t = np.abs(np.degrees(np.arctan2(d[:, 0], d[:, 1])))
        return float((np.minimum(t, 10.0) * length).sum() / max(length.sum(), 1e-9))

    return mean_tilt(p1, p2), mean_tilt(mapped(p1), mapped(p2))


def _homog_lines(p1, p2):
    ones = np.ones((len(p1), 1))
    lines = np.cross(np.hstack([p1, ones]), np.hstack([p2, ones]))
    return lines / np.hypot(lines[:, 0], lines[:, 1])[:, None]


def _vp_instability(p1, p2, length, mid, inl, angles, base) -> float:
    """Leave-one-cluster-out: Wie stark ändern sich Roll/Pitch, wenn man die
    Linien an einer x-Position (z. B. eine einzelne Dachkante) weglässt?"""
    lines = _homog_lines(p1, p2)
    worst = 0.0
    for offset in (0.0, 0.015):   # zwei Rasterlagen: Ergebnis darf nicht an der Einteilung hängen
        worst = max(worst, _vp_instability_bins(lines, length, mid, inl, angles, base,
                                                np.floor((mid[:, 0] + offset) / 0.03).astype(int)))
    return worst


def _vp_instability_bins(lines, length, mid, inl, angles, base, cl) -> float:
    worst = 0.0
    for c in np.unique(cl[inl]):
        sub = inl & (cl != c)
        if sub.sum() < 2:
            continue
        L = lines[sub] * length[sub][:, None]
        v = np.linalg.svd(L.T @ L)[2][-1]
        r, p = angles(v)
        w = length[sub]
        mx = (mid[sub, 0] * w).sum() / w.sum()
        spread = math.sqrt(((mid[sub, 0] - mx) ** 2 * w).sum() / w.sum())
        # Bleiben nur Linien an einer Stelle übrig, ist die Neigung dort nicht
        # bestimmbar - dann nur die Drehung vergleichen.
        dev = abs(r - base[0]) if spread < 0.08 else max(abs(r - base[0]), abs(p - base[1]))
        worst = max(worst, dev)
    return worst


def _vp_ransac(p1, p2, d, length, thr_deg: float = 1.2, iters: int = 600):
    n = len(p1)
    lines = _homog_lines(p1, p2)
    mid = 0.5 * (p1 + p2)
    thr = math.sin(math.radians(thr_deg))

    def residual(v):
        if abs(v[2]) < 1e-9:
            to_vp = np.broadcast_to(v[:2], mid.shape)
        else:
            to_vp = v[:2] / v[2] - mid
        nrm = np.hypot(to_vp[:, 0], to_vp[:, 1]) + 1e-12
        return np.abs(d[:, 0] * to_vp[:, 1] - d[:, 1] * to_vp[:, 0]) / nrm   # sin(Winkel)

    def plausible(v):
        if abs(v[2]) < 1e-9:
            dirv = v[:2]
        else:
            dirv = v[:2] / v[2]
            if np.hypot(*dirv) < 1.2:          # Fluchtpunkt im Bild: keine Senkrechten
                return False
        return abs(dirv[1]) / (np.hypot(*dirv) + 1e-12) >= math.cos(math.radians(30))

    rng = np.random.default_rng(20260924)
    prob = length / length.sum()
    cands = [np.array([0.0, 1.0, 0.0])]
    for _ in range(iters):
        i, j = rng.choice(n, size=2, replace=False, p=prob)
        v = np.cross(lines[i], lines[j])
        nv = np.linalg.norm(v)
        if nv > 1e-12:
            cands.append(v / nv)
    best, best_score = None, 0.0
    for v in cands:
        if not plausible(v):
            continue
        r = residual(v)
        inl = r < thr
        score = float((length[inl] * (1 - (r[inl] / thr) ** 2)).sum())
        if score > best_score:
            best, best_score = v, score
    if best is None:
        return None
    v = best
    for _ in range(3):  # Verfeinerung mit kleinsten Quadraten auf den Inliern
        inl = residual(v) < thr
        if inl.sum() < 2:
            return None
        L = lines[inl] * length[inl][:, None]
        _, _, vt = np.linalg.svd(L.T @ L)
        v_new = vt[-1]
        if not plausible(v_new):
            break
        v = v_new
    inl = residual(v) < thr
    if inl.sum() < 2:
        return None
    wts = length[inl]
    mx = (mid[inl, 0] * wts).sum() / wts.sum()
    spread = math.sqrt(((mid[inl, 0] - mx) ** 2 * wts).sum() / wts.sum())
    return v, inl, spread


def _best_content_rect(valid: np.ndarray, weight: np.ndarray, px: np.ndarray, py: np.ndarray,
                       aspect: float, src_w: int, src_h: int, max_side_loss: float):
    """Rechteck mit festem Seitenverhältnis, das möglichst viel ORIGINAL-Bildinhalt
    enthält (nicht bloß Leinwandfläche: entzerrte Bereiche sind gestreckt).

    Bevorzugt werden Lagen, bei denen an keiner Bildseite mehr als max_side_loss
    der Originalhöhe/-breite wegfällt - so bleiben Decke, Boden und Seiten erhalten."""
    h, w = valid.shape
    ii_bad = cv2.integral((~valid).astype(np.uint8))
    ii_w = cv2.integral(weight.astype(np.float32), sdepth=cv2.CV_64F)
    ys, xs = np.nonzero(valid)
    if len(xs) == 0:
        return None
    mcx, mcy = xs.mean(), ys.mean()

    def bounds(cx, cy, hw):
        hh = hw / aspect
        return (int(math.floor(cx - hw)), int(math.floor(cy - hh)),
                int(math.ceil(cx + hw)), int(math.ceil(cy + hh)))

    def box_sum(ii, x0, y0, x1, y1):
        return ii[y1, x1] - ii[y0, x1] - ii[y1, x0] + ii[y0, x0]

    def fits(cx, cy, hw):
        x0, y0, x1, y1 = bounds(cx, cy, hw)
        if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
            return False
        return box_sum(ii_bad, x0, y0, x1, y1) == 0

    def side_losses(x0, y0, x1, y1):
        # Größter Verlust entlang der GANZEN Kante (nicht nur in der Kantenmitte):
        # bei trapezförmiger Entzerrung fehlt an den Ecken am meisten.
        xa, xb = max(x0 + 1, 0), min(max(x1 - 1, x0 + 2), w)
        ya, yb = max(y0 + 1, 0), min(max(y1 - 1, y0 + 2), h)
        top = py[min(y0 + 1, h - 1), xa:xb].max() / (src_h - 1)
        bottom = 1.0 - py[max(y1 - 2, 0), xa:xb].min() / (src_h - 1)
        left = px[ya:yb, min(x0 + 1, w - 1)].max() / (src_w - 1)
        right = 1.0 - px[ya:yb, max(x1 - 2, 0)].min() / (src_w - 1)
        return tuple(max(0.0, float(v)) for v in (top, bottom, left, right))

    def pick(cands):
        # Bei (nahezu) gleichem Inhalt: gleichmäßigster Beschnitt, dann mittigste Lage.
        if not cands:
            return None
        top_content = max(c[0] for c in cands)
        near = [c for c in cands if c[0] >= (1 - 1e-3) * top_content]
        return min(near, key=lambda c: (round(max(c[4]), 3), math.hypot(c[1] - mcx, c[2] - mcy)))

    cands_all = []
    for fy in np.linspace(-0.3, 0.3, 15):
        for fx in np.linspace(-0.3, 0.3, 15):
            cx, cy = mcx + fx * w, mcy + fy * h
            if not (0 <= cx < w and 0 <= cy < h) or not valid[int(cy), int(cx)]:
                continue
            lo, hi = 0.0, float(w)
            for _ in range(22):
                mid = 0.5 * (lo + hi)
                if fits(cx, cy, mid):
                    lo = mid
                else:
                    hi = mid
            if lo < 2:
                continue
            hw = lo - 1.5 * max(1.0, aspect)   # Sicherheitsabstand (Rasterquantisierung), beide Achsen
            b = bounds(cx, cy, hw)
            content = float(box_sum(ii_w, *b))
            cands_all.append((content, cx, cy, hw, side_losses(*b)))
    best_ok = pick([c for c in cands_all if max(c[4]) <= max_side_loss])
    chosen = best_ok or pick(cands_all)
    if chosen is None:
        return None
    content, cx, cy, hw, losses = chosen
    return {"rect": (cx - hw, cy - hw / aspect, 2 * hw, 2 * hw / aspect),
            "content": content, "losses": losses, "feasible": best_ok is not None}


def plan_crop(src_w: int, src_h: int, k: float, H: np.ndarray, max_side_loss: float = 0.08):
    """Gültigen Bereich nach der Entzerrung bestimmen und den Bildausschnitt im
    Original-Seitenverhältnis wählen (keine leeren Ränder, möglichst viel Inhalt).

    Rückgabe: dict mit rect (normierte Leinwand-Koordinaten), retention (Anteil
    des Original-Bildinhalts), losses (Beschnitt oben/unten/links/rechts),
    feasible (Seitenbeschnitt im Limit) - oder None."""
    cx, cy, R = _norm_params(src_w, src_h)
    # Rand des Quellbilds vorwärts abbilden -> Ausdehnung der Leinwand
    t = np.linspace(0, 1, 200)
    bx = np.concatenate([t * (src_w - 1), np.full_like(t, src_w - 1), t * (src_w - 1), np.zeros_like(t)])
    by = np.concatenate([np.zeros_like(t), t * (src_h - 1), np.full_like(t, src_h - 1), t * (src_h - 1)])
    pn = np.stack([(bx - cx) / R, (by - cy) / R], axis=1)
    pu = undistort_points(pn, k)
    q = (H @ np.hstack([pu, np.ones((len(pu), 1))]).T).T
    if np.any(q[:, 2] <= 1e-6):
        return None
    qx, qy = q[:, 0] / q[:, 2], q[:, 1] / q[:, 2]
    xmin, xmax = float(qx.min()), float(qx.max())
    ymin, ymax = float(qy.min()), float(qy.max())
    if max(xmax - xmin, ymax - ymin) > 8:
        return None
    cell = max(xmax - xmin, ymax - ymin) / 700.0
    gw = int(math.ceil((xmax - xmin) / cell))
    gh = int(math.ceil((ymax - ymin) / cell))
    gx = xmin + (np.arange(gw) + 0.5) * cell
    gy = ymin + (np.arange(gh) + 0.5) * cell
    GX, GY = np.meshgrid(gx, gy)
    Hinv = np.linalg.inv(H)
    X = Hinv[0, 0] * GX + Hinv[0, 1] * GY + Hinv[0, 2]
    Y = Hinv[1, 0] * GX + Hinv[1, 1] * GY + Hinv[1, 2]
    Z = Hinv[2, 0] * GX + Hinv[2, 1] * GY + Hinv[2, 2]
    ok = Z > 1e-6
    Zs = np.where(ok, Z, 1.0)
    dx, dy, okd = distort_points(X / Zs, Y / Zs, k)
    px, py = dx * R + cx, dy * R + cy
    valid = ok & okd & (px >= 0) & (px <= src_w - 1) & (py >= 0) & (py <= src_h - 1)
    # Wie viele Original-Pixel² deckt jede Rasterzelle ab? (Jacobi-Determinante)
    px_y, px_x = np.gradient(px)
    py_y, py_x = np.gradient(py)
    weight = np.where(valid, np.abs(px_x * py_y - px_y * py_x), 0.0)
    best = _best_content_rect(valid, weight, px, py, src_w / src_h, src_w, src_h, max_side_loss)
    if best is None:
        return None
    rx, ry, rw, rh = best["rect"]
    best["rect"] = (xmin + rx * cell, ymin + ry * cell, rw * cell, rh * cell)
    best["retention"] = best["content"] / float(src_w * src_h)
    return best


def correct_geometry(img: np.ndarray, loaded: LoadedImage, s: Settings):
    h, w = img.shape[:2]
    info = {"k": 0.0, "roll": 0.0, "pitch": 0.0, "keep": 1.0, "applied": False, "notes": []}
    if not (s.lens or s.perspective or s.lens_k is not None):
        return img, info

    gray = cv2.cvtColor(to_u8(img), cv2.COLOR_RGB2GRAY)
    small, _ = resize_long_edge(gray, 1200)
    sh, sw = small.shape

    # --- Objektivverzeichnung
    k = 0.0
    if s.lens_k is not None:
        k = float(s.lens_k)
        info["notes"].append(f"Objektiv: manueller Koeffizient k={k:+.3f}")
    elif s.lens:
        k, linfo = estimate_lens_distortion(small)
        if k:
            info["notes"].append(f"Objektivverzeichnung korrigiert (k={k:+.3f}, "
                                 f"{linfo.get('used')} Kanten, Faktor {linfo.get('gain')})")
        else:
            info["notes"].append(f"Objektiv: keine Korrektur ({linfo['reason']})")
    info["k"] = round(k, 4)

    # --- Senkrechten / Horizont (auf dem entzerrten Vorschaubild)
    roll = pitch = 0.0
    if s.perspective:
        small_u = small
        if k:
            small_u = _remap_normalized(small, k, np.eye(3), _full_rect(sw, sh), (sw, sh),
                                        interp=cv2.INTER_LINEAR)
        focal35 = s.focal35 or loaded.focal35 or 24.0
        f_n = 2.0 * focal35 / 43.27
        try:
            vinfo = estimate_verticals(small_u, f_n, s)
        except Exception as exc:  # noqa: BLE001 - lieber keine Korrektur als kein Bild
            vinfo = {"ok": False, "roll": 0.0, "pitch": 0.0, "lines": 0, "mode": "",
                     "reason": f"interne Schätzung fehlgeschlagen ({type(exc).__name__})"}
        if vinfo["ok"]:
            roll, pitch = math.radians(vinfo["roll"]), math.radians(vinfo["pitch"])
            if abs(vinfo["roll"]) < 0.2:
                roll = 0.0
            if abs(vinfo["pitch"]) < 0.5:
                pitch = 0.0
        else:
            info["notes"].append(f"Senkrechten: keine Korrektur ({vinfo['reason']})")
        focal_note = f"{focal35:.0f} mm KB" + ("" if (s.focal35 or loaded.focal35) else " angenommen")
    else:
        vinfo, focal_note, f_n = None, "", 1.0

    if k == 0 and roll == 0 and pitch == 0:
        return img, info

    K = np.diag([f_n, f_n, 1.0])
    Kinv = np.linalg.inv(K)
    target_pitch = pitch * s.vertical_strength
    if pitch and s.vertical_strength == 0:
        info["notes"].append("Senkrechten: Korrektur abgeschaltet (--vertical-strength 0)")

    def attempt(pf, rf, limit, kf=1.0):
        hm = K @ rotation_matrix(roll * rf, target_pitch * pf) @ Kinv
        return {"pf": pf, "rf": rf, "kf": kf, "H": hm, "plan": plan_crop(w, h, k * kf, hm, limit)}

    def bisect(make, ok, fallback):
        best, lo, hi = fallback, 0.0, 1.0
        for _ in range(7):
            mid = 0.5 * (lo + hi)
            cand = make(mid)
            if ok(cand):
                lo, best = mid, cand
            else:
                hi = mid
        return best

    def keep_ok(a):
        """Mindest-Bildinhalt; mit ausdrücklichem --max-crop auch dessen Grenze."""
        p = a["plan"]
        if p is None or p["retention"] < s.min_keep_area:
            return False
        return not s.max_side_loss_explicit or max(p["losses"]) <= s.max_side_loss + 1e-3

    # 0) Objektiv: extreme (z. B. manuelle) Werte nur so weit, wie der Beschnitt es erlaubt
    kf = 1.0
    lens_loss = 0.0
    if k and not keep_ok(attempt(0.0, 0.0, s.max_side_loss)):
        kf = bisect(lambda f: attempt(0.0, 0.0, s.max_side_loss, f), keep_ok,
                    attempt(0.0, 0.0, s.max_side_loss, 0.0))["kf"]
        info["notes"].append(f"Objektivkorrektur nur zu {kf:.0%} angewendet (Beschnittgrenze)")
        k = k * kf
        info["k"] = round(k, 4)
    if k:
        lens_plan = attempt(0.0, 0.0, s.max_side_loss)["plan"]
        lens_loss = max(lens_plan["losses"]) if lens_plan is not None else 0.0

    # 1) Horizont: Drehen kostet zwangsläufig die Ecken. Begrenzt wird es über den
    #    erhaltenen Bildinhalt - bzw. über --max-crop, wenn ausdrücklich gesetzt.
    base = attempt(0.0, 1.0, s.max_side_loss)
    if roll and not keep_ok(base):
        base = bisect(lambda f: attempt(0.0, f, s.max_side_loss), keep_ok,
                      attempt(0.0, 0.0, s.max_side_loss))
    rf = base["rf"]
    base_loss = max(base["plan"]["losses"]) if base["plan"] is not None else 0.0
    # Die Senkrechten bekommen ihr eigenes Budget ZUSÄTZLICH zu dem, was das
    # Ausrichten des Horizonts schon kostet - sonst bliebe für sie nichts übrig.
    limit = s.max_side_loss if s.max_side_loss_explicit else max(s.max_side_loss, base_loss + 0.025)

    # 2) Stürzende Linien: volle Korrektur, solange je Bildseite höchstens das
    #    Limit wegfällt; sonst so weit abschwächen, dass es passt
    #    (vergleichbar mit "Upright: Auto" in Lightroom).
    def pitch_ok(a):
        p = a["plan"]
        return p is not None and p["retention"] >= s.min_keep_area and max(p["losses"]) <= limit + 1e-6

    chosen = base
    if target_pitch:
        full = attempt(1.0, rf, limit)
        chosen = full if pitch_ok(full) else bisect(lambda f: attempt(f, rf, limit), pitch_ok, base)
    pf = chosen["pf"]
    p_eff, r_eff = target_pitch * pf, roll * rf
    if p_eff and abs(math.degrees(p_eff)) < 0.5:
        chosen, pf, p_eff = base, 0.0, 0.0
    if r_eff and abs(math.degrees(r_eff)) < 0.1:
        r_eff = 0.0
    plan = chosen["plan"]
    if r_eff == 0 and p_eff == 0 and k == 0:
        if roll or target_pitch:
            info["notes"].append("Geometrie: Korrektur hätte zu viel Bild gekostet – übersprungen")
        return img, info
    if plan is None:
        info["notes"].append("Geometrie: kein gültiger Bildausschnitt – übersprungen")
        return img, info

    if vinfo is not None and vinfo["ok"]:
        msg = (f"Senkrechten/Horizont: Drehung {_z(math.degrees(r_eff)):+.2f}°, "
               f"Neigung {_z(math.degrees(p_eff)):+.2f}° "
               f"({vinfo['lines']} Linien, {vinfo['mode']}, {focal_note})")
        if target_pitch and pf < 0.001:
            msg += f" – Neigung nicht korrigiert (gemessen {math.degrees(pitch):+.1f}°), sonst zu viel Beschnitt"
        elif target_pitch and pf < 0.999:
            msg += f" – Neigung zu {pf:.0%} korrigiert (gemessen {math.degrees(pitch):+.1f}°), Beschnittgrenze"
        if roll and rf < 0.001:
            msg += f" – Horizont nicht ausgerichtet (gemessen {math.degrees(roll):+.1f}°), sonst zu viel Beschnitt"
        elif roll and rf < 0.999:
            msg += f" – Horizont zu {rf:.0%} ausgerichtet (gemessen {math.degrees(roll):+.1f}°), Beschnittgrenze"
        info["notes"].append(msg)
    keep_pct = int(round(plan["retention"] * 100))
    t, b, l, r = plan["losses"]
    note = (f"Zuschnitt: oben {t:.0%}, unten {b:.0%}, links {l:.0%}, rechts {r:.0%}; "
            f"{keep_pct} % des Bildinhalts erhalten")
    if max(plan["losses"]) > s.max_side_loss + 0.005:
        roll_loss = max(base_loss - lens_loss, 0.0) if r_eff else 0.0
        if roll_loss > s.max_side_loss:
            note += (f" – ACHTUNG: mehr als {s.max_side_loss:.0%} je Seite, weil der Horizont "
                     f"{abs(math.degrees(roll)):.1f}° schief war; bitte prüfen (mit --max-crop "
                     f"{s.max_side_loss:.2f} wird er nur teilweise ausgerichtet)")
        else:
            causes = [c for c, on in (("Objektiv", bool(k)), ("Horizont", bool(r_eff)),
                                      ("Senkrechten", bool(p_eff))) if on]
            note += f" – etwas mehr als {s.max_side_loss:.0%} je Seite ({' + '.join(causes)} zusammen)"
    info["notes"].append(note)

    rect = plan["rect"]
    _, _, R = _norm_params(w, h)
    out_w = min(w, int(math.floor(rect[2] * R)))
    out_h = min(h, int(round(out_w * h / w)))
    img_out = _remap_normalized(img, k, chosen["H"], rect, (out_w, out_h))
    info.update(roll=round(_z(math.degrees(r_eff)), 2), pitch=round(_z(math.degrees(p_eff)), 2),
                pitch_measured=round(math.degrees(pitch), 2), keep=keep_pct / 100.0, applied=True)
    return np.clip(img_out, 0, 1).astype(np.float32), info


def _z(x: float) -> float:
    """-0.00 vermeiden."""
    return 0.0 if abs(x) < 0.005 else x


def _full_rect(w: int, h: int):
    cx, cy, R = _norm_params(w, h)
    return (-(cx + 0.5) / R, -(cy + 0.5) / R, w / R, h / R)


# --------------------------------------------------------------------------- #
# 4. Ton und Farbe
# --------------------------------------------------------------------------- #

def fast_guided_filter(p: np.ndarray, radius: int, eps: float, work_long: int = 640) -> np.ndarray:
    """Selbstgeführter Guided Filter (He & Sun, 'fast' Variante) - kantenerhaltend."""
    h, w = p.shape
    small, sc = resize_long_edge(p, work_long)
    r = max(1, int(round(radius * sc)))
    ksize = (2 * r + 1, 2 * r + 1)

    def box(x):
        return cv2.boxFilter(x, -1, ksize, borderType=cv2.BORDER_REFLECT)

    mean_i = box(small)
    var_i = box(small * small) - mean_i * mean_i
    a = var_i / (var_i + eps)
    b = mean_i - a * mean_i
    A = cv2.resize(box(a), (w, h), interpolation=cv2.INTER_LINEAR)
    B = cv2.resize(box(b), (w, h), interpolation=cv2.INTER_LINEAR)
    return A * p + B


def estimate_white_balance(lin: np.ndarray, s: Settings):
    """Weißabgleich auf den neutralsten Flächen des Bildes.

    Wände, Decken und Fugen sind in Immobilienfotos fast immer neutral.
    1. Saat: die engste Farbschwelle, die noch genug Fläche abdeckt - so zählen
       beige Fliesen, rosa Fassaden oder Waschbeton nicht als "neutral".
    2. Nachzentrieren auf den Farbton dieser Saat, damit ein Farbstich voll
       erkannt wird und nicht nur sein am wenigsten getönter Rand.
    3. Hat das Bild kaum neutrale Pixel, aber viele leicht warme (reines
       Kunstlicht), wird weich auf eine kräftigere Korrektur übergeblendet.
    """
    small, _ = resize_long_edge(lin, 600)
    px = small.reshape(-1, 3).astype(np.float64)
    Y = px @ LUMA_REC709.astype(np.float64)
    lab0 = cv2.cvtColor(np.clip(px, 0, 1).astype(np.float32).reshape(1, -1, 3),
                        cv2.COLOR_LRGB2Lab).reshape(-1, 3)
    chroma = np.hypot(lab0[:, 1], lab0[:, 2])
    ok = (Y > 0.03) & (px.max(axis=1) < 0.95) & (lab0[:, 0] > 30) & (lab0[:, 0] < 98)

    def gains_of(mask):
        wts = (lab0[mask, 0] / 100.0) ** 2
        mean = (px[mask] * wts[:, None]).sum(axis=0) / wts.sum()
        g = mean.mean() / np.maximum(mean, 1e-6)
        return g / float(g @ LUMA_REC709)

    normal, used = None, 0.0
    for thr in (6.0, 9.0, 13.0, 18.0):
        m = ok & (chroma < thr)
        if m.mean() < 0.05:
            continue
        for _ in range(2):
            wts = (lab0[m, 0] / 100.0) ** 2
            ca = float((lab0[m, 1] * wts).sum() / wts.sum())
            cb = float((lab0[m, 2] * wts).sum() / wts.sum())
            cand = ok & (np.hypot(lab0[:, 1] - ca, lab0[:, 2] - cb) < 5.0) & (chroma < 18.0)
            if cand.mean() < 0.05:
                break
            m = cand
        normal, used = gains_of(m), float(m.mean())
        break

    w_uni, uniform = float(smoothstep(0.03, 0.005, float((ok & (chroma < 6)).mean()))), None
    if w_uni > 0:
        for thr in (20.0, 26.0, 32.0):
            cand = ok & (chroma < thr)
            # nur warme Stiche (Glühlampe/Halogen) - ein großer blauer Himmel ist kein Farbstich
            if cand.mean() > 0.40 and float(np.median(lab0[cand, 2])) > 4.0:
                uniform = gains_of(cand)
                used = max(used, float(cand.mean()))
                break
    if uniform is None:
        w_uni = 0.0
    if normal is None and uniform is None:
        return np.ones(3, np.float32), {"skipped": "zu wenig neutrale Flächen"}
    if normal is None:
        normal, w_uni = uniform, 1.0
    gains = np.exp(np.log(normal) * (1 - w_uni) + np.log(uniform if uniform is not None else normal) * w_uni)
    gains = gains ** float(np.clip(s.wb_strength, 0, 1))
    # Starke Farbstiche entstehen meist durch Mischlicht (Glühlampe + Fenster).
    # Voll neutralisiert würde das Tageslicht dann blau -> Korrektur begrenzen.
    max_ratio = math.exp(math.log(s.wb_max_ratio) * (1 - w_uni) + math.log(1.45) * w_uni)
    ratio = float(gains.max() / gains.min())
    if ratio > max_ratio:
        gains = gains ** (math.log(max_ratio) / math.log(ratio))
    gains = gains * np.array([1 + s.warmth, 1.0, 1 - s.warmth])
    gains = gains / float(gains @ LUMA_REC709)
    return gains.astype(np.float32), {"gains": gains.round(3).tolist(), "neutral": round(used, 3),
                                      "uniform_cast": round(w_uni, 2)}


def apply_white_balance(lin: np.ndarray, gains: np.ndarray, protect: np.ndarray) -> np.ndarray:
    """Weißabgleich anwenden - schonend bei Mischlicht und ausgebrannten Lichtern.

    Kühlt die Korrektur einen Kunstlicht-Stich, darf kein Pixel dadurch
    deutlich bläulich werden (Tageslicht-Reflexe, Fensterlicht bleiben, wie sie
    sind); umgekehrt beim Wärmen. Ausgebrannte Lichter enthalten keine
    Farbinformation mehr und werden gar nicht eingefärbt."""
    full = lin * (1.0 + (gains.reshape(1, 1, 3) - 1.0) * (1.0 - protect[..., None]))
    if gains[2] > gains[0]:
        ch_a, ch_b = 2, 0          # Blau-Überhang begrenzen
    elif gains[0] > gains[2]:
        ch_a, ch_b = 0, 2          # Rot-Überhang begrenzen
    else:
        return full.astype(np.float32)
    d_in = (lin[..., ch_a] - lin[..., ch_b]) / np.maximum(lin.mean(axis=2), 1e-4)
    d_out = (full[..., ch_a] - full[..., ch_b]) / np.maximum(full.mean(axis=2), 1e-4)
    allowed = np.maximum(d_in, 0.05)
    t = np.where(d_out > allowed, np.clip((allowed - d_in) / np.maximum(d_out - d_in, 1e-6), 0, 1), 1.0)
    return (lin + (full - lin) * t[..., None]).astype(np.float32)


def highlight_protect_mask(srgb: np.ndarray) -> np.ndarray:
    """Weiche Maske für (fast) ausgebrannte Bereiche, z. B. Fenster.

    Echt ausgebrannte Pixel enthalten keine Information mehr. Sie dürfen nicht
    grau abgedunkelt werden, sonst wirken Fenster schmutzig."""
    m = smoothstep(0.90, 0.985, srgb.max(axis=2))
    sigma = max(1.0, max(srgb.shape[:2]) / 1500.0)
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), sigma)


def highlight_shoulder(lin: np.ndarray, knee: float = 0.8) -> np.ndarray:
    """Werte über 1 weich (farbton-erhaltend) zurückführen statt hart abzuschneiden."""
    m = lin.max(axis=2)
    small, _ = resize_long_edge(m, 800)
    m_max = float(np.percentile(small, 99.95))
    if m_max <= 1.0:
        return np.clip(lin, 0, 1)
    lw = (m_max - knee) / (1.0 - knee)
    x = np.maximum(m - knee, 0) / (1.0 - knee)
    x2 = x * (1.0 + x / (lw * lw)) / (1.0 + x)
    m_new = np.where(m > knee, knee + x2 * (1.0 - knee), m)
    scale = m_new / np.maximum(m, 1e-6)
    out = lin * scale[:, :, None]
    # Stark komprimierte Spitzlichter laufen wie bei einer Kamera ins Weiße aus,
    # statt farbig zu bleiben (sonst wirken z. B. Fliesenreflexe wie Flecken).
    # Kräftig farbige Flächen (sonnenbeschienenes Holz, Ziegel) aber nicht: die würden
    # sonst zu weißen Flecken ausbleichen.
    sat = 1.0 - lin.min(axis=2) / np.maximum(m, 1e-6)
    wdes = (smoothstep(0.85, 1.0, m_new) * np.clip(2.0 * (1.0 - scale), 0.0, 1.0)
            * (1.0 - smoothstep(0.35, 0.6, sat)))
    out = out + (m_new[:, :, None] - out) * wdes[:, :, None]
    return np.clip(out, 0, 1)


def _limit_gain_in_bright_areas(lin: np.ndarray, gain: np.ndarray) -> np.ndarray:
    """Aufhellen in GROSSEN Flächen begrenzen, deren hellster Farbkanal danach
    überlaufen würde (blauer Himmel, Sonnenflecken, helle Fenster).

    Kantenerhaltend (Guided Filter) und morphologisch geöffnet: Kleine
    Glanzlichter bleiben ungebremst. Würden auch sie gebremst, blieben sie
    dunkler als ihre aufgehellte Umgebung und sähen wie farbige Flecken aus."""
    h, w = lin.shape[:2]
    log_mx = np.log2(np.maximum(lin.max(axis=2), 1.0 / 4096)).astype(np.float32)
    log_mx_base = fast_guided_filter(log_mx, int(0.03 * max(h, w)), 0.3)
    over = smoothstep(0.6, 1.0, np.exp2(log_mx_base + np.maximum(gain, 0)))
    small, _ = resize_long_edge(over.astype(np.float32), 600)
    size = max(3, int(0.05 * max(small.shape)) | 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
    # Öffnen entfernt kleine Flächen; das anschließende Wachsen stellt die volle
    # Ausdehnung großer Flächen bis an ihre Kante wieder her (sonst heller Saum).
    region = cv2.dilate(cv2.morphologyEx(small, cv2.MORPH_OPEN, kernel), kernel)
    region = cv2.GaussianBlur(region, (0, 0), size / 6.0)
    region = np.minimum(cv2.resize(region, (w, h), interpolation=cv2.INTER_LINEAR), over)
    # Satte Farben (Himmelsblau) auch in schmalen Flächen schützen, z. B. Himmel
    # zwischen Dachbalken: dort würde sonst ein einzelner Kanal ausbrennen.
    # Blasse Glanzlichter dürfen dagegen hell werden - wie bei einer Kamera.
    blur = cv2.GaussianBlur(np.clip(lin, 0, 1).astype(np.float32), (0, 0), max(1.0, max(h, w) / 400.0))
    lab_b = cv2.cvtColor(blur, cv2.COLOR_LRGB2Lab)
    # Wahrnehmungsgerechte Buntheit. Warme Töne zählen erst ab hoher Buntheit
    # (Ziegeldächer ja, warm angestrahlte cremefarbene Decken und beige Fliesen
    # nein - sonst entstehen dort graue Flecken), bläuliche schon ab mäßiger
    # (Himmel hinter Glas oder Dunst).
    # Rottöne (Dachziegel, Klinker) zählen schon ab mittlerer Buntheit - gelbliche
    # Töne wie beige Fliesen dagegen nicht.
    chroma_b = np.hypot(lab_b[..., 1], lab_b[..., 2])
    sat_lin = 1.0 - blur.min(axis=2) / np.maximum(blur.max(axis=2), 1e-4)
    hue_b = np.degrees(np.arctan2(lab_b[..., 2], lab_b[..., 1]))
    red = smoothstep(-40.0, -20.0, hue_b) * (1.0 - smoothstep(40.0, 55.0, hue_b))
    sat_w = np.maximum.reduce([smoothstep(25.0, 40.0, chroma_b),
                               smoothstep(10.0, 20.0, chroma_b) * smoothstep(-3.0, -10.0, lab_b[..., 2]),
                               smoothstep(0.25, 0.45, sat_lin) * smoothstep(14.0, 20.0, chroma_b) * red])
    region = np.maximum(region, over * sat_w)
    cap = np.maximum(math.log2(0.85) - log_mx_base, 0.0)      # hellster Kanal max. ~0.85 linear
    # Satte Flächen (Himmel, Aussicht) nur wenig anheben - sonst werden sie flau und flach.
    cap = cap - sat_w * np.maximum(cap - 0.35, 0.0)
    return gain - region * np.maximum(gain - cap, 0.0)


def _wall_exposure(lin: np.ndarray):
    """Belichtung (EV), die helle neutrale Flächen (Wände, Decken) auf ein
    freundliches Weiß bringen würde, und deren Helligkeit - oder None ohne
    solche Flächen.

    Maßgeblich sind die helleren 30 % dieser Flächen (70. Perzentil), damit
    graue Böden oder Fliesen nicht mitzählen und der Bildausschnitt die
    Belichtung nicht verschiebt. "Neutral" wird relativ zum vorherrschenden
    Wandton bestimmt, damit auch ein Rest Kunstlichtstich nicht stört."""
    small, _ = resize_long_edge(lin, 512)
    px = small.reshape(-1, 3)
    lab = cv2.cvtColor(np.clip(px, 0, 1).reshape(1, -1, 3).astype(np.float32), cv2.COLOR_LRGB2Lab).reshape(-1, 3)
    chroma = np.hypot(lab[:, 1], lab[:, 2])
    base = (lab[:, 0] > 45) & (px.max(axis=1) < 0.9)
    near = base & (chroma < 20)
    ca, cb = (float(np.median(lab[near, 1])), float(np.median(lab[near, 2]))) if near.mean() >= 0.05 else (0.0, 0.0)
    m = base & (np.hypot(lab[:, 1] - ca, lab[:, 2] - cb) < 8)
    if m.mean() < 0.05:
        return None
    wall = float(np.percentile(px[m] @ LUMA_REC709, 70))
    return math.log2(0.70 / max(wall, 1e-4)), wall


def local_tone_map(lin: np.ndarray, protect: np.ndarray, s: Settings, noise_sigma=None):
    """Belichtung + Schatten/Lichter in log2-Luminanz (Basis/Detail-Zerlegung).

    Nur die großflächige Basis wird verändert, feine Details bleiben 1:1
    erhalten - so wirkt das Ergebnis nicht wie ein HDR-Foto."""
    h, w = lin.shape[:2]
    Y = luminance(lin)
    logY = np.log2(np.maximum(Y, 1.0 / 4096)).astype(np.float32)

    small, _ = resize_long_edge(logY, 512)
    lo, hi = np.percentile(small, [5, 95])
    key = float(small[(small >= lo) & (small <= hi)].mean())
    e = s.target_key_ev - key
    e_key = None
    if e < 0:
        # Abdunkeln nur, wenn wirklich Lichter ausbrennen - weich eingeblendet,
        # damit ähnliche Bilder nicht sprunghaft verschieden hell werden.
        near_clip = float((small > math.log2(0.95)).mean())
        e = max(min(0.0, (e + 0.4) * 0.6), -s.max_ev_down) * float(smoothstep(0.02, 0.08, near_clip))
    # Helle neutrale Flächen (Wände, Decken) sollen einheitlich freundlich hell
    # werden - auch wenn die Durchschnittshelligkeit schon passt (max. +0.6 EV mehr).
    # Bis 0.8 Rauschen darf stärker aufgehellt werden, darüber weich weniger.
    max_up = s.max_ev_up_clean - (s.max_ev_up_clean - s.max_ev_up) * float(
        smoothstep(0.8, 1.4, noise_sigma if noise_sigma is not None else 99.0))
    e_key = min(max(e, 0.0), max_up) if e > 0 else e
    wall = _wall_exposure(lin)
    if wall is not None and wall[0] > e:
        e = min(wall[0], e + 0.6)       # mehr würde Lampenschein und Aussichten verfälschen
    e = min(e, max_up)

    base = fast_guided_filter(logY, radius=int(0.03 * max(h, w)), eps=0.3)
    d = base + e - s.target_key_ev
    lift = s.max_shadow_lift_ev * np.tanh(np.maximum(-d, 0) * (1 - s.shadow_compress)
                                          / s.max_shadow_lift_ev)
    # Lichter erst oberhalb eines Knies absenken: diffus weiße Wände sind keine Lichter.
    cut = s.max_highlight_cut_ev * np.tanh(np.maximum(d - s.highlight_knee_ev, 0)
                                           * (1 - s.highlight_compress) / s.max_highlight_cut_ev)
    gain = e + lift - cut
    extra = e - e_key
    if extra > 0 and wall is not None:
        # Die zusätzliche Aufhellung für die Wände wird auf Flächen, die deutlich
        # heller als die Wände sind (Fensteraussichten, Lampenschein), weich
        # zurückgenommen - sonst werden sie flau. Die Rücknahme hängt nur von der
        # (großflächigen) Helligkeit ab und steigt über >= 1.5 EV an: So bleibt die
        # Helligkeitsreihenfolge erhalten, nichts wird dunkler als seine Umgebung.
        t0 = math.log2(max(wall[1], 1e-4)) + 0.3
        gain = gain - extra * smoothstep(t0, t0 + max(1.5 * extra, 0.5), base)
    gain = gain * (1 - protect) + np.maximum(gain, 0) * protect
    # Aufhellen dort zurücknehmen, wo ein Farbkanal großflächig schon fast voll
    # ist (blauer Himmel, Sonnenflecken, helle Fenster) - sonst brennt dieser
    # Kanal aus.
    gain = _limit_gain_in_bright_areas(lin, gain)
    out = lin * np.exp2(gain)[:, :, None]
    # Neutrale helle Flächen erst später komprimieren (Knie 0.9 statt 0.8), damit
    # Flecken, Risse und Spuren an hellen Wänden ihren Kontrast behalten.
    sat_out = 1.0 - out.min(axis=2) / np.maximum(out.max(axis=2), 1e-4)
    out = highlight_shoulder(out, knee=0.8 + 0.1 * (1.0 - smoothstep(0.05, 0.15, sat_out)))
    # Ausgebrannte Flächen (Fenster, Oberlichter) sauber weiß statt hellgrau.
    blown = protect * smoothstep(0.90, 0.98, lin.min(axis=2))
    out = out + (1.0 - out) * blown[:, :, None]
    return out.astype(np.float32), {"key": round(key, 2), "ev": round(_z(e), 2)}


def apply_levels(srgb: np.ndarray):
    """Schwarz- und Weißpunkt behutsam setzen (keine abgesoffenen Schatten)."""
    small, _ = resize_long_edge(srgb, 800)
    luma = small @ np.array([0.299, 0.587, 0.114], np.float32)
    lo = float(np.percentile(luma, 0.5))
    hi = float(np.percentile(small.max(axis=2), 99.8))   # Maximalkanal: kein Kanal clippt
    b = float(np.clip((lo - 0.015) / (1 - 0.015), 0.0, 0.02))
    g_cap = 1.10 + 0.25 * (1.0 - float(smoothstep(0.65, 0.85, hi)))   # ohne echte Lichter: Weiß darf weiß werden
    g = float(max(1.0 / (1.0 - b), min(0.975 / max(hi - b, 1e-3), g_cap)))
    return np.clip((srgb - b) * g, 0, 1), {"black": round(b, 3), "gain": round(g, 3)}


def finish_lab(srgb: np.ndarray, is_gray: bool, s: Settings,
               reference: Optional[np.ndarray] = None) -> np.ndarray:
    """S-Kurve (Kontrast), Dynamik und Schärfung im Lab-Raum.

    reference = Bild vor der Ton-/Farbbearbeitung: Die Buntheit darf gegenüber
    dem Original nur maßvoll steigen (kein Lila-Stich in aufgehellten Schatten)."""
    lab = cv2.cvtColor(srgb.astype(np.float32), cv2.COLOR_RGB2Lab)
    L0 = lab[:, :, 0].copy()
    # Nahe am Kanal-Maximum (sonnige Ziegeldächer, helle Fassaden) weder S-Kurve
    # noch Dynamik noch Schärfung - sonst brennt dort ein einzelner Farbkanal aus.
    sat_s = 1.0 - srgb.min(axis=2) / np.maximum(srgb.max(axis=2), 1e-4)
    calm = 1.0 - smoothstep(0.88, 0.97, srgb.max(axis=2)) * smoothstep(0.03, 0.08, sat_s)
    x = L0 / 100.0
    L = L0 + (100.0 * (x + s.contrast * x * (1 - x) * (2 * x - 1)) - L0) * calm

    if not is_gray and s.vibrance:
        a, b = lab[:, :, 1], lab[:, :, 2]
        chroma = np.hypot(a, b)
        boost = s.vibrance * smoothstep(2.0, 10.0, chroma) * (1 - np.clip(chroma / 70.0, 0, 1)) ** 2 * calm
        lab[:, :, 1] = a * (1 + boost)
        lab[:, :, 2] = b * (1 + boost)
        if reference is not None:
            ref = cv2.cvtColor(reference.astype(np.float32), cv2.COLOR_RGB2Lab)
            c_in = np.hypot(ref[:, :, 1], ref[:, :, 2])
            # Warme Töne dürfen mit der Aufhellung mitwachsen (sonst wirken
            # aufgehellte Räume blass), kühle nicht (sonst lila Schatten).
            grow = np.maximum((L + 16.0) / (ref[:, :, 0] + 16.0), 1.0)
            c_ref = np.where(ref[:, :, 2] > 0, c_in * grow, c_in)
            c_out = np.hypot(lab[:, :, 1], lab[:, :, 2])
            limit = np.maximum(c_ref * 1.2, c_ref + 2.0)
            f = np.where(c_out > limit, limit / np.maximum(c_out, 1e-6), 1.0)
            # Aufgehellte, vorher dunkle Schatten mit blau-violettem Himmelslicht dämpfen.
            # nur bei Außenaufnahmen (sichtbarer Himmel) - blaue/lila Möbel innen bleiben
            sky = float(((ref[:, :, 0] > 50) & (ref[:, :, 2] < -15)).mean())
            violet = (smoothstep(40.0, 25.0, ref[:, :, 0]) * smoothstep(4.0, 12.0, L - ref[:, :, 0])
                      * smoothstep(-4.0, -10.0, lab[:, :, 2]) * smoothstep(0.0, 4.0, lab[:, :, 1])
                      * float(smoothstep(0.01, 0.04, sky)))
            f = f * (1.0 - 0.5 * violet)
            lab[:, :, 1] *= f
            lab[:, :, 2] *= f

    if s.sharpen > 0:
        sigma = float(np.clip(max(L.shape) / 2400.0, 0.6, 1.6))
        detail = L - cv2.GaussianBlur(L, (0, 0), sigma)
        thr = 0.6
        detail = np.sign(detail) * np.maximum(np.abs(detail) - thr, 0)
        L = L + np.clip(0.55 * s.sharpen * detail, -5.0, 5.0) * calm

    lab[:, :, 0] = np.clip(L, 0, 100)
    if is_gray:
        lab[:, :, 1:] = 0
    return np.clip(cv2.cvtColor(lab, cv2.COLOR_Lab2RGB), 0, 1)


def tone_and_color(srgb: np.ndarray, is_gray: bool, s: Settings, noise_sigma=None):
    info = {}
    protect = highlight_protect_mask(srgb)
    lin = srgb_to_linear(srgb)
    if not is_gray and s.wb_strength > 0:
        gains, info["wb"] = estimate_white_balance(lin, s)
        lin = apply_white_balance(lin, gains, protect)
    lin, info["tone"] = local_tone_map(lin, protect, s, noise_sigma)
    out = linear_to_srgb(lin)
    out, info["levels"] = apply_levels(out)
    out = finish_lab(out, is_gray, s, reference=srgb)
    return out, info


# --------------------------------------------------------------------------- #
# 5. Speichern
# --------------------------------------------------------------------------- #

def _exif_bytes(exif: Optional[Image.Exif], size: tuple, notes: list) -> Optional[bytes]:
    if exif is None:
        return None
    try:
        sub = exif.get_ifd(0x8769)
        if 0xA002 in sub:
            sub[0xA002] = size[0]
        if 0xA003 in sub:
            sub[0xA003] = size[1]
    except Exception:
        pass
    try:
        return exif.tobytes()
    except Exception:
        try:  # defekte Herstellerdaten sind die häufigste Ursache
            exif.get_ifd(0x8769).pop(0x927C, None)
            data = exif.tobytes()
            notes.append("EXIF-MakerNote nicht übertragbar, restliche EXIF-Daten übernommen")
            return data
        except Exception as exc:
            notes.append(f"EXIF-Daten nicht übertragbar ({exc})")
            return None


def save_jpeg(srgb: np.ndarray, dst: Path, loaded: LoadedImage, s: Settings, notes: list):
    arr = to_u8(srgb)
    im = Image.fromarray(arr[:, :, 0], "L") if loaded.is_gray else Image.fromarray(arr, "RGB")
    kwargs = dict(format="JPEG", quality=int(s.jpeg_quality), subsampling=0,
                  optimize=True, progressive=True, comment=OUTPUT_MARKER)
    if loaded.icc_out and not loaded.is_gray:
        kwargs["icc_profile"] = loaded.icc_out
    exif = _exif_bytes(loaded.exif, im.size, notes)
    if exif and len(exif) > 65533:        # ein JPEG-Segment fasst max. 64 KB
        notes.append("EXIF-Daten zu groß für JPEG (> 64 KB) – nicht übernommen")
        exif = None
    if exif:
        kwargs["exif"] = exif
    if loaded.xmp and len(loaded.xmp) > 65504:
        notes.append("XMP-Daten zu groß für JPEG (> 64 KB) – nicht übernommen")
    elif loaded.xmp:
        kwargs["xmp"] = loaded.xmp
    if loaded.dpi:
        kwargs["dpi"] = tuple(int(round(float(v))) for v in loaded.dpi[:2])

    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".jpg", dir=str(dst.parent))
    os.close(fd)
    try:  # mkstemp legt 0600 an - fertige Fotos sollen normal lesbar sein
        os.chmod(tmp, 0o666 & ~_UMASK)
    except OSError:
        pass
    try:
        try:
            im.save(tmp, **kwargs)
        except (OSError, ValueError):
            kwargs.pop("optimize", None)
            kwargs.pop("progressive", None)
            im.save(tmp, **kwargs)
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def save_compare(before: np.ndarray, after: np.ndarray, dst: Path):
    height = min(900, before.shape[0], after.shape[0])

    def fit(img):
        s = height / img.shape[0]
        return cv2.resize(to_u8(img), (int(round(img.shape[1] * s)), height), interpolation=cv2.INTER_AREA)

    a, b = fit(before), fit(after)
    gap = np.full((height, 12, 3), 255, np.uint8)
    canvas = np.hstack([a, gap, b])
    for text, x in (("Original", 12), ("Bearbeitet", a.shape[1] + 24)):
        cv2.putText(canvas, text, (x, 36), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(canvas, text, (x, 36), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(canvas, "RGB").save(dst, "JPEG", quality=88, comment=OUTPUT_MARKER)


# --------------------------------------------------------------------------- #
# Ein Bild komplett verarbeiten
# --------------------------------------------------------------------------- #

def process_image(src: Path, dst: Path, s: Settings, compare_dst: Optional[Path] = None) -> dict:
    t0 = time.time()
    loaded = load_image(src, s)
    notes = list(loaded.notes)
    original = loaded.rgb
    h0, w0 = original.shape[:2]

    img, dn = denoise_image(original, loaded.high_bit_depth, s)
    notes.append(f"Rauschen σ={dn['sigma']}: " + (dn["applied"] or "gering – keine Reduzierung nötig"))
    img, geo = correct_geometry(img, loaded, s)
    notes.extend(geo["notes"])

    if s.max_long_edge and max(img.shape[:2]) > s.max_long_edge:
        img, _ = resize_long_edge(img, s.max_long_edge)
        notes.append(f"auf {s.max_long_edge} px lange Kante verkleinert")

    img, tone = tone_and_color(img, loaded.is_gray, s, dn["sigma"])
    save_jpeg(img, dst, loaded, s, notes)
    if compare_dst is not None:
        save_compare(original, img, compare_dst)

    return {
        "src": str(src), "dst": str(dst),
        "size_in": (w0, h0), "size_out": (img.shape[1], img.shape[0]),
        "noise": dn, "geometry": {k: v for k, v in geo.items() if k != "notes"},
        "tone": tone, "notes": notes, "seconds": round(time.time() - t0, 2),
    }


def _summary_line(r: dict) -> str:
    parts = [f"{r['size_in'][0]}x{r['size_in'][1]} -> {r['size_out'][0]}x{r['size_out'][1]}"]
    if r["noise"].get("applied") and r["noise"]["applied"] != "abgeschaltet":
        parts.append("Rauschen reduziert")
    g = r["geometry"]
    if g.get("applied"):
        geo = f"Drehung {g['roll']:+.1f}°, Neigung {g['pitch']:+.1f}°"
        if g.get("k"):
            geo += f", Objektiv k={g['k']:+.3f}"
        parts.append(f"{geo}, Bildinhalt {g['keep']:.0%}")
    wb = r["tone"].get("wb", {})
    if "gains" in wb:
        gr = wb["gains"]
        parts.append(f"WB R×{gr[0]:.2f} B×{gr[2]:.2f}")
    parts.append(f"Belichtung {r['tone']['tone']['ev']:+.2f} EV")
    parts.append(f"{r['seconds']:.1f} s")
    return " | ".join(parts)


def _friendly_error(exc: BaseException) -> str:
    """Technische Ausnahmen in verständliche Ursachen übersetzen."""
    msg = str(exc)
    if isinstance(exc, UnidentifiedImageError):
        return "keine lesbare Bilddatei (beschädigt oder anderes Format)"
    if isinstance(exc, Image.DecompressionBombError):
        return "Bild ist zu groß (über 250 Megapixel)"
    if isinstance(exc, MemoryError):
        return "zu wenig Arbeitsspeicher"
    if isinstance(exc, OSError) and ("truncated" in msg or "broken data stream" in msg):
        return "Datei unvollständig oder beschädigt"
    return f"{type(exc).__name__}: {msg}"


def _worker(args):
    src, dst, settings, compare_dst, threads = args
    if threads:
        cv2.setNumThreads(threads)
    try:
        return "ok", src, process_image(Path(src), Path(dst), settings,
                                        Path(compare_dst) if compare_dst else None)
    except SkipImage as exc:
        return "skip", src, str(exc)
    except Exception as exc:  # noqa: BLE001 - jedes Bild einzeln absichern
        return "error", src, f"{_friendly_error(exc)}\n{traceback.format_exc()}"


def _terminate_pool(ex: ProcessPoolExecutor):
    procs = list((getattr(ex, "_processes", None) or {}).values())
    try:
        ex.shutdown(wait=False, cancel_futures=True)
    except Exception:
        pass
    for proc in procs:
        try:
            proc.terminate()
        except Exception:
            pass


def _run_parallel(work: list, workers: int, threads: int, report) -> bool:
    """Bilder parallel verarbeiten. Stürzt ein Prozess ab (z. B. zu wenig
    Arbeitsspeicher), laufen die offenen Bilder erst in einem frischen Pool
    weiter; was dort erneut abstürzt, wird einzeln wiederholt, damit nur das
    schuldige Bild als Fehler endet. Rückgabe False = Strg+C."""
    pending = {job[0]: job for job in work}
    ex = None

    def run_pool(jobs, n_workers, n_threads):
        nonlocal ex
        ex = ProcessPoolExecutor(max_workers=n_workers)
        futs = {ex.submit(_worker, (*job, n_threads)): job for job in jobs}
        for fut in as_completed(futs):
            job = futs[fut]
            try:
                result = fut.result()
            except BrokenProcessPool:
                continue
            except Exception as exc:  # noqa: BLE001
                pending.pop(job[0], None)
                report("error", job[0], f"Verarbeitung abgebrochen: {exc}")
                continue
            pending.pop(job[0], None)
            report(*result)
        ex.shutdown(wait=True)

    try:
        run_pool(list(pending.values()), workers, threads)
        if pending:
            log.warning("Ein Arbeitsprozess ist abgestürzt (z. B. zu wenig Arbeitsspeicher) – "
                        "%d Bild(er) werden erneut verarbeitet.", len(pending))
            run_pool(list(pending.values()), max(1, workers - 1), threads)
        for job in list(pending.values()):          # nur noch die wirklich schuldigen
            ex = ProcessPoolExecutor(max_workers=1)
            try:
                report(*ex.submit(_worker, (*job, 0)).result())
            except BrokenProcessPool:
                report("error", job[0], "Arbeitsprozess abgestürzt (vermutlich zu wenig Arbeitsspeicher)")
            pending.pop(job[0], None)
            ex.shutdown(wait=True)
        return True
    except KeyboardInterrupt:
        if ex is not None:
            _terminate_pool(ex)
        return False


# --------------------------------------------------------------------------- #
# Dateiauswahl und Hauptprogramm
# --------------------------------------------------------------------------- #

def _is_output_tree(d: Path) -> bool:
    """Ausgabeordner (auch früherer Läufe) erkennt man am Namen oder an einem
    nicht leeren Manifest - nicht bloß am Protokoll, das ein Lauf ohne
    Ergebnis ebenfalls hinterlassen kann."""
    if d.name in (DEFAULT_OUTPUT_DIRNAME, COMPARE_DIRNAME):
        return True
    try:
        return bool(_load_manifest(d))
    except OSError:
        return False


def discover_images(input_dir: Path, output_dir: Path, recursive: bool, pruned: Optional[list] = None,
                    unreadable: Optional[list] = None) -> list:
    """Alle JPG/JPEG/PNG-Dateien finden. Ausgelassen werden versteckte Dateien,
    macOS-"._"-Dateien, versteckte Ordner, NAS-Systemordner ("@eaDir", "#recycle" …)
    und Ausgabeordner früherer Läufe - sonst würden Ergebnisse doppelt bearbeitet."""
    out_res = output_dir.resolve()
    in_res = input_dir.resolve()
    output_inside_input = in_res in out_res.parents
    if unreadable is None:
        unreadable = []

    def candidates():
        if not recursive:
            yield from input_dir.iterdir()
            return
        for root, dirs, names in os.walk(input_dir, onerror=lambda e: unreadable.append(e)):
            rootp = Path(root)
            keep = []
            for d in dirs:
                if d.startswith(".") or d in NAS_SYSTEM_DIRS or _is_output_tree(rootp / d):
                    if pruned is not None:
                        pruned.append(rootp / d)
                else:
                    keep.append(d)
            dirs[:] = keep
            for n in names:
                yield rootp / n

    files = []
    for p in candidates():
        try:
            if not p.is_file():
                continue
        except OSError:
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        if output_inside_input:
            rp = p.resolve()
            if rp == out_res or out_res in rp.parents:
                continue
        files.append(p)
    return sorted(files, key=lambda p: str(p).lower())


def plan_outputs(files: list, input_root: Path, output_dir: Path) -> list:
    """Zielnamen festlegen: JPEGs behalten ihren Namen exakt, PNGs werden .jpg.
    Namenskonflikte (foto.png + foto.jpg) werden eindeutig aufgelöst."""
    used, plan = set(), {}
    ordered = sorted(files, key=lambda p: (p.suffix.lower() == ".png", str(p).lower()))
    for p in ordered:
        rel = p.relative_to(input_root)
        name = p.name if p.suffix.lower() in (".jpg", ".jpeg") else p.stem + ".jpg"
        cand = rel.with_name(name)
        n = 1
        while str(cand).lower() in used:
            suffix = p.suffix.lower().lstrip(".")
            cand = rel.with_name(f"{p.stem}_{suffix}{'' if n == 1 else f'_{n}'}.jpg")
            n += 1
        used.add(str(cand).lower())
        plan[p] = output_dir / cand
    return [(p, plan[p]) for p in files]


def _file_id(p: Path):
    try:
        st = p.stat()
    except OSError:
        return None
    return (st.st_dev, st.st_ino) if st.st_ino else None


def _destination_problem(src: Path, dst: Path, rel_dst: str, originals: set, original_ids: set,
                         manifest: dict) -> str:
    """Grund, warum dst nicht beschrieben werden darf - oder "" wenn alles in Ordnung ist.

    Mehrfache Absicherung: niemals Originale überschreiben - auch nicht über
    Verknüpfungen, eingebundene Laufwerke, Groß-/Kleinschreibung oder einen
    Unterordner der Eingabe als Ausgabeordner. Vorhandene Dateien werden nur
    überschrieben, wenn sie nachweislich von diesem Skript stammen und seitdem
    nicht verändert wurden."""
    if dst.resolve() in originals or (_file_id(dst) in original_ids):
        return "Ziel wäre eine Originaldatei"
    if not dst.exists():
        return ""
    entry = manifest.get(rel_dst)
    if isinstance(entry, list) and len(entry) >= 5:
        # Wir wissen genau, was wir geschrieben haben: nur unverändert überschreiben.
        if _matches_manifest(dst, entry):
            return ""
        return (f"{dst} wurde seit dem letzten Lauf verändert (nachbearbeitet?) – "
                "wird nicht überschrieben; Datei löschen, um sie neu zu erzeugen")
    if _is_our_output(dst):
        return ""
    return (f"{dst} existiert bereits und ist nicht als Ausgabe dieses Skripts erkennbar "
            "(fremde Datei oder ältere Version) – Datei löschen oder anderen Ausgabeordner wählen")


def _matches_manifest(dst: Path, entry) -> bool:
    """Manifest-Eintrag gilt nur, wenn die Datei seit dem Schreiben unverändert ist."""
    if not isinstance(entry, list) or len(entry) < 5:
        return False
    try:
        st = dst.stat()
    except OSError:
        return False
    return entry[3] == st.st_size and entry[4] == st.st_mtime_ns


def _is_our_output(p: Path) -> bool:
    """Stammt die (vorhandene) Datei von diesem Skript? Nur solche Dateien werden überschrieben."""
    try:
        with Image.open(p) as im:
            return OUTPUT_MARKER in (im.info.get("comment") or b"")
    except Exception:
        return False


def _all_input_ids(input_root: Path, output_dir: Path) -> set:
    """Datei-Identitäten ALLER Bilder unter dem Eingabeordner (ohne den Ausgabeordner),
    unabhängig von -r - Schutz gegen Aliase, Verknüpfungen und Unterordner als Ziel."""
    out_res = output_dir.resolve()
    ids = set()
    for root, dirs, names in os.walk(input_root, onerror=lambda e: None):
        rootp = Path(root)
        dirs[:] = [d for d in dirs if (rootp / d).resolve() != out_res]
        for n in names:
            if Path(n).suffix.lower() in SUPPORTED_EXTENSIONS:
                fid = _file_id(rootp / n)
                if fid:
                    ids.add(fid)
    return ids


def _source_signature(p: Path, input_root: Path) -> list:
    st = p.stat()
    return [p.relative_to(input_root).as_posix(), st.st_size, st.st_mtime_ns]


def _load_manifest(output_dir: Path) -> dict:
    try:
        with open(output_dir / MANIFEST_NAME, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save_manifest(output_dir: Path, manifest: dict):
    tmp = output_dir / (MANIFEST_NAME + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, ensure_ascii=True, indent=0)
        os.replace(tmp, output_dir / MANIFEST_NAME)
    except (OSError, ValueError):
        try:
            tmp.unlink()
        except OSError:
            pass


def _ranged(kind, lo=None, hi=None):
    def conv(value):
        try:
            v = kind(value)
        except ValueError:
            raise argparse.ArgumentTypeError(f"'{value}' ist keine gültige Zahl")
        if isinstance(v, float) and not math.isfinite(v):
            raise argparse.ArgumentTypeError(f"'{value}' ist keine gültige Zahl")
        if (lo is not None and v < lo) or (hi is not None and v > hi):
            rng = f"{lo} bis {hi}" if hi is not None else f"mindestens {lo}"
            raise argparse.ArgumentTypeError(f"{value} ist nicht erlaubt ({rng})")
        return v
    return conv


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Bereitet Immobilienfotos (JPG/JPEG/PNG) automatisch für ein Exposé auf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Beispiele:\n  python process_real_estate_photos.py ./input_photos\n"
               "  python process_real_estate_photos.py \"C:\\Users\\Ich\\Fotos Wohnung\" --compare\n"
               "Pfade mit Leerzeichen bitte in Anführungszeichen setzen.",
    )
    ap.add_argument("input", nargs="*",
                    help="Ordner (oder einzelnes Foto) mit den Originalen (Standard: ./input_photos)")
    ap.add_argument("-o", "--output", help=f"Ausgabeordner (Standard: <Eingabe>/{DEFAULT_OUTPUT_DIRNAME})")
    ap.add_argument("-q", "--quality", type=_ranged(int, 1, 100), default=92,
                    help="JPEG-Qualität 1-100 (Standard 92)")
    ap.add_argument("-r", "--recursive", action="store_true", help="auch Unterordner verarbeiten")
    ap.add_argument("-j", "--workers", type=_ranged(int, 1, 64), default=1,
                    help="parallele Prozesse (Standard 1; je Prozess ca. 1-2 GB RAM)")
    ap.add_argument("--compare", action="store_true",
                    help=f"zusätzlich Vorher/Nachher-Bilder in {DEFAULT_OUTPUT_DIRNAME}/{COMPARE_DIRNAME}/")
    ap.add_argument("--skip-existing", action="store_true",
                    help="bereits bearbeitete, seither unveränderte Fotos überspringen")
    ap.add_argument("--max-size", type=_ranged(int, 256), metavar="PX",
                    help="lange Kante höchstens PX Pixel (nur verkleinern, z. B. 3000)")
    ap.add_argument("--min-size", type=_ranged(int, 1), default=320, metavar="PX",
                    help="Bilder mit kürzerer Kante unter PX werden übersprungen (Standard 320)")
    ap.add_argument("--no-geometry", action="store_true", help="keine Objektiv-/Perspektivkorrektur")
    ap.add_argument("--no-lens", action="store_true", help="keine Objektivkorrektur")
    ap.add_argument("--lens-k", type=_ranged(float, -0.3, 0.3), metavar="K",
                    help="Verzeichnung manuell vorgeben (Divisionsmodell, z. B. -0.05 tonnenförmig)")
    ap.add_argument("--no-perspective", action="store_true", help="keine Horizont-/Senkrechtenkorrektur")
    ap.add_argument("--vertical-strength", type=_ranged(float, 0.0, 1.0), default=1.0, metavar="0..1",
                    help="Stärke der Senkrechtenkorrektur (1 = ganz gerade, Standard)")
    ap.add_argument("--max-crop", type=_ranged(float, 0.0, 0.3), metavar="ANTEIL",
                    help="max. Beschnitt je Bildseite durch die Geometriekorrektur "
                         "(Standard 0.10 = 10 %%; wenn gesetzt, gilt es auch fürs Ausrichten des Horizonts)")
    ap.add_argument("--focal35", type=_ranged(float, 8.0, 300.0), metavar="MM",
                    help="KB-Brennweite, falls nicht im EXIF (Standard 24; Ultraweitwinkel ≈ 13)")
    ap.add_argument("--no-denoise", action="store_true", help="keine Rauschreduzierung")
    ap.add_argument("--warmth", type=_ranged(float, -0.1, 0.1), default=0.015,
                    help="leichte Wärme des Looks (0 = neutral, Standard 0.015)")
    ap.add_argument("--strip-gps", action="store_true", help="GPS-Position aus EXIF und XMP entfernen")
    ap.add_argument("-v", "--verbose", action="store_true", help="alle Einzelentscheidungen anzeigen")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return ap


def settings_from_args(a) -> Settings:
    s = Settings()
    s.jpeg_quality = a.quality
    s.max_long_edge = a.max_size
    s.min_size = a.min_size
    s.compare = a.compare
    s.strip_gps = a.strip_gps
    s.denoise = not a.no_denoise
    s.lens = not (a.no_geometry or a.no_lens)
    s.lens_k = None if a.no_geometry else a.lens_k
    s.perspective = not (a.no_geometry or a.no_perspective)
    s.vertical_strength = a.vertical_strength
    s.focal35 = a.focal35
    if a.max_crop is not None:
        s.max_side_loss = a.max_crop
        s.max_side_loss_explicit = True
    s.warmth = a.warmth
    return s


def setup_logging(output_dir: Path, verbose: bool):
    try:  # Umlaute/Sonderzeichen dürfen auf Windows-Konsolen (cp1252/cp850) nie abstürzen
        sys.stdout.reconfigure(errors="replace")
    except (AttributeError, ValueError):
        pass
    log.setLevel(logging.DEBUG)
    log.handlers.clear()
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(console)
    fh = logging.FileHandler(output_dir / LOG_FILENAME, mode="a", encoding="utf-8", errors="backslashreplace")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(message)s"))
    log.addHandler(fh)


def _same_dir(a: Path, b: Path) -> bool:
    try:
        return os.path.samefile(a, b)
    except OSError:
        return a.resolve() == b.resolve()


def main(argv=None) -> int:
    ap = build_arg_parser()
    a = ap.parse_args(argv)
    parts = a.input or ["input_photos"]
    src = Path(" ".join(parts)).expanduser()
    if not src.exists():
        if len(parts) > 1 and any(Path(x).expanduser().is_file() for x in parts[1:]):
            sys.stderr.write("Bitte nur einen Ordner oder ein einzelnes Foto angeben "
                             "(bei mehreren Fotos den Ordner angeben).\n")
        elif len(parts) > 1 and Path(parts[0]).expanduser().exists():
            rest = " ".join(parts[1:])
            sys.stderr.write("Nur ein Eingabeordner möglich. Einen Ausgabeordner bitte mit -o angeben, "
                             f"z. B.: -o \"{rest}\"\n")
        elif len(parts) > 1:
            sys.stderr.write("Mehrere Eingaben erkannt. Pfade mit Leerzeichen bitte in "
                             f"Anführungszeichen setzen, z. B.: \"{' '.join(parts)}\"\n")
        else:
            sys.stderr.write(f"Eingabe nicht gefunden: {src}\n")
        return 2
    if src.is_file():
        input_root, single = src.parent, src
    else:
        input_root, single = src, None
    output_dir = Path(a.output).expanduser() if a.output else input_root / DEFAULT_OUTPUT_DIRNAME
    if output_dir.exists() and _same_dir(output_dir, input_root):
        sys.stderr.write("Der Ausgabeordner darf nicht der Eingabeordner sein "
                         "(Originale würden überschrieben).\n")
        return 2
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        sys.stderr.write(f"Ausgabeordner kann nicht angelegt werden: {exc}\n")
        return 2
    if _same_dir(output_dir, input_root):
        sys.stderr.write("Der Ausgabeordner darf nicht der Eingabeordner sein "
                         "(Originale würden überschrieben).\n")
        return 2
    # Vor dem ersten Schreibzugriff: alle Originale unter dem Eingabeordner merken
    input_ids = _all_input_ids(input_root, output_dir)
    try:
        setup_logging(output_dir, a.verbose)
    except OSError as exc:
        sys.stderr.write(f"Ausgabeordner ist nicht beschreibbar: {exc}\n")
        return 2
    s = settings_from_args(a)

    pruned: list = []
    unreadable: list = []
    if single is not None:
        if single.suffix.lower() not in SUPPORTED_EXTENSIONS:
            log.error("Nicht unterstützter Dateityp: %s", single.name)
            return 2
        files = [single]
    else:
        files = discover_images(input_root, output_dir, a.recursive, pruned, unreadable)

    log.info("=" * 72)
    log.info("Immobilienfotos für Exposé – v%s – %s", __version__, time.strftime("%Y-%m-%d %H:%M:%S"))
    log.info("Eingabe : %s", input_root.resolve())
    log.info("Ausgabe : %s", output_dir.resolve())
    for d in pruned:
        log.info("Ordner übersprungen (versteckt, System- oder Ausgabeordner): %s", d)
    for err in unreadable:
        log.warning("Ordner nicht lesbar (Zugriff verweigert?): %s", getattr(err, "filename", err))
    if not files:
        if single is None and not a.recursive and discover_images(input_root, output_dir, True):
            log.warning("Keine Bilder direkt in diesem Ordner, aber in Unterordnern. "
                        "Mit -r (--recursive) werden auch Unterordner verarbeitet.")
        else:
            log.warning("Keine JPG-/JPEG-/PNG-Dateien gefunden.")
        return 2
    log.info("%d Bild(er) gefunden.", len(files))

    jobs = plan_outputs(files, input_root, output_dir)
    originals = {p.resolve() for p in files}
    original_ids = input_ids | {i for i in (_file_id(p) for p in files) if i}
    manifest = _load_manifest(output_dir)
    signatures = {}
    counts = {"ok": 0, "skip": 0, "error": 0, "exists": 0, "blocked": 0}
    work = []
    for p, dst in jobs:
        rel_dst = dst.relative_to(output_dir).as_posix()
        try:
            blocked = _destination_problem(p, dst, rel_dst, originals, original_ids, manifest)
        except (OSError, RuntimeError) as exc:
            blocked = f"Zielpfad {dst} nicht prüfbar ({exc})"
        if blocked:
            log.error("BLOCKIERT %s: %s", p.name, blocked)
            counts["blocked"] += 1
            continue
        try:
            signatures[str(p)] = (rel_dst, _source_signature(p, input_root))
        except OSError:
            pass
        entry = manifest.get(rel_dst)
        if a.skip_existing and dst.exists() and str(p) in signatures and isinstance(entry, list) \
                and entry[:3] == signatures[str(p)][1] and (_matches_manifest(dst, entry) or _is_our_output(dst)):
            log.info("vorhanden  %s", rel_dst)
            counts["exists"] += 1
            continue
        cmp_dst = None
        if s.compare:
            rel = dst.relative_to(output_dir)
            cmp_dst = output_dir / COMPARE_DIRNAME / rel.with_name(dst.stem + "_vergleich.jpg")
            # Die Vergleichsbilder gehören zur eigenen Ausgabe: wird das Ergebnis neu
            # geschrieben, darf auch sein Vergleichsbild ersetzt werden.
            if cmp_dst.exists() and not dst.exists() and not _is_our_output(cmp_dst):
                log.warning("Vergleichsbild %s existiert bereits (fremde Datei) – wird nicht ersetzt", cmp_dst)
                cmp_dst = None
        work.append((str(p), str(dst), s, str(cmp_dst) if cmp_dst else None))

    workers = max(1, min(a.workers, len(work) or 1, 61 if os.name == "nt" else 64))
    threads = max(1, (os.cpu_count() or 2) // workers) if workers > 1 else 0
    t_start = time.time()

    def report(status, src_path, payload):
        name = Path(src_path).name
        counts[status] += 1
        if status == "ok":
            log.info("OK      %s", name)
            log.info("        %s", _summary_line(payload))
            for note in payload["notes"]:
                log.debug("        - %s", note)
            if src_path in signatures:
                rel_dst, sig = signatures[src_path]
                try:
                    st = (output_dir / rel_dst).stat()
                    manifest[rel_dst] = sig + [st.st_size, st.st_mtime_ns]
                    _save_manifest(output_dir, manifest)     # sofort: --skip-existing auch nach Abbruch
                except OSError:
                    pass
        elif status == "skip":
            log.warning("SKIP    %s: %s", name, payload)
        else:
            first = payload.splitlines()[0]
            log.error("FEHLER  %s: %s", name, first)
            log.debug(payload)

    manifest_before = dict(manifest)
    # Einträge, die in diesem Lauf neu geschrieben werden, vorübergehend auf die
    # Herkunft reduzieren: Bricht der Lauf ab oder scheitert ein Bild, nachdem das
    # Ergebnis schon ersetzt wurde, gilt die Datei sonst beim nächsten Lauf als
    # "nachbearbeitet". Unberührte Einträge werden am Ende wiederhergestellt.
    inflight = {}
    for job in work:
        rel = Path(job[1]).relative_to(output_dir).as_posix()
        entry = manifest.get(rel)
        if isinstance(entry, list) and len(entry) >= 5:
            inflight[rel] = entry
            manifest[rel] = entry[:3]
    if inflight:
        _save_manifest(output_dir, manifest)
    finished = True
    if workers == 1:
        try:
            for job in work:
                report(*_worker((*job, 0)))
        except KeyboardInterrupt:
            finished = False
    else:
        finished = _run_parallel(work, workers, threads, report)
    for rel, old in inflight.items():
        cur = manifest.get(rel)
        if isinstance(cur, list) and len(cur) < 5 and _matches_manifest(output_dir / rel, old):
            manifest[rel] = old
    if manifest != manifest_before:
        _save_manifest(output_dir, manifest)
    if not finished:
        log.warning("Abgebrochen durch Benutzer (Strg+C) – %d Bild(er) fertig.", counts["ok"])
        return 130

    log.info("-" * 72)
    extra = f", {counts['exists']} bereits vorhanden" if counts["exists"] else ""
    extra += f", {counts['blocked']} blockiert (Ziel nicht beschreibbar)" if counts["blocked"] else ""
    log.info("Fertig in %.1f s: %d verarbeitet, %d übersprungen, %d Fehler%s.",
             time.time() - t_start, counts["ok"], counts["skip"], counts["error"], extra)
    log.info("Ergebnisse: %s", output_dir.resolve())
    log.info("Protokoll : %s", (output_dir / LOG_FILENAME).resolve())
    return 1 if (counts["error"] or counts["blocked"] or unreadable) else 0


if __name__ == "__main__":
    sys.exit(main())
