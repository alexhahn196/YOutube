#!/usr/bin/env python3
"""Composite HUD (persistent) + bauchbinden + verdict meter (each active ONLY in its window
via -itsoffset/-t, so the graph stays light) + burned subtitles. Usage: composite.py [test_sec]"""
import json, os, subprocess, sys
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "signal_ep01_FINAL_ducked.mp4")
BB = json.load(open(os.path.join(HERE, "bauchbinden.json")))
TESTSEC = float(sys.argv[1]) if len(sys.argv) > 1 else 0

BB_DUR = 5.0
MET_S, MET_E = 636.0, 663.0

# timed overlays: (png, x, y, start, end)
timed = [(os.path.join(HERE, "meter.png"), 490, 420, MET_S, MET_E)]
for i, b in enumerate(BB):
    timed.append((os.path.join(HERE, f"bb_{i:02d}.png"), 70, 92, b["start"], b["start"]+BB_DUR))

# inputs: 0=master, 1=hud (persistent full-length), then timed (each windowed)
inputs = ["-i", MASTER, "-loop", "1", "-i", os.path.join(HERE, "hud.png")]
for png, x, y, s, e in timed:
    inputs += ["-loop", "1", "-t", f"{e-s:.2f}", "-itsoffset", f"{s:.2f}", "-i", png]

fc = ["[1:v]format=rgba[hud]", "[0:v][hud]overlay=0:0:enable='gte(t,0)'[v0]"]
prev = "v0"
for k, (png, x, y, s, e) in enumerate(timed):
    idx = 2 + k
    fc.append(f"[{idx}:v]format=rgba,fade=t=in:st={s:.2f}:d=0.3:alpha=1,"
              f"fade=t=out:st={e-0.4:.2f}:d=0.4:alpha=1[o{k}]")
    lbl = f"v{k+1}"
    fc.append(f"[{prev}][o{k}]overlay={x}:{y}:eof_action=pass:enable='between(t,{s:.2f},{e:.2f})'[{lbl}]")
    prev = lbl
subs = os.path.join(HERE, "subtitles.ass").replace(":", "\\:")
fc.append(f"[{prev}]subtitles='{subs}'[vout]")

out = os.path.join(HERE, "signal_ep01_test.mp4" if TESTSEC else "signal_ep01_MASTER_final.mp4")
cmd = [FF, "-y"] + inputs + ["-filter_complex", ";".join(fc),
       "-map", "[vout]", "-map", "0:a", "-c:v", "libx264", "-preset", "veryfast",
       "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "copy"]  # no +faststart (slow rewrite on this disk)
# hard output duration so the infinite -loop 1 HUD input can't cause an end-of-stream churn
def _dur(p):
    o = subprocess.run([FF, "-i", p], capture_output=True, text=True).stderr
    import re
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 728
cmd += ["-t", str(TESTSEC if TESTSEC else round(_dur(MASTER), 2))]
cmd += [out]
print("compositing ->", os.path.basename(out))
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode != 0:
    print("ERR:\n", r.stderr[-2500:]); sys.exit(1)
print("OK ->", out)
