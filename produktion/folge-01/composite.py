#!/usr/bin/env python3
"""Composite HUD + bauchbinden + verdict meter + burned subtitles onto the ducked master.
Usage: python3 composite.py [test_seconds]"""
import json, os, subprocess, sys
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "signal_ep01_FINAL_ducked.mp4")
BB = json.load(open(os.path.join(HERE, "bauchbinden.json")))
TESTSEC = float(sys.argv[1]) if len(sys.argv) > 1 else 0

BB_DUR = 5.0
MET_S, MET_E = 636.0, 663.0     # verdict meter window (Leans-Noise moment)

inputs = ["-i", MASTER, "-loop", "1", "-i", os.path.join(HERE, "hud.png"),
          "-loop", "1", "-i", os.path.join(HERE, "meter.png")]
for i in range(len(BB)):
    inputs += ["-loop", "1", "-i", os.path.join(HERE, f"bb_{i:02d}.png")]

fc = []
fc.append("[1:v]format=rgba[hud]")
fc.append("[0:v][hud]overlay=0:0[v0]")
# meter
fc.append(f"[2:v]format=rgba,fade=t=in:st={MET_S}:d=0.5:alpha=1,"
          f"fade=t=out:st={MET_E-0.6:.2f}:d=0.6:alpha=1[mtr]")
fc.append(f"[v0][mtr]overlay=490:420:enable='between(t,{MET_S},{MET_E})'[vm]")
prev = "vm"
for i, b in enumerate(BB):
    s = b["start"]; e = s + BB_DUR
    idx = 3 + i
    fc.append(f"[{idx}:v]format=rgba,fade=t=in:st={s:.2f}:d=0.3:alpha=1,"
              f"fade=t=out:st={e-0.4:.2f}:d=0.4:alpha=1[bb{i}]")
    lbl = f"vb{i}"
    fc.append(f"[{prev}][bb{i}]overlay=70:92:enable='between(t,{s:.2f},{e:.2f})'[{lbl}]")
    prev = lbl
# subtitles burn
subs = os.path.join(HERE, "subtitles.ass").replace(":", "\\:")
fc.append(f"[{prev}]subtitles='{subs}'[vout]")

out = os.path.join(HERE, "signal_ep01_test.mp4" if TESTSEC else "signal_ep01_MASTER_final.mp4")
cmd = [FF, "-y"] + inputs + ["-filter_complex", ";".join(fc),
       "-map", "[vout]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast",
       "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart"]
if TESTSEC:
    cmd += ["-t", str(TESTSEC)]
cmd += [out]
print("running composite ->", os.path.basename(out), "(test" if TESTSEC else "(full", TESTSEC or "12min", ")")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ERR:\n", r.stderr[-2500:]); sys.exit(1)
print("OK ->", out)
