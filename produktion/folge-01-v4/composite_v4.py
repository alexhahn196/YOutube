#!/usr/bin/env python3
"""Composite SIGNAL overlays onto v4_FINAL -> v4_MASTER.mp4.
HUD persistent (loop, bounded by -t). Lower-thirds + meter as timed windows
(-itsoffset/-t + alpha fades + overlay enable). Audio copied. No faststart on master."""
import os, json, subprocess, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(HERE,"overlays.json")))
VD = meta["video_dur"]
src = os.path.join(HERE,"v4_FINAL.mp4"); out = os.path.join(HERE,"v4_MASTER.mp4")

cmd = [FF,"-y","-i",src]
# input 1: HUD (persistent)
cmd += ["-loop","1","-t",f"{VD:.2f}","-i",os.path.join(HERE,meta["hud"])]
timed = []  # (input_index, x, y, st, dur)
idx = 2
# lower-thirds (NO -itsoffset; shift via setpts after fade so fade timing stays 0-based)
for lt in meta["lowerthirds"]:
    cmd += ["-loop","1","-t",f"{lt['dur']:.2f}","-i",os.path.join(HERE,lt["png"])]
    timed.append((idx, lt["x"], lt["y"], lt["start"], lt["dur"])); idx += 1
# meter
mt = meta["meter"]
cmd += ["-loop","1","-t",f"{mt['dur']:.2f}","-i",os.path.join(HERE,mt["png"])]
timed.append((idx, mt["x"], mt["y"], mt["start"], mt["dur"])); idx += 1

fc = []
# HUD overlay (always on)
fc.append("[1:v]format=rgba,fps=30[hud]")
fc.append("[0:v][hud]overlay=0:0:eof_action=pass[b1]")
last = "b1"
for n,(i,x,y,st,dur) in enumerate(timed):
    fo = max(0.1, dur-0.35)
    en = st+dur
    # fade on 0-based input timeline, THEN shift PTS to global start
    fc.append(f"[{i}:v]format=rgba,fps=30,fade=t=in:st=0:d=0.35:alpha=1,"
              f"fade=t=out:st={fo:.2f}:d=0.35:alpha=1,setpts=PTS+{st:.3f}/TB[o{n}]")
    nxt = f"c{n}"
    fc.append(f"[{last}][o{n}]overlay={x}:{y}:enable='between(t,{st:.2f},{en:.2f})':eof_action=pass[{nxt}]")
    last = nxt

cmd += ["-filter_complex",";".join(fc),"-map",f"[{last}]","-map","0:a",
        "-t",f"{VD:.2f}","-c:v","libx264","-preset","veryfast","-crf","18",
        "-pix_fmt","yuv420p","-c:a","copy",out]
print("compositing", len(timed),"timed overlays + HUD -> v4_MASTER.mp4")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode:
    print("ERR\n", r.stderr[-2500:]); raise SystemExit(1)
o = subprocess.run([FF,"-i",out],capture_output=True,text=True).stderr
import re
d = re.search(r"Duration: (\S+),",o)
print("v4_MASTER done", d.group(1) if d else "?", os.path.getsize(out)//1048576,"MB")
