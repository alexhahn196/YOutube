#!/usr/bin/env python3
"""Assemble the SIGNAL Episode 1 silent visual master.
Two-pass: (1) normalize every segment to uniform 1080p30 CFR files,
(2) xfade-chain them with title cards. Output: signal_ep01_master.mp4
"""
import json, os, subprocess, sys, re
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
CLIPDIR = os.path.join(HERE, "clips")
NORMDIR = os.path.join(HERE, "norm"); os.makedirs(NORMDIR, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H, FPS = 1920, 1080, 30
XF = 0.5          # crossfade seconds
TITLE_DUR = 2.4   # title card seconds

SEQ = [
    ("title", ("SIGNAL", "signal or noise - you decide")),
    ("clip", "C01"), ("clip", "C02"), ("clip", "C03"),
    ("title", ("THE CLAIM", "what the internet said")),
    ("clip", "C04"), ("clip", "C05"), ("clip", "C06"), ("clip", "C07"),
    ("title", ("THE EVIDENCE", "what the telescopes measured")),
    ("clip", "C09"), ("clip", "C10"), ("clip", "C11"), ("clip", "C12"),
    ("clip", "C13"), ("clip", "C14"), ("clip", "C16"), ("clip", "C17"),
    ("title", ("THE VERDICT", "leans noise - most likely natural")),
    ("clip", "C19"), ("clip", "C20"), ("clip", "C21"),
    ("title", ("SIGNAL", "which object should we investigate next?")),
]

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERR:\n", r.stderr[-2500:]); raise SystemExit(1)
    return r

def probe_dur(path):
    out = subprocess.run([FF, "-i", path], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", out)
    if not m: return 6.0
    h, mi, s = m.groups(); return int(h)*3600+int(mi)*60+float(s)

def make_title_png(idx, big, small):
    from PIL import Image, ImageDraw, ImageFont
    png = os.path.join(NORMDIR, f"title_{idx}.png")
    img = Image.new("RGB", (W, H), (5, 7, 13)); dr = ImageDraw.Draw(img)
    f_big = ImageFont.truetype(FONT, 116); f_small = ImageFont.truetype(FONT, 42)
    bb = dr.textbbox((0, 0), big, font=f_big)
    dr.text(((W-(bb[2]-bb[0]))/2 - bb[0], H/2 - 150 - bb[1]), big, font=f_big, fill=(34, 211, 238))
    dr.rectangle([(W-560)//2, H//2 - 18, (W+560)//2, H//2 - 15], fill=(34, 211, 238))
    sb = dr.textbbox((0, 0), small, font=f_small)
    dr.text(((W-(sb[2]-sb[0]))/2 - sb[0], H/2 + 20 - sb[1]), small, font=f_small, fill=(208, 238, 245))
    img.save(png); return png

FADE = 0.3  # per-segment in/out fade seconds

def normalize(idx, kind, val):
    """Produce a uniform CFR 1080p30 mp4 with short in/out fades; return (path, dur)."""
    out = os.path.join(NORMDIR, f"seg_{idx:02d}.mp4")
    if kind == "title":
        png = make_title_png(idx, val[0], val[1])
        vf = (f"scale={W}:{H},setsar=1,fps={FPS},format=yuv420p,"
              f"fade=t=in:st=0:d=0.4,fade=t=out:st={TITLE_DUR-0.4:.2f}:d=0.4")
        run([FF, "-y", "-loop", "1", "-i", png, "-t", f"{TITLE_DUR}",
             "-vf", vf, "-r", str(FPS), "-fps_mode", "cfr",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", out])
        return out, TITLE_DUR
    src = os.path.join(CLIPDIR, f"{val}.mp4")
    if not os.path.exists(src):
        print("MISSING", val); return None
    d = probe_dur(src)
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p,"
          f"fade=t=in:st=0:d={FADE},fade=t=out:st={max(0,d-FADE):.2f}:d={FADE}")
    run([FF, "-y", "-i", src, "-vf", vf, "-r", str(FPS), "-fps_mode", "cfr", "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out])
    return out, probe_dur(out)

def main():
    items = []
    for i, (kind, val) in enumerate(SEQ):
        r = normalize(i, kind, val)
        if r: items.append(r)
    n = len(items)
    print(f"normalized {n} segments, total ~{sum(d for _,d in items):.1f}s")
    # concat demuxer (identical codec params -> stream copy, lossless & reliable)
    listf = os.path.join(NORMDIR, "list.txt")
    with open(listf, "w") as f:
        for p, _ in items:
            f.write(f"file '{p}'\n")
    out = os.path.join(HERE, "signal_ep01_master.mp4")
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", listf,
         "-c", "copy", "-movflags", "+faststart", out])
    print("OK ->", out, "| duration", round(probe_dur(out), 2), "s")

if __name__ == "__main__":
    main()
