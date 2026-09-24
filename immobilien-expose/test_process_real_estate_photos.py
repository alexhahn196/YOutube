"""Tests für process_real_estate_photos.py  –  Aufruf:  python -m pytest -q"""
import hashlib
import os
import math
import sys
from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parent))
import process_real_estate_photos as P  # noqa: E402


# --------------------------------------------------------------------------- #
# Hilfen
# --------------------------------------------------------------------------- #

def synthetic_room(w=1200, h=900, seed=0):
    """Wandfläche mit Rauschen, senkrechten Kanten (Zargen) und waagrechten Leisten."""
    rng = np.random.default_rng(seed)
    img = np.clip(190 + rng.normal(0, 3, (h, w, 3)), 0, 255).astype(np.uint8)
    for x in range(90, w - 50, 140):
        cv2.line(img, (x, 0), (x, h - 1), (70, 55, 40), 4, cv2.LINE_AA)
    for y in range(110, h - 50, 170):
        cv2.line(img, (0, y), (w - 1, y), (110, 110, 110), 3, cv2.LINE_AA)
    return img


def vertical_tilt_deg(gray):
    """Längengewichteter mittlerer Winkel fast senkrechter Segmente (0 = lotrecht)."""
    seg = P._find_segments(gray, min_len=0.1 * max(gray.shape))
    d = seg[:, 2:4] - seg[:, 0:2]
    d *= np.sign(d[:, 1:2] + 1e-12)
    ang = np.degrees(np.arctan2(d[:, 0], d[:, 1]))
    length = np.hypot(d[:, 0], d[:, 1])
    m = np.abs(ang) < 20
    assert m.sum() >= 3
    return float((ang[m] * length[m]).sum() / length[m].sum())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def loaded_from(arr):
    return P.LoadedImage(rgb=arr.astype(np.float32) / 255.0, is_gray=False, high_bit_depth=False,
                         exif=None, xmp=None, icc_out=None, dpi=None, focal35=None)


# --------------------------------------------------------------------------- #
# Einzelbausteine
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("orientation", range(1, 9))
def test_orientation_matches_pillow(orientation, tmp_path):
    base = np.arange(6 * 4 * 3, dtype=np.uint8).reshape(4, 6, 3) * 3
    exif = Image.Exif()
    exif[0x0112] = orientation
    path = tmp_path / "o.png"
    Image.fromarray(base).save(path, exif=exif)
    with Image.open(path) as im:
        expected = np.asarray(ImageOps.exif_transpose(im))
    assert np.array_equal(P.apply_orientation(base, orientation), expected)


def test_distortion_inverse_roundtrip():
    rng = np.random.default_rng(1)
    pd = rng.uniform(-0.8, 0.8, (500, 2))
    for k in (-0.15, -0.05, 0.05):
        pu = P.undistort_points(pd, k)
        dx, dy, ok = P.distort_points(pu[:, 0], pu[:, 1], k)
        assert ok.all()
        assert np.allclose(np.stack([dx, dy], 1), pd, atol=1e-9)


def test_noise_estimate_is_calibrated():
    rng = np.random.default_rng(2)
    flat = np.full((600, 800), 128.0)
    for sigma in (2.0, 5.0):
        noisy = np.clip(flat + rng.normal(0, sigma, flat.shape), 0, 255).astype(np.uint8)
        assert abs(P.estimate_noise_sigma(noisy) - sigma) < 0.35 * sigma


def test_straight_image_is_not_touched():
    img = synthetic_room()
    out, info = P.correct_geometry(img.astype(np.float32) / 255, loaded_from(img), P.Settings())
    assert not info["applied"]
    assert out.shape == img.shape


@pytest.mark.parametrize("angle", [-3.0, 2.0])
def test_tilted_horizon_is_levelled(angle):
    img = synthetic_room(1400, 1050)
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D(((w - 1) / 2, (h - 1) / 2), angle, 1.25)   # zoom: keine Ecken
    tilted = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    before = vertical_tilt_deg(cv2.cvtColor(tilted, cv2.COLOR_RGB2GRAY))
    assert abs(before) > 1.5
    out, info = P.correct_geometry(tilted.astype(np.float32) / 255, loaded_from(tilted), P.Settings())
    assert info["applied"]
    after = vertical_tilt_deg(cv2.cvtColor(P.to_u8(out), cv2.COLOR_RGB2GRAY))
    assert abs(after) < 0.3, (before, after)
    assert out.shape[0] <= h and out.shape[1] <= w


def test_converging_verticals_are_straightened():
    img = synthetic_room(1400, 1050)
    h, w = img.shape[:2]
    cx, cy, R = P._norm_params(w, h)
    f_n = 2 * 24 / 43.27
    K = np.diag([f_n, f_n, 1.0])
    Hn = K @ P.rotation_matrix(0.0, math.radians(-8)) @ np.linalg.inv(K)   # Kamera nach unten geneigt
    S = np.array([[1 / R, 0, -cx / R], [0, 1 / R, -cy / R], [0, 0, 1]])
    Hpx = np.linalg.inv(S) @ np.linalg.inv(Hn) @ S
    keystoned = cv2.warpPerspective(img, Hpx, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    s = P.Settings()
    s.lens = False
    out, info = P.correct_geometry(keystoned.astype(np.float32) / 255, loaded_from(keystoned), s)
    assert info["applied"] and abs(info["pitch"]) > 3
    # Senkrechten links und rechts müssen danach parallel sein
    gray = cv2.cvtColor(P.to_u8(out), cv2.COLOR_RGB2GRAY)
    left = vertical_tilt_deg(gray[:, : gray.shape[1] // 3])
    right = vertical_tilt_deg(gray[:, 2 * gray.shape[1] // 3:])
    assert abs(left - right) < 0.8, (left, right)


def synthetic_frames(w=1400, h=1050, seed=4):
    """Wand mit Türzargen und Fensterrahmen: lange, nicht kreuzende Kanten auch am Bildrand."""
    rng = np.random.default_rng(seed)
    img = np.clip(185 + rng.normal(0, 3, (h, w, 3)), 0, 255).astype(np.uint8)
    for x in (40, 70, w - 70, w - 40, w // 2 - 200, w // 2 + 200):
        cv2.line(img, (x, 30), (x, h - 30), (60, 45, 30), 5, cv2.LINE_AA)
    for y in (40, 70, h - 70, h - 40):
        cv2.line(img, (120, y), (w - 120, y), (95, 95, 95), 4, cv2.LINE_AA)
    return img


def simulate_barrel(img, k):
    h, w = img.shape[:2]
    cx, cy, R = P._norm_params(w, h)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    pu = P.undistort_points(np.stack([(xx - cx) / R, (yy - cy) / R], -1), k)
    return cv2.remap(img, (pu[..., 0] * R + cx).astype(np.float32), (pu[..., 1] * R + cy).astype(np.float32),
                     cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)


@pytest.mark.parametrize("k_true", [-0.05, -0.10])
def test_lens_distortion_is_recovered(k_true):
    gray = cv2.cvtColor(simulate_barrel(synthetic_frames(), k_true), cv2.COLOR_RGB2GRAY)
    k, info = P.estimate_lens_distortion(P.resize_long_edge(gray, 1200)[0])
    assert abs(k - k_true) < 0.015, info


def test_no_lens_correction_without_distortion():
    gray = cv2.cvtColor(synthetic_frames(), cv2.COLOR_RGB2GRAY)
    k, info = P.estimate_lens_distortion(P.resize_long_edge(gray, 1200)[0])
    assert k == 0.0, info


def test_tone_keeps_range_and_no_nan():
    rng = np.random.default_rng(3)
    img = rng.uniform(0, 1, (300, 400, 3)).astype(np.float32)
    for scale in (0.05, 1.0):
        out, _ = P.tone_and_color(img * scale, False, P.Settings())
        assert np.isfinite(out).all() and out.min() >= 0 and out.max() <= 1


def test_clipped_white_stays_neutral_under_color_cast():
    img = np.zeros((400, 600, 3), np.float32)
    img[:] = (0.75, 0.62, 0.45)                 # warmer Wandton (Glühlampe)
    img[150:250, 250:350] = 1.0                 # ausgebranntes Fenster
    out, _ = P.tone_and_color(img, False, P.Settings())
    win = out[180:220, 280:320].reshape(-1, 3).mean(0)
    assert win.min() > 0.97 and win.max() - win.min() < 0.02


# --------------------------------------------------------------------------- #
# Ende-zu-Ende über die Kommandozeile
# --------------------------------------------------------------------------- #

@pytest.fixture()
def photo_dir(tmp_path):
    d = tmp_path / "fotos"
    d.mkdir()
    room = synthetic_room(900, 600)
    exif = Image.Exif()
    exif[0x0112] = 6
    exif[0x010F] = "TestKamera"
    exif.get_ifd(0x8769)[0x9003] = "2026:09:24 10:00:00"
    exif.get_ifd(0x8825)[1] = "N"
    Image.fromarray(room).save(d / "wohnzimmer.jpg", quality=95, exif=exif)
    rgba = np.dstack([room, np.full(room.shape[:2], 255, np.uint8)])
    rgba[:50, :50, 3] = 0
    Image.fromarray(rgba, "RGBA").save(d / "grundriss.png")
    Image.fromarray(room).save(d / "wohnzimmer.png")                  # Namenskonflikt
    Image.fromarray(room[:100, :100]).save(d / "winzig.jpg")          # zu klein
    (d / "kaputt.jpg").write_bytes(b"\xff\xd8\xff\xe0 kein echtes jpeg")
    (d / "._wohnzimmer.jpg").write_bytes(b"macos resource fork")
    (d / "notiz.txt").write_text("keine Bilddatei")
    return d


def test_cli_end_to_end(photo_dir):
    before = {p.name: sha(p) for p in photo_dir.iterdir()}
    rc = P.main([str(photo_dir)])
    out = photo_dir / "output_expose"
    assert rc == 1                                            # kaputt.jpg -> Fehler, Rest läuft
    assert {p.name: sha(p) for p in photo_dir.iterdir() if p.is_file()} == before
    names = sorted(p.name for p in out.glob("*.jpg"))
    assert names == ["grundriss.jpg", "wohnzimmer.jpg", "wohnzimmer_png.jpg"]

    with Image.open(out / "wohnzimmer.jpg") as im:
        assert im.format == "JPEG"
        assert im.size[0] <= 600 and im.size[1] <= 900        # hochkant gedreht, nie größer
        assert im.size[1] > im.size[0]
        ex = im.getexif()
        assert ex.get(0x0112) == 1
        assert ex.get(0x010F) == "TestKamera"
        assert ex.get_ifd(0x8769).get(0x9003) == "2026:09:24 10:00:00"
        assert ex.get_ifd(0x8825).get(1) == "N"
    with Image.open(out / "grundriss.jpg") as im:
        assert im.getpixel((5, 5)) == pytest.approx((255, 255, 255), abs=6)   # Transparenz -> weiß

    log = (out / "verarbeitung.log").read_text(encoding="utf-8")
    assert "kaputt.jpg" in log and "winzig.jpg" in log
    assert "._wohnzimmer" not in log


def test_strip_gps(photo_dir):
    P.main([str(photo_dir), "--strip-gps", "--no-geometry"])
    with Image.open(photo_dir / "output_expose" / "wohnzimmer.jpg") as im:
        assert 0x8825 not in im.getexif()


def test_output_equal_to_input_is_refused(photo_dir):
    assert P.main([str(photo_dir), "-o", str(photo_dir)]) == 2


def test_missing_input_folder(tmp_path):
    assert P.main([str(tmp_path / "gibt_es_nicht")]) == 2


# --------------------------------------------------------------------------- #
# Regressionen aus dem Review
# --------------------------------------------------------------------------- #

def test_denoise_keeps_fine_cracks():
    rng = np.random.default_rng(5)
    wall = np.full((400, 600), 200.0)
    wall[:, 300] -= 8                                      # 1 px feiner Riss
    wall[150:162, 100:112] -= 12                           # kleiner Fleck
    noisy = np.clip(wall + rng.normal(0, 4, wall.shape), 0, 255)
    img = np.dstack([noisy] * 3).astype(np.float32) / 255
    out, info = P.denoise_image(img, False, P.Settings())
    assert info["sigma"] > 2
    g = out[..., 1] * 255
    crack = g[:, 300].mean() - 0.5 * (g[:, 295].mean() + g[:, 305].mean())
    stain = g[150:162, 100:112].mean() - g[150:162, 130:142].mean()
    assert crack < -5 and stain < -9, (crack, stain)


def test_one_sided_verticals_do_not_cause_roll():
    img = np.full((1050, 1400, 3), 190, np.uint8)
    for x in (1150, 1220, 1290):                           # Zargen nur am rechten Rand
        cv2.line(img, (x, 0), (x, 1049), (60, 45, 30), 4, cv2.LINE_AA)
    h, w = img.shape[:2]
    cx, cy, R = P._norm_params(w, h)
    f_n = 2 * 24 / 43.27
    K = np.diag([f_n, f_n, 1.0])
    Hn = K @ P.rotation_matrix(0.0, math.radians(-8)) @ np.linalg.inv(K)
    S = np.array([[1 / R, 0, -cx / R], [0, 1 / R, -cy / R], [0, 0, 1]])
    keystoned = cv2.warpPerspective(img, np.linalg.inv(S) @ np.linalg.inv(Hn) @ S, (w, h),
                                    flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    s = P.Settings()
    s.lens = False
    _, info = P.correct_geometry(keystoned.astype(np.float32) / 255, loaded_from(keystoned), s)
    assert info["roll"] == 0.0


def test_mixed_light_daylight_patch_not_pushed_blue():
    img = np.zeros((400, 600, 3), np.float32)
    img[:] = (0.80, 0.72, 0.62)                            # Kunstlicht-Wand
    img[150:250, 250:350] = (0.64, 0.69, 0.76)              # Tageslicht-Reflex, schon kühl
    lab_in = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)
    out, info = P.tone_and_color(img, False, P.Settings())
    assert info["wb"]["gains"][2] > info["wb"]["gains"][0]  # Stich wird gekühlt
    lab_out = cv2.cvtColor(out.astype(np.float32), cv2.COLOR_RGB2Lab)
    assert lab_out[200, 300, 2] > lab_in[200, 300, 2] - 3   # Reflex nicht deutlich blauer


def test_blue_sky_does_not_clip_blue_channel():
    img = np.zeros((600, 800, 3), np.float32)
    ramp = np.linspace(0.55, 0.75, 300)[:, None]
    img[:300] = np.dstack([ramp * 0.45, ramp * 0.75, ramp * 1.0 + 0 * ramp])   # blauer Himmel
    img[300:] = (0.18, 0.16, 0.14)                          # dunkle Häuser
    out, _ = P.tone_and_color(img, False, P.Settings())
    assert (out[:300, :, 2] >= 254 / 255).mean() < 0.02


def test_bright_white_room_is_not_darkened():
    rng = np.random.default_rng(6)
    img = np.clip(0.80 + rng.normal(0, 0.01, (400, 600, 3)), 0, 1).astype(np.float32)
    img[300:] = 0.45                                        # Boden
    L_in = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)[:300, :, 0].mean()
    out, _ = P.tone_and_color(img, False, P.Settings())
    L_out = cv2.cvtColor(out.astype(np.float32), cv2.COLOR_RGB2Lab)[:300, :, 0].mean()
    assert L_out >= L_in - 1.0, (L_in, L_out)


def _write(p, arr=None, **kw):
    Image.fromarray(synthetic_room(800, 600) if arr is None else arr).save(p, **kw)


def test_hardlinked_output_never_overwrites_original(tmp_path):
    src = tmp_path / "in"
    out = tmp_path / "out"
    src.mkdir()
    out.mkdir()
    _write(src / "foto.jpg", quality=95)
    os.link(src / "foto.jpg", out / "foto.jpg")             # Ziel = dieselbe Datei
    before = sha(src / "foto.jpg")
    P.main([str(src), "-o", str(out), "--no-geometry"])
    assert sha(src / "foto.jpg") == before


def test_symlinked_output_equal_to_input_is_refused(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _write(src / "foto.jpg")
    (tmp_path / "alias").symlink_to(src, target_is_directory=True)
    assert P.main([str(src), "-o", str(tmp_path / "alias")]) == 2


def test_output_in_parent_folder_works(tmp_path):
    src = tmp_path / "fotos"
    src.mkdir()
    _write(src / "foto.jpg")
    assert P.main([str(src), "-o", str(tmp_path), "--no-geometry"]) == 0
    assert (tmp_path / "foto.jpg").exists()


def test_recursive_skips_previous_outputs_and_hidden_folders(tmp_path):
    src = tmp_path / "fotos"
    (src / "Wohnzimmer").mkdir(parents=True)
    (src / ".thumbnails").mkdir()
    (src / "@eaDir").mkdir()
    _write(src / "a.jpg")
    _write(src / "Wohnzimmer" / "b.jpg")
    _write(src / ".thumbnails" / "c.jpg")
    _write(src / "@eaDir" / "d.jpg")
    assert P.main([str(src), "--compare", "--no-geometry"]) == 0     # erzeugt output_expose/
    (src / "export").mkdir()                                           # Ausgabe eines früheren Laufs mit -o
    _write(src / "export" / "x.jpg")
    P._save_manifest(src / "export", {"x.jpg": ["x.jpg", 1, 1, 1, 1]})
    (src / "nur_protokoll").mkdir()                                     # nur ein Protokoll: KEIN Ausgabeordner
    _write(src / "nur_protokoll" / "y.jpg")
    (src / "nur_protokoll" / P.LOG_FILENAME).write_text("Lauf ohne Ergebnis")
    found = P.discover_images(src, tmp_path / "neu", True)
    assert sorted(p.name for p in found) == ["a.jpg", "b.jpg", "y.jpg"]


def test_subfolder_hint_when_no_top_level_images(tmp_path, caplog):
    src = tmp_path / "fotos"
    (src / "sub").mkdir(parents=True)
    _write(src / "sub" / "a.jpg")
    assert P.main([str(src)]) == 2
    assert "-r" in (src / "output_expose" / P.LOG_FILENAME).read_text(encoding="utf-8")


def test_skip_existing_uses_source_signature(tmp_path):
    src = tmp_path / "fotos"
    src.mkdir()
    _write(src / "foto.jpg")
    out = src / "output_expose"
    assert P.main([str(src), "--no-geometry"]) == 0
    first = (out / "foto.jpg").stat().st_mtime_ns
    assert P.main([str(src), "--no-geometry", "--skip-existing"]) == 0
    assert (out / "foto.jpg").stat().st_mtime_ns == first            # übersprungen
    _write(src / "foto.jpg", synthetic_room(800, 600, seed=9))        # Original geändert
    os.utime(src / "foto.jpg", ns=(first + 10**9, first + 10**9))
    assert P.main([str(src), "--no-geometry", "--skip-existing"]) == 0
    assert (out / "foto.jpg").stat().st_mtime_ns != first            # neu bearbeitet


@pytest.mark.parametrize("args", [["--max-size", "-1"], ["-j", "0"], ["-q", "150"], ["--max-crop", "2"]])
def test_invalid_cli_values_are_rejected(tmp_path, args):
    with pytest.raises(SystemExit) as exc:
        P.main([str(tmp_path)] + args)
    assert exc.value.code == 2


def test_oversized_xmp_is_dropped_not_fatal(tmp_path):
    src = tmp_path / "fotos"
    src.mkdir()
    from PIL import PngImagePlugin
    meta = PngImagePlugin.PngInfo()
    meta.add_itxt("XML:com.adobe.xmp", "<x:xmpmeta>" + "A" * 120_000 + "</x:xmpmeta>")
    Image.fromarray(synthetic_room(800, 600)).save(src / "gross.png", pnginfo=meta)
    assert P.main([str(src), "--no-geometry"]) == 0
    assert (src / "output_expose" / "gross.jpg").exists()


def test_strip_gps_also_cleans_xmp(tmp_path):
    src = tmp_path / "fotos"
    src.mkdir()
    xmp = (b'<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
           b'<rdf:Description xmlns:exif="http://ns.adobe.com/exif/1.0/" exif:GPSLatitude="52,31.2N" '
           b'exif:GPSLongitude="13,24.6E" exif:ExposureTime="1/60"/></rdf:RDF></x:xmpmeta>')
    _write(src / "foto.jpg", xmp=xmp)
    P.main([str(src), "--no-geometry", "--strip-gps"])
    with Image.open(src / "output_expose" / "foto.jpg") as im:
        out_xmp = im.info.get("xmp", b"")
    assert b"GPS" not in out_xmp and b"ExposureTime" in out_xmp


@pytest.mark.skipif(os.name == "nt", reason="POSIX-Dateirechte")
def test_output_files_are_readable_by_others(tmp_path):
    src = tmp_path / "fotos"
    src.mkdir()
    _write(src / "foto.jpg")
    old = os.umask(0o022)
    try:
        P.main([str(src), "--no-geometry"])
    finally:
        os.umask(old)
    assert (src / "output_expose" / "foto.jpg").stat().st_mode & 0o044 == 0o044


def test_strong_uniform_tungsten_cast_is_reduced():
    img = np.zeros((400, 600, 3), np.float32)
    img[:] = (0.80, 0.66, 0.50)                            # kräftig orange, keine neutrale Fläche
    img[300:] = (0.45, 0.36, 0.27)
    def warmth(x):   # Gelbanteil relativ zur Helligkeit (Aufhellen allein ändert ihn nicht)
        lab = cv2.cvtColor(x.astype(np.float32), cv2.COLOR_RGB2Lab)[:300]
        return float(lab[..., 2].mean() / (lab[..., 0].mean() + 16))
    out, info = P.tone_and_color(img, False, P.Settings())
    assert info["wb"].get("uniform_cast", 0) > 0.5
    # bewusst nur teilweise: sonst würden cremefarbene Wände grau (Obergrenze 1.45)
    assert warmth(out) < 0.80 * warmth(img), (warmth(img), warmth(out))


# --------------------------------------------------------------------------- #
# Regressionen aus Review-Runde 2
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("recursive", [True, False])
def test_output_into_input_subfolder_never_overwrites_originals(tmp_path, recursive):
    src = tmp_path / "in"
    (src / "sub").mkdir(parents=True)
    _write(src / "foto.jpg", synthetic_room(800, 600, seed=1))
    _write(src / "sub" / "foto.jpg", synthetic_room(900, 700, seed=2))
    before = sha(src / "sub" / "foto.jpg")
    args = [str(src), "-o", str(src / "sub"), "--no-geometry"] + (["-r"] if recursive else [])
    P.main(args)
    assert sha(src / "sub" / "foto.jpg") == before


def test_foreign_file_in_output_is_not_overwritten(tmp_path):
    src = tmp_path / "in"
    out = tmp_path / "out"
    src.mkdir()
    out.mkdir()
    _write(src / "foto.jpg")
    _write(out / "foto.jpg", synthetic_room(640, 480, seed=3))          # gehört dem Nutzer
    before = sha(out / "foto.jpg")
    P.main([str(src), "-o", str(out), "--no-geometry"])
    assert sha(out / "foto.jpg") == before


def test_own_previous_output_is_overwritten(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _write(src / "foto.jpg")
    assert P.main([str(src), "--no-geometry"]) == 0
    (src / "output_expose" / P.MANIFEST_NAME).unlink()                   # auch ohne Manifest erkennbar
    first = (src / "output_expose" / "foto.jpg").stat().st_mtime_ns
    assert P.main([str(src), "--no-geometry"]) == 0
    assert (src / "output_expose" / "foto.jpg").stat().st_mtime_ns != first


@pytest.mark.skipif(os.name == "nt", reason="Byte-Dateinamen nur unter POSIX")
def test_non_utf8_filename_keeps_manifest_working(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    name = os.fsdecode(b"K\xfcche.jpg")
    _write(src / name)
    assert P.main([str(src), "--no-geometry"]) == 0
    assert P._load_manifest(src / "output_expose")                       # gültig und nicht leer
    assert not (src / "output_expose" / (P.MANIFEST_NAME + ".tmp")).exists()


def test_recursive_keeps_user_folders_with_hash_or_at(tmp_path):
    src = tmp_path / "in"
    (src / "#1 Wohnzimmer").mkdir(parents=True)
    (src / "@Balkon").mkdir()
    (src / "@eaDir").mkdir()
    _write(src / "#1 Wohnzimmer" / "a.jpg")
    _write(src / "@Balkon" / "b.jpg")
    _write(src / "@eaDir" / "c.jpg")
    found = P.discover_images(src, src / "output_expose", True)
    assert sorted(p.name for p in found) == ["a.jpg", "b.jpg"]


@pytest.mark.parametrize("args", [["--warmth", "nan"], ["--max-crop", "nan"], ["--vertical-strength", "inf"]])
def test_non_finite_cli_values_are_rejected(tmp_path, args):
    with pytest.raises(SystemExit) as exc:
        P.main([str(tmp_path)] + args)
    assert exc.value.code == 2


def test_unwritable_log_location_gives_clean_error(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _write(src / "foto.jpg")
    (src / "output_expose" / P.LOG_FILENAME).mkdir(parents=True)          # Log-Pfad ist ein Ordner
    assert P.main([str(src)]) == 2


def test_too_many_megapixels_are_skipped(tmp_path, monkeypatch):
    monkeypatch.setattr(P, "MAX_MEGAPIXELS", 0.3)
    src = tmp_path / "in"
    src.mkdir()
    _write(src / "gross.jpg")                                            # 0.48 MP
    assert P.main([str(src), "--no-geometry"]) == 0
    assert not (src / "output_expose" / "gross.jpg").exists()
    assert "zu groß" in (src / "output_expose" / P.LOG_FILENAME).read_text(encoding="utf-8")


def test_second_positional_argument_gets_output_hint(tmp_path, capsys):
    src = tmp_path / "in"
    src.mkdir()
    assert P.main([str(src), "ausgabe"]) == 2
    assert "-o" in capsys.readouterr().err


def test_roll_does_not_eat_the_vertical_budget():
    img = synthetic_room(1400, 1050)
    h, w = img.shape[:2]
    cx, cy, R = P._norm_params(w, h)
    f_n = 2 * 24 / 43.27
    K = np.diag([f_n, f_n, 1.0])
    Hn = K @ P.rotation_matrix(math.radians(2.5), math.radians(-8)) @ np.linalg.inv(K)
    S = np.array([[1 / R, 0, -cx / R], [0, 1 / R, -cy / R], [0, 0, 1]])
    warped = cv2.warpPerspective(img, np.linalg.inv(S) @ np.linalg.inv(Hn) @ S, (w, h),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    s = P.Settings()
    s.lens = False
    _, info = P.correct_geometry(warped.astype(np.float32) / 255, loaded_from(warped), s)
    assert abs(info["roll"]) > 2.0
    assert info["pitch"] / info["pitch_measured"] >= 0.6, info


def test_mild_warm_cast_on_white_walls_is_mostly_removed():
    rng = np.random.default_rng(7)
    lin = np.clip(0.55 + rng.normal(0, 0.01, (400, 600, 3)), 0, 1)
    lin[300:] = 0.12                                                     # Boden
    lin = (lin * np.array([1.12, 1.0, 0.85])).astype(np.float32)          # milder Kunstlichtstich
    img = P.linear_to_srgb(lin)
    out, _ = P.tone_and_color(img, False, P.Settings())
    b_in = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)[:300, :, 2].mean()
    b_out = cv2.cvtColor(out.astype(np.float32), cv2.COLOR_RGB2Lab)[:300, :, 2].mean()
    assert b_in > 8 and b_out <= 5.0, (b_in, b_out)


def test_grey_walls_in_bright_room_become_friendly_white():
    rng = np.random.default_rng(8)
    img = np.clip(0.70 + rng.normal(0, 0.01, (400, 600, 3)), 0, 1).astype(np.float32)   # L* ≈ 72
    img[280:] = 0.40
    out, _ = P.tone_and_color(img, False, P.Settings(), noise_sigma=0.1)
    L_out = cv2.cvtColor(out.astype(np.float32), cv2.COLOR_RGB2Lab)[:280, :, 0].mean()
    assert L_out >= 78, L_out


def test_sunlit_red_roof_does_not_clip_red_channel():
    img = np.zeros((400, 600, 3), np.float32)
    img[:200] = (0.93, 0.55, 0.45)                                       # sonniges Ziegeldach
    img[200:] = (0.35, 0.33, 0.30)
    out, _ = P.tone_and_color(img, False, P.Settings())
    u = P.to_u8(out[:200])
    assert ((u[..., 0] >= 254) & (u.min(axis=2) < 200)).mean() < 0.02


def test_no_denoise_does_not_change_exposure():
    img = synthetic_room(900, 600).astype(np.float32) / 255 * 0.35
    s1, s2 = P.Settings(), P.Settings()
    s2.denoise = False
    _, d1 = P.denoise_image(img, False, s1)
    _, d2 = P.denoise_image(img, False, s2)
    assert d1["sigma"] == d2["sigma"]
    _, t1 = P.tone_and_color(img, False, s1, d1["sigma"])
    _, t2 = P.tone_and_color(img, False, s2, d2["sigma"])
    assert t1["tone"]["ev"] == t2["tone"]["ev"]


def test_levels_have_no_jump():
    base = np.full((200, 300, 3), 0.5, np.float32)
    g = []
    for hi in (0.745, 0.755):
        img = base.copy()
        img[:30, :30] = hi                                               # 1.5 % > 0.2 % -> bestimmt den Weißpunkt
        g.append(P.apply_levels(img)[1]["gain"])
    assert g[0] > 1.15 and abs(g[0] - g[1]) < 0.03, g


# --------------------------------------------------------------------------- #
# Regressionen aus Review-Runde 3
# --------------------------------------------------------------------------- #

def _grey_room(h=600, w=900, seed=11):
    rng = np.random.default_rng(seed)
    img = np.clip(0.62 + rng.normal(0, 0.008, (h, w, 3)), 0, 1).astype(np.float32)   # graue Wand L* ≈ 65
    img[int(h * 0.6):] = 0.38                                                           # Boden
    return img


def test_exposure_does_not_depend_on_framing():
    img = _grey_room()
    _, full = P.tone_and_color(img, False, P.Settings(), 0.1)
    _, lower = P.tone_and_color(img[150:], False, P.Settings(), 0.1)     # mehr Boden im Bild
    assert abs(full["tone"]["ev"] - lower["tone"]["ev"]) <= 0.15, (full["tone"], lower["tone"])


def test_stain_on_bright_wall_keeps_its_contrast():
    img = _grey_room()
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)
    patch = lab[100:120, 200:220].copy()
    patch[..., 0] -= 3                                                  # schwacher Fleck
    img[100:120, 200:220] = cv2.cvtColor(patch, cv2.COLOR_Lab2RGB)
    out, _ = P.tone_and_color(img, False, P.Settings(), 0.1)
    li = cv2.cvtColor(img, cv2.COLOR_RGB2Lab)[..., 0]
    lo = cv2.cvtColor(out.astype(np.float32), cv2.COLOR_RGB2Lab)[..., 0]
    before = li[100:120, 200:220].mean() - li[100:120, 250:270].mean()
    after = lo[100:120, 200:220].mean() - lo[100:120, 250:270].mean()
    assert after / before >= 0.8, (before, after)


def test_blown_window_stays_pure_white():
    img = _grey_room() * 0.7
    img[80:250, 300:500] = 1.0                                          # ausgebranntes Fenster
    out, _ = P.tone_and_color(img, False, P.Settings(), 0.1)
    assert P.to_u8(out[120:210, 340:460]).min() >= 253


def test_lamp_glow_stays_brighter_than_ceiling():
    h, w = 500, 800
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot(yy - 150, xx - 400)
    ceiling = np.full((h, w, 3), 0.52, np.float32)                       # graue Decke
    glow = np.exp(-(r / 90.0) ** 2)[..., None] * np.array([0.35, 0.22, 0.08], np.float32)
    img = np.clip(ceiling + glow, 0, 1)
    img[r < 12] = 1.0                                                   # Glühbirne
    out, _ = P.tone_and_color(img, False, P.Settings(), 0.1)
    L = cv2.cvtColor(out.astype(np.float32), cv2.COLOR_RGB2Lab)[..., 0]
    ring = L[(r > 30) & (r < 60)].mean()
    far = L[(r > 250) & (r < 300)].mean()
    assert ring > far, (ring, far)


def test_own_output_is_not_processed_again(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _write(src / "foto.jpg")
    assert P.main([str(src), "--no-geometry"]) == 0
    again = tmp_path / "again"
    again.mkdir()
    (again / "foto.jpg").write_bytes((src / "output_expose" / "foto.jpg").read_bytes())
    P.main([str(again), "--no-geometry"])
    assert not (again / "output_expose" / "foto.jpg").exists()
    assert "bereits ein Ergebnis" in (again / "output_expose" / P.LOG_FILENAME).read_text(encoding="utf-8")


def test_edited_output_is_not_overwritten_and_exit_code_signals_it(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _write(src / "foto.jpg")
    assert P.main([str(src), "--no-geometry"]) == 0
    out = src / "output_expose" / "foto.jpg"
    Image.open(out).save(out, quality=80)                               # vom Nutzer nachbearbeitet
    before = sha(out)
    assert P.main([str(src), "--no-geometry"]) == 1
    assert sha(out) == before


def test_compare_image_follows_its_output(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _write(src / "foto.jpg")
    assert P.main([str(src), "--no-geometry", "--compare"]) == 0
    cmp = src / "output_expose" / P.COMPARE_DIRNAME / "foto_vergleich.jpg"
    Image.new("RGB", (50, 50)).save(cmp)                                # veraltetes Vergleichsbild ohne Kennung
    assert P.main([str(src), "--no-geometry", "--compare"]) == 0        # Ergebnis ist unser -> Vergleich auch
    with Image.open(cmp) as im:
        assert im.width > 50


def test_two_image_files_get_a_clear_hint(tmp_path, capsys):
    _write(tmp_path / "a.jpg")
    _write(tmp_path / "b.jpg")
    assert P.main([str(tmp_path / "a.jpg"), str(tmp_path / "b.jpg")]) == 2
    assert "Ordner" in capsys.readouterr().err


def test_steep_shot_still_gets_its_horizon_levelled():
    img = synthetic_room(1400, 1050)
    h, w = img.shape[:2]
    cx, cy, R = P._norm_params(w, h)
    f_n = 2 * 24 / 43.27
    K = np.diag([f_n, f_n, 1.0])
    Hn = K @ P.rotation_matrix(math.radians(2.5), math.radians(-28)) @ np.linalg.inv(K)
    S = np.array([[1 / R, 0, -cx / R], [0, 1 / R, -cy / R], [0, 0, 1]])
    warped = cv2.warpPerspective(img, np.linalg.inv(S) @ np.linalg.inv(Hn) @ S, (w, h),
                                 flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    small, _ = P.resize_long_edge(cv2.cvtColor(warped, cv2.COLOR_RGB2GRAY), 1200)
    info = P.estimate_verticals(small, f_n, P.Settings())
    assert info["ok"] and abs(info["roll"] - 2.5) < 0.5 and info["pitch"] == 0.0, info


@pytest.mark.skipif(os.name == "nt", reason="Byte-Dateinamen nur unter POSIX")
def test_non_utf8_filename_appears_in_log(tmp_path):
    src = tmp_path / "in"
    src.mkdir()
    _write(src / os.fsdecode(b"K\xfcche.jpg"))
    assert P.main([str(src), "--no-geometry"]) == 0
    assert "OK      K" in (src / "output_expose" / P.LOG_FILENAME).read_text(encoding="utf-8")


def test_noise_estimate_ignores_blown_areas():
    rng = np.random.default_rng(12)
    g = np.clip(100 + rng.normal(0, 4, (600, 800)), 0, 255)
    clean = P.estimate_noise_sigma(g.astype(np.uint8))
    g[:, :300] = 255                                                    # großes ausgebranntes Fenster
    blown = P.estimate_noise_sigma(g.astype(np.uint8))
    assert abs(blown - clean) < 0.3, (clean, blown)
