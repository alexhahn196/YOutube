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
  2. Rauschen    Non-Local-Means, Stärke aus dem gemessenen Rauschen abgeleitet.
                 Läuft VOR der Geometrie, solange das Rauschen noch pixelgenau ist.
  3. Geometrie   Objektivverzeichnung (Plumb-Line-Schätzung), Horizont (Roll) und
                 stürzende Linien (Pitch) über den Fluchtpunkt der Senkrechten,
                 alles in EINEM Resampling-Schritt. Zuschnitt nur so weit, dass
                 keine leeren Ränder entstehen; Seitenverhältnis bleibt erhalten.
  4. Ton/Farbe   Weißabgleich (auf neutralen Flächen), Belichtung, Schatten
                 aufhellen / Lichter absenken (kantenerhaltend, moderat), Schwarz-
                 und Weißpunkt, sanfte S-Kurve, Dynamik (Vibrance) statt Sättigung.
  5. Schärfe     leichte Ausgabeschärfung, nur Helligkeit, mit Rauschschwelle.
  6. Speichern   JPEG (Qualität 92, 4:4:4), EXIF/XMP/Farbprofil übernommen.

Grundsatz: nur klassische fotografische Korrekturen. Es werden keine Bildinhalte
erzeugt, entfernt, retuschiert oder verschoben. Jede Korrektur, deren
automatische Schätzung unsicher ist, wird übersprungen statt geraten.
"""

from __future__ import annotations

import argparse
import io
import logging
import math
import os
import re
import sys
import tempfile
import time
import traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageCms, ImageOps
except ImportError as exc:  # pragma: no cover - reine Nutzerhilfe
    sys.stderr.write(
        f"Fehlende Bibliothek: {exc}\n"
        "Bitte zuerst installieren:  pip install -r requirements.txt\n"
    )
    sys.exit(2)

__version__ = "1.0.0"

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
DEFAULT_OUTPUT_DIRNAME = "output_expose"
LOG_FILENAME = "verarbeitung.log"
COMPARE_DIRNAME = "_vergleich"

# Schutz vor Dekompressionsbomben, aber groß genug für Panoramen.
Image.MAX_IMAGE_PIXELS = 250_000_000

LUMA_REC709 = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

log = logging.getLogger("expose")


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
    max_side_loss: float = 0.08              # max. Beschnitt je Bildseite
    min_keep_area: float = 0.75              # min. erhaltener Bildinhalt

    # Ton & Farbe (gleiche Zielwerte für alle Bilder = einheitlicher Look)
    wb_strength: float = 0.8                 # 0 = aus, 1 = voll neutralisieren
    wb_max_ratio: float = 1.25               # max. Verhältnis der Kanal-Faktoren
    warmth: float = 0.015                    # leicht warm = freundlich
    target_key_ev: float = -2.25             # Ziel-Mittelhelligkeit (log2, linear)
    max_ev_up: float = 1.3
    max_ev_down: float = 0.5
    shadow_compress: float = 0.72            # <1 hellt Schatten auf
    highlight_compress: float = 0.85         # <1 senkt Lichter
    max_shadow_lift_ev: float = 1.0
    max_highlight_cut_ev: float = 0.8
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


def _looks_gray(rgb: np.ndarray) -> bool:
    small, _ = resize_long_edge(rgb, 256)
    return float(np.abs(small - small.mean(axis=2, keepdims=True)).max()) < 2.0 / 255.0


def load_image(path: Path, settings: Settings) -> LoadedImage:
    notes: list = []
    with Image.open(path) as im:
        fmt = im.format
        if fmt not in ("JPEG", "MPO", "PNG"):
            raise SkipImage(f"Dateiinhalt ist {fmt or 'unbekannt'}, kein JPEG/PNG")
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
            elif fmt != "JPEG" or im.mode == "RGB":
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
        xmp=_xmp_reset_orientation(xmp),
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
    flat = mag <= np.percentile(mag, 50)
    return float(math.sqrt(math.pi / 2) * np.abs(resp[flat]).mean() / 6.0)


def denoise_image(img: np.ndarray, high_bit: bool, s: Settings):
    info = {"sigma": None, "h": None}
    if not s.denoise or s.denoise_strength <= 0:
        return img, info
    u8 = to_u8(img)
    sigma = estimate_noise_sigma(cv2.cvtColor(u8, cv2.COLOR_RGB2GRAY))
    info["sigma"] = round(sigma, 2)
    if sigma < 0.6:
        return img, info
    h_luma = float(np.clip(0.85 * sigma * s.denoise_strength, 1.0, 6.0))
    h_color = float(np.clip((1.5 * sigma + 2.0) * s.denoise_strength, 2.0, 10.0))
    info["h"] = round(h_luma, 2)
    if high_bit:
        # 16-Bit-Daten nicht auf 8 Bit quantisieren: sanfter bilateraler Filter.
        sig = h_luma / 255.0 * 3.0
        out = cv2.bilateralFilter(img, d=5, sigmaColor=sig, sigmaSpace=2.0)
        return np.clip(out, 0, 1).astype(np.float32), info
    search = 21 if u8.shape[0] * u8.shape[1] <= 6_000_000 else 15
    bgr = cv2.cvtColor(u8, cv2.COLOR_RGB2BGR)
    den = cv2.fastNlMeansDenoisingColored(bgr, None, h_luma, h_color, 7, search)
    return cv2.cvtColor(den, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0, info


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
    if abs(k_best) < 0.015:
        info["reason"] = "Verzeichnung vernachlässigbar"
        return 0.0, info
    if gain < 1.35:
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
    if vert.sum() >= 3:
        res = _vp_ransac(p1[vert], p2[vert], d[vert], length[vert])
    else:
        res = None

    if res is not None:
        v, inl, spread = res
        info["lines"] = int(inl.sum())
        tot_len = float(length[vert][inl].sum())
        enough = inl.sum() >= 4 and tot_len >= 0.5
        if enough:
            if spread >= 0.12:
                u = np.array([v[0] / f_n, v[1] / f_n, v[2]])
                info["mode"] = "Fluchtpunkt"
            else:  # Linien nur auf einer Seite: nur Roll, kein Pitch
                dd = d[vert][inl]
                dd = dd * np.sign(dd[:, 1:2] + 1e-12)
                mean = (dd * length[vert][inl][:, None]).sum(axis=0)
                u = np.array([mean[0], mean[1], 0.0])
                info["mode"] = "nur Horizont (Linien zu einseitig)"
            roll, pitch = _rotation_from_up(u)
            info.update(roll=math.degrees(roll), pitch=math.degrees(pitch))
            if abs(info["roll"]) > s.max_roll_deg:
                info["reason"] = f"Roll {info['roll']:.1f}° unplausibel groß"
                return info
            if abs(info["pitch"]) > s.max_pitch_deg:
                info["reason"] = f"Neigung {info['pitch']:.1f}° unplausibel groß"
                return info
            info["ok"] = True
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


def _vp_ransac(p1, p2, d, length, thr_deg: float = 1.2, iters: int = 600):
    n = len(p1)
    ones = np.ones((n, 1))
    lines = np.cross(np.hstack([p1, ones]), np.hstack([p2, ones]))
    lines /= np.hypot(lines[:, 0], lines[:, 1])[:, None]
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
        xm = min(max((x0 + x1) // 2, 0), w - 1)
        ym = min(max((y0 + y1) // 2, 0), h - 1)
        top = py[min(y0 + 1, h - 1), xm] / (src_h - 1)
        bottom = 1.0 - py[max(y1 - 2, 0), xm] / (src_h - 1)
        left = px[ym, min(x0 + 1, w - 1)] / (src_w - 1)
        right = 1.0 - px[ym, max(x1 - 2, 0)] / (src_w - 1)
        return max(0.0, float(top)), max(0.0, float(bottom)), max(0.0, float(left)), max(0.0, float(right))

    best_ok, best_any = None, None
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
            hw = lo - 1.5   # Sicherheitsabstand (Rasterquantisierung)
            b = bounds(cx, cy, hw)
            content = float(box_sum(ii_w, *b))
            losses = side_losses(*b)
            cand = (content, cx, cy, hw, losses)
            if best_any is None or content > best_any[0]:
                best_any = cand
            if max(losses) <= max_side_loss and (best_ok is None or content > best_ok[0]):
                best_ok = cand
    chosen = best_ok or best_any
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
        vinfo = estimate_verticals(small_u, f_n, s)
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

    # --- Plan: volle Korrektur, solange kein wichtiger Bildbereich verloren geht.
    # Sonst die Neigungskorrektur so weit abschwächen, dass der Beschnitt je
    # Bildseite im Limit bleibt (wie "Upright: Auto" in Lightroom).
    K = np.diag([f_n, f_n, 1.0])
    Kinv = np.linalg.inv(K)
    target_pitch = pitch * s.vertical_strength

    def attempt(factor):
        hm = K @ rotation_matrix(roll, target_pitch * factor) @ Kinv
        return factor, hm, plan_crop(w, h, k, hm, s.max_side_loss)

    def acceptable(plan):
        return plan is not None and plan["feasible"] and plan["retention"] >= s.min_keep_area

    chosen = attempt(1.0)
    if target_pitch and not acceptable(chosen[2]):
        best = attempt(0.0)
        lo, hi = 0.0, 1.0
        for _ in range(7):
            mid = 0.5 * (lo + hi)
            cand = attempt(mid)
            if acceptable(cand[2]):
                lo, best = mid, cand
            else:
                hi = mid
        chosen = best
    factor, Hm, plan = chosen
    p_eff = target_pitch * factor
    if abs(math.degrees(p_eff)) < 0.5 and p_eff:
        factor, Hm, plan = attempt(0.0)
        p_eff = 0.0
    # Horizont (Roll) und Objektiv allein kosten wenig Bild - nur bei extremem
    # Beschnitt wird auch darauf verzichtet.
    if plan is None or plan["retention"] < 0.65:
        info["notes"].append("Geometrie: Korrektur hätte zu viel Bild gekostet – übersprungen")
        return img, info
    if roll == 0 and p_eff == 0 and k == 0:
        return img, info

    if vinfo is not None and vinfo["ok"]:
        msg = (f"Senkrechten/Horizont: Roll {math.degrees(roll):+.2f}°, "
               f"Neigung {math.degrees(p_eff):+.2f}° ({vinfo['lines']} Linien, {vinfo['mode']}, {focal_note})")
        if pitch and factor < 0.999:
            msg += (f" – Neigung nur zu {factor:.0%} korrigiert "
                    f"(gemessen {math.degrees(pitch):+.1f}°), damit nichts Wichtiges abgeschnitten wird")
        info["notes"].append(msg)
    t, b, l, r = plan["losses"]
    info["notes"].append(f"Zuschnitt: oben {t:.0%}, unten {b:.0%}, links {l:.0%}, rechts {r:.0%}; "
                         f"{plan['retention']:.0%} des Bildinhalts erhalten")

    rect = plan["rect"]
    _, _, R = _norm_params(w, h)
    out_w = min(w, int(math.floor(rect[2] * R)))
    out_h = min(h, int(round(out_w * h / w)))
    img_out = _remap_normalized(img, k, Hm, rect, (out_w, out_h))
    info.update(roll=round(math.degrees(roll), 2), pitch=round(math.degrees(p_eff), 2),
                pitch_measured=round(math.degrees(pitch), 2), keep=round(plan["retention"], 3),
                applied=True)
    return np.clip(img_out, 0, 1).astype(np.float32), info


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
    """Graustufen-Annahme nur auf (nahezu) neutralen, hellen Flächen - iterativ.

    Wände, Decken, Fliesenfugen und Fassaden sind in Immobilienfotos fast immer
    neutral. Farbige Flächen (Holz, Ziegel, Himmel, Rasen) werden ausgeschlossen.
    """
    small, _ = resize_long_edge(lin, 600)
    px = small.reshape(-1, 3).astype(np.float64)
    Y = px @ LUMA_REC709.astype(np.float64)
    base = (Y > 0.03) & (px.max(axis=1) < 0.95)
    gains = np.ones(3)
    used = 0.0
    for thr in (20.0, 14.0, 10.0, 7.0):
        corr = np.clip(px * gains, 0, 1).astype(np.float32).reshape(1, -1, 3)
        lab = cv2.cvtColor(corr, cv2.COLOR_LRGB2Lab).reshape(-1, 3)
        chroma = np.hypot(lab[:, 1], lab[:, 2])
        m = base & (chroma < thr) & (lab[:, 0] > 30) & (lab[:, 0] < 98)
        if m.sum() < max(300, 0.02 * len(px)):
            break
        wts = (lab[m, 0] / 100.0) ** 2
        mean = (px[m] * wts[:, None]).sum(axis=0) / wts.sum()
        g = mean.mean() / np.maximum(mean, 1e-6)
        gains = g / float(g @ LUMA_REC709)
        used = float(m.mean())
    if used == 0.0:
        return np.ones(3, np.float32), {"skipped": "zu wenig neutrale Flächen"}

    gains = gains ** float(np.clip(s.wb_strength, 0, 1))
    # Sehr starke Farbstiche entstehen fast immer durch Mischlicht (Glühlampe +
    # Fenster). Voll neutralisiert würde das Tageslicht dann blau - daher die
    # Korrektur begrenzen; ein Rest Wärme wirkt ohnehin natürlich.
    ratio = float(gains.max() / gains.min())
    if ratio > s.wb_max_ratio:
        gains = gains ** (math.log(s.wb_max_ratio) / math.log(ratio))
    gains = gains * np.array([1 + s.warmth, 1.0, 1 - s.warmth])
    gains = gains / float(gains @ LUMA_REC709)
    return gains.astype(np.float32), {"gains": gains.round(3).tolist(), "neutral": round(used, 3)}


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
    return np.clip(lin * scale[:, :, None], 0, 1)


def local_tone_map(lin: np.ndarray, protect: np.ndarray, s: Settings):
    """Belichtung + Schatten/Lichter in log2-Luminanz (Basis/Detail-Zerlegung).

    Nur die großflächige Basis wird komprimiert, feine Details bleiben 1:1
    erhalten - so wirkt das Ergebnis nicht wie ein HDR-Foto."""
    h, w = lin.shape[:2]
    Y = luminance(lin)
    logY = np.log2(np.maximum(Y, 1.0 / 4096)).astype(np.float32)

    small, _ = resize_long_edge(logY, 512)
    lo, hi = np.percentile(small, [5, 95])
    key = float(small[(small >= lo) & (small <= hi)].mean())
    e = s.target_key_ev - key
    if e >= 0:
        e = min(e, s.max_ev_up)
    else:  # abdunkeln nur bei deutlich zu hellen Bildern und nur teilweise
        e = max(min(0.0, (e + 0.4) * 0.6), -s.max_ev_down)

    base = fast_guided_filter(logY, radius=int(0.03 * max(h, w)), eps=0.3)
    d = base + e - s.target_key_ev
    lift = s.max_shadow_lift_ev * np.tanh(np.maximum(-d, 0) * (1 - s.shadow_compress)
                                          / s.max_shadow_lift_ev)
    cut = s.max_highlight_cut_ev * np.tanh(np.maximum(d, 0) * (1 - s.highlight_compress)
                                           / s.max_highlight_cut_ev)
    gain = e + lift - cut
    gain = gain * (1 - protect) + np.maximum(gain, 0) * protect
    out = lin * np.exp2(gain)[:, :, None]
    out = highlight_shoulder(out)
    return out.astype(np.float32), {"key": round(key, 2), "ev": round(e, 2)}


def apply_levels(srgb: np.ndarray):
    """Schwarz- und Weißpunkt behutsam setzen (keine abgesoffenen Schatten)."""
    small, _ = resize_long_edge(srgb, 800)
    luma = small @ np.array([0.299, 0.587, 0.114], np.float32)
    lo, hi = np.percentile(luma, [0.5, 99.8])
    b = float(np.clip((lo - 0.015) / (1 - 0.015), 0.0, 0.05))
    g_min = 1.0 / (1.0 - b)
    g = float(max(g_min, min(0.975 / max(hi - b, 1e-3), 1.10)))
    return np.clip((srgb - b) * g, 0, 1), {"black": round(b, 3), "gain": round(g, 3)}


def finish_lab(srgb: np.ndarray, is_gray: bool, s: Settings) -> np.ndarray:
    """S-Kurve (Kontrast), Dynamik und Schärfung im Lab-Raum."""
    lab = cv2.cvtColor(srgb.astype(np.float32), cv2.COLOR_RGB2Lab)
    L = lab[:, :, 0] / 100.0
    c = s.contrast
    L = L + c * L * (1 - L) * (2 * L - 1)
    L = L * 100.0

    if not is_gray and s.vibrance:
        a, b = lab[:, :, 1], lab[:, :, 2]
        chroma = np.hypot(a, b)
        boost = s.vibrance * smoothstep(2.0, 10.0, chroma) * (1 - np.clip(chroma / 70.0, 0, 1)) ** 2
        lab[:, :, 1] = a * (1 + boost)
        lab[:, :, 2] = b * (1 + boost)

    if s.sharpen > 0:
        sigma = float(np.clip(max(L.shape) / 2400.0, 0.6, 1.6))
        detail = L - cv2.GaussianBlur(L, (0, 0), sigma)
        thr = 0.6
        detail = np.sign(detail) * np.maximum(np.abs(detail) - thr, 0)
        L = L + np.clip(0.55 * s.sharpen * detail, -5.0, 5.0)

    lab[:, :, 0] = np.clip(L, 0, 100)
    if is_gray:
        lab[:, :, 1:] = 0
    return np.clip(cv2.cvtColor(lab, cv2.COLOR_Lab2RGB), 0, 1)


def tone_and_color(srgb: np.ndarray, is_gray: bool, s: Settings):
    info = {}
    protect = highlight_protect_mask(srgb)
    lin = srgb_to_linear(srgb)
    if not is_gray and s.wb_strength > 0:
        gains, info["wb"] = estimate_white_balance(lin, s)
        # Ausgebrannte Lichter enthalten keine Farbinformation: dort den
        # Weißabgleich ausblenden, sonst werden weiße Reflexe blau/gelb.
        p = protect[:, :, None]
        lin = lin * (1.0 + (gains.reshape(1, 1, 3) - 1.0) * (1.0 - p))
    lin, info["tone"] = local_tone_map(lin, protect, s)
    out = linear_to_srgb(lin)
    out, info["levels"] = apply_levels(out)
    out = finish_lab(out, is_gray, s)
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
                  optimize=True, progressive=True)
    if loaded.icc_out and not loaded.is_gray:
        kwargs["icc_profile"] = loaded.icc_out
    exif = _exif_bytes(loaded.exif, im.size, notes)
    if exif:
        kwargs["exif"] = exif
    if loaded.xmp:
        kwargs["xmp"] = loaded.xmp
    if loaded.dpi:
        kwargs["dpi"] = tuple(int(round(float(v))) for v in loaded.dpi[:2])

    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".jpg", dir=str(dst.parent))
    os.close(fd)
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
    Image.fromarray(canvas, "RGB").save(dst, "JPEG", quality=88)


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
    img, geo = correct_geometry(img, loaded, s)
    notes.extend(geo["notes"])

    if s.max_long_edge and max(img.shape[:2]) > s.max_long_edge:
        img, _ = resize_long_edge(img, s.max_long_edge)
        notes.append(f"auf {s.max_long_edge} px lange Kante verkleinert")

    img, tone = tone_and_color(img, loaded.is_gray, s)
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
    parts = [f"{r['size_in'][0]}×{r['size_in'][1]} → {r['size_out'][0]}×{r['size_out'][1]}"]
    if r["noise"].get("h"):
        parts.append(f"Rauschen σ={r['noise']['sigma']} (h={r['noise']['h']})")
    g = r["geometry"]
    if g.get("applied"):
        parts.append(f"Geometrie Roll {g['roll']:+.2f}° Neigung {g['pitch']:+.2f}° "
                     f"k={g['k']:+.3f} Bildfläche {g['keep']:.0%}")
    wb = r["tone"].get("wb", {})
    if "gains" in wb:
        gr = wb["gains"]
        parts.append(f"WB R×{gr[0]:.3f} G×{gr[1]:.3f} B×{gr[2]:.3f}")
    parts.append(f"Belichtung {r['tone']['tone']['ev']:+.2f} EV")
    parts.append(f"{r['seconds']:.1f} s")
    return " | ".join(parts)


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
        return "error", src, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}"


# --------------------------------------------------------------------------- #
# Dateiauswahl und Hauptprogramm
# --------------------------------------------------------------------------- #

def discover_images(input_dir: Path, output_dir: Path, recursive: bool) -> list:
    out_res = output_dir.resolve()
    it = input_dir.rglob("*") if recursive else input_dir.iterdir()
    files = []
    for p in it:
        try:
            if not p.is_file():
                continue
        except OSError:
            continue
        if p.name.startswith("."):          # versteckt, macOS "._"-Dateien
            continue
        if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
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


def build_arg_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description="Bereitet Immobilienfotos (JPG/JPEG/PNG) automatisch für ein Exposé auf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Beispiel:\n  python process_real_estate_photos.py ./input_photos\n"
               "  python process_real_estate_photos.py ./input_photos --compare --workers 4",
    )
    ap.add_argument("input", nargs="?", default="input_photos",
                    help="Ordner mit den Originalfotos (Standard: ./input_photos)")
    ap.add_argument("-o", "--output", help=f"Ausgabeordner (Standard: <Eingabe>/{DEFAULT_OUTPUT_DIRNAME})")
    ap.add_argument("-q", "--quality", type=int, default=92, help="JPEG-Qualität 1-100 (Standard 92)")
    ap.add_argument("-r", "--recursive", action="store_true", help="auch Unterordner verarbeiten")
    ap.add_argument("-j", "--workers", type=int, default=1, help="parallele Prozesse (Standard 1)")
    ap.add_argument("--compare", action="store_true",
                    help=f"zusätzlich Vorher/Nachher-Bilder in {DEFAULT_OUTPUT_DIRNAME}/{COMPARE_DIRNAME}/")
    ap.add_argument("--skip-existing", action="store_true", help="bereits vorhandene Ausgaben überspringen")
    ap.add_argument("--max-size", type=int, metavar="PX",
                    help="lange Kante höchstens PX Pixel (nur verkleinern, z. B. 3000)")
    ap.add_argument("--min-size", type=int, default=320, metavar="PX",
                    help="Bilder mit kürzerer Kante unter PX werden übersprungen (Standard 320)")
    ap.add_argument("--no-geometry", action="store_true", help="keine Objektiv-/Perspektivkorrektur")
    ap.add_argument("--no-lens", action="store_true", help="keine Objektivkorrektur")
    ap.add_argument("--lens-k", type=float, metavar="K",
                    help="Verzeichnung manuell vorgeben (Divisionsmodell, z. B. -0.05 tonnenförmig)")
    ap.add_argument("--no-perspective", action="store_true", help="keine Horizont-/Senkrechtenkorrektur")
    ap.add_argument("--vertical-strength", type=float, default=1.0, metavar="0..1",
                    help="Stärke der Senkrechtenkorrektur (1 = ganz gerade, Standard)")
    ap.add_argument("--max-crop", type=float, default=0.08, metavar="ANTEIL",
                    help="max. Beschnitt je Bildseite durch die Geometriekorrektur (Standard 0.08 = 8 %%)")
    ap.add_argument("--focal35", type=float, metavar="MM",
                    help="KB-Brennweite, falls nicht im EXIF (Standard 24; Ultraweitwinkel ≈ 13)")
    ap.add_argument("--no-denoise", action="store_true", help="keine Rauschreduzierung")
    ap.add_argument("--warmth", type=float, default=0.015,
                    help="leichte Wärme des Looks (0 = neutral, Standard 0.015)")
    ap.add_argument("--strip-gps", action="store_true", help="GPS-Daten aus den EXIF-Daten entfernen")
    ap.add_argument("-v", "--verbose", action="store_true", help="ausführliche Ausgabe")
    ap.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return ap


def settings_from_args(a) -> Settings:
    s = Settings()
    s.jpeg_quality = int(np.clip(a.quality, 1, 100))
    s.max_long_edge = a.max_size
    s.min_size = a.min_size
    s.compare = a.compare
    s.strip_gps = a.strip_gps
    s.denoise = not a.no_denoise
    s.lens = not (a.no_geometry or a.no_lens)
    s.lens_k = None if a.no_geometry else a.lens_k
    s.perspective = not (a.no_geometry or a.no_perspective)
    s.vertical_strength = float(np.clip(a.vertical_strength, 0.0, 1.0))
    s.focal35 = a.focal35
    s.max_side_loss = float(np.clip(a.max_crop, 0.0, 0.3))
    s.warmth = float(np.clip(a.warmth, -0.1, 0.1))
    return s


def setup_logging(output_dir: Path, verbose: bool):
    log.setLevel(logging.DEBUG)
    log.handlers.clear()
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.DEBUG if verbose else logging.INFO)
    console.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(console)
    fh = logging.FileHandler(output_dir / LOG_FILENAME, mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)-7s %(message)s"))
    log.addHandler(fh)


def main(argv=None) -> int:
    a = build_arg_parser().parse_args(argv)
    src = Path(a.input).expanduser()
    if not src.exists():
        sys.stderr.write(f"Eingabe nicht gefunden: {src}\n")
        return 2
    if src.is_file():
        input_root, single = src.parent, src
    else:
        input_root, single = src, None
    output_dir = Path(a.output).expanduser() if a.output else input_root / DEFAULT_OUTPUT_DIRNAME
    if output_dir.resolve() == input_root.resolve():
        sys.stderr.write("Der Ausgabeordner darf nicht der Eingabeordner sein "
                         "(Originale würden überschrieben).\n")
        return 2
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        sys.stderr.write(f"Ausgabeordner kann nicht angelegt werden: {exc}\n")
        return 2
    setup_logging(output_dir, a.verbose)
    s = settings_from_args(a)

    if single is not None:
        if single.suffix.lower() not in SUPPORTED_EXTENSIONS:
            log.error("Nicht unterstützter Dateityp: %s", single.name)
            return 2
        files = [single]
    else:
        files = discover_images(input_root, output_dir, a.recursive)

    log.info("=" * 72)
    log.info("Immobilienfotos für Exposé – v%s – %s", __version__, time.strftime("%Y-%m-%d %H:%M:%S"))
    log.info("Eingabe : %s", input_root.resolve())
    log.info("Ausgabe : %s", output_dir.resolve())
    if not files:
        log.warning("Keine JPG-/JPEG-/PNG-Dateien gefunden.")
        return 2
    log.info("%d Bild(er) gefunden.", len(files))

    jobs = plan_outputs(files, input_root, output_dir)
    originals = {p.resolve() for p in files}
    work = []
    for p, dst in jobs:
        if dst.resolve() in originals:   # doppelte Absicherung: niemals Originale überschreiben
            log.error("ÜBERSPRUNGEN %s: Ziel wäre eine Originaldatei", p.name)
            continue
        if a.skip_existing and dst.exists():
            log.info("vorhanden  %s", dst.name)
            continue
        cmp_dst = None
        if s.compare:
            rel = dst.relative_to(output_dir)
            cmp_dst = output_dir / COMPARE_DIRNAME / rel.with_name(dst.stem + "_vergleich.jpg")
        work.append((str(p), str(dst), s, str(cmp_dst) if cmp_dst else None))

    workers = max(1, int(a.workers))
    threads = max(1, (os.cpu_count() or 2) // workers) if workers > 1 else 0
    counts = {"ok": 0, "skip": 0, "error": 0}
    t_start = time.time()

    def report(status, src_path, payload):
        name = Path(src_path).name
        counts[status] += 1
        if status == "ok":
            log.info("OK      %s", name)
            log.info("        %s", _summary_line(payload))
            for note in payload["notes"]:
                log.debug("        - %s", note)
        elif status == "skip":
            log.warning("SKIP    %s: %s", name, payload)
        else:
            first = payload.splitlines()[0]
            log.error("FEHLER  %s: %s", name, first)
            log.debug(payload)

    if workers == 1:
        for job in work:
            report(*_worker((*job, 0)))
    else:
        with ProcessPoolExecutor(max_workers=workers) as ex:
            futs = [ex.submit(_worker, (*job, threads)) for job in work]
            for fut in as_completed(futs):
                try:
                    report(*fut.result())
                except Exception as exc:  # z. B. abgestürzter Prozess
                    counts["error"] += 1
                    log.error("FEHLER  Prozess abgebrochen: %s", exc)

    log.info("-" * 72)
    log.info("Fertig in %.1f s: %d verarbeitet, %d übersprungen, %d Fehler.",
             time.time() - t_start, counts["ok"], counts["skip"], counts["error"])
    log.info("Ergebnisse: %s   Protokoll: %s", output_dir.resolve(), (output_dir / LOG_FILENAME).resolve())
    return 1 if counts["error"] else 0


if __name__ == "__main__":
    sys.exit(main())
