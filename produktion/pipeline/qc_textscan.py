#!/usr/bin/env python3
"""QC-Gate (Playbook §6 Schritt 6): Text-Scan-Kontaktboegen VOR dem Assemble.

Extrahiert 3 Frames pro Clip (10 % / 50 % / 90 % der Dauer) und baut
Kontaktboegen (4 Clips pro Bogen) zur Sichtpruefung auf eingebrannten
Fake-Text / Slop-Artefakte. Befund danach in produktion/clip-katalog.md
eintragen — kein Clip ohne "clean"-Status in den Schnitt.

Nutzung:
    python3 qc_textscan.py <clip-ordner-oder-datei> [weitere ...] [--out qc_textscan]

Beispiel (F5): python3 ../pipeline/qc_textscan.py clips/ --out qc/textscan
"""
import subprocess, sys, re, os
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw

FF = imageio_ffmpeg.get_ffmpeg_exe()
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv"}


def duration(path):
    out = subprocess.run([FF, "-i", str(path)], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m:
        return None
    return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))


def grab(path, t, dst):
    subprocess.run([FF, "-y", "-ss", f"{t:.2f}", "-i", str(path),
                    "-frames:v", "1", str(dst)], capture_output=True)
    return dst.exists()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    out_dir = Path("qc_textscan")
    if "--out" in sys.argv:
        out_dir = Path(sys.argv[sys.argv.index("--out") + 1])
    if not args:
        sys.exit(__doc__)
    out_dir.mkdir(parents=True, exist_ok=True)

    clips = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            clips += sorted(x for x in p.iterdir() if x.suffix.lower() in VIDEO_EXT)
        elif p.suffix.lower() in VIDEO_EXT:
            clips.append(p)
    if not clips:
        sys.exit("keine Clips gefunden")

    TW, TH = 640, 360  # Thumbnail-Groesse je Frame
    rows = []
    for c in clips:
        d = duration(c)
        if not d:
            print(f"⚠️  {c.name}: Dauer nicht lesbar — MANUELL pruefen")
            continue
        frames = []
        for frac in (0.1, 0.5, 0.9):
            f = out_dir / f"_{c.stem}_{int(frac*100)}.png"
            if grab(c, d * frac, f):
                frames.append(Image.open(f).resize((TW, TH)))
        if len(frames) == 3:
            rows.append((c.name, frames))
        else:
            print(f"⚠️  {c.name}: Frame-Extraktion unvollstaendig — MANUELL pruefen")

    PER_SHEET = 4
    for s in range(0, len(rows), PER_SHEET):
        batch = rows[s:s + PER_SHEET]
        sheet = Image.new("RGB", (TW * 3 + 40, (TH + 30) * len(batch) + 10), (12, 12, 16))
        dr = ImageDraw.Draw(sheet)
        for i, (name, frames) in enumerate(batch):
            y = 10 + i * (TH + 30)
            dr.text((10, y + 4), name, fill=(255, 255, 120))
            for j, fr in enumerate(frames):
                sheet.paste(fr, (10 + j * (TW + 10), y + 22))
        dst = out_dir / f"sheet_{s // PER_SHEET + 1:02d}.jpg"
        sheet.save(dst, quality=85)
        print(f"→ {dst}  ({', '.join(n for n, _ in batch)})")
    for tmp in out_dir.glob("_*.png"):
        tmp.unlink()
    print(f"\n{len(rows)} Clips auf {(len(rows)+PER_SHEET-1)//PER_SHEET} Boegen. "
          f"Sichtpruefen und Befund in produktion/clip-katalog.md eintragen.")


if __name__ == "__main__":
    main()
