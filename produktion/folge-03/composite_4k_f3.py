#!/usr/bin/env python3
"""Composite SIGNAL Ep03 overlays onto f2_FINAL_4k -> f3_MASTER_4K.mp4 (2160p).
Same technique as composite_f2.py (HUD persistent; timed lower-thirds/meter via 0-based fade
+ setpts PTS-shift). Reads overlays_4k.json (native-4K PNGs). Audio copied from f2_FINAL_4k."""
import os, json, subprocess, re, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
meta = json.load(open(os.path.join(HERE,"overlays_4k.json")))
VD = meta["video_dur"]
src = os.path.join(HERE,"f3_FINAL_4k.mp4"); out = os.path.join(HERE,"f3_MASTER_4K.mp4")

cmd = [FF,"-y","-i",src]
cmd += ["-loop","1","-t",f"{VD:.2f}","-i",os.path.join(HERE,meta["hud"])]
timed = []; idx = 2
for lt in meta["lowerthirds"]:
    cmd += ["-loop","1","-t",f"{lt['dur']:.2f}","-i",os.path.join(HERE,lt["png"])]
    timed.append((idx, lt["x"], lt["y"], lt["start"], lt["dur"])); idx += 1
mt = meta["meter"]
cmd += ["-loop","1","-t",f"{mt['dur']:.2f}","-i",os.path.join(HERE,mt["png"])]
timed.append((idx, mt["x"], mt["y"], mt["start"], mt["dur"])); idx += 1

fc = []
fc.append("[1:v]format=rgba,fps=30[hud]")
fc.append("[0:v][hud]overlay=0:0:eof_action=pass[b1]")
last = "b1"
for n,(i,x,y,st,dur) in enumerate(timed):
    fo = max(0.1, dur-0.35)
    en = st+dur
    fc.append(f"[{i}:v]format=rgba,fps=30,fade=t=in:st=0:d=0.35:alpha=1,"
              f"fade=t=out:st={fo:.2f}:d=0.35:alpha=1,setpts=PTS+{st:.3f}/TB[o{n}]")
    nxt = f"c{n}"
    fc.append(f"[{last}][o{n}]overlay={x}:{y}:enable='between(t,{st:.2f},{en:.2f})':eof_action=pass[{nxt}]")
    last = nxt

cmd += ["-filter_complex",";".join(fc),"-map",f"[{last}]","-map","0:a",
        "-t",f"{VD:.2f}","-c:v","libx264","-preset","fast","-crf","18",
        "-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",out]
print("compositing 4K:", len(timed),"timed overlays + HUD -> f3_MASTER_4K.mp4")
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode:
    print("ERR\n", r.stderr[-2500:]); raise SystemExit(1)
o = subprocess.run([FF,"-i",out],capture_output=True,text=True).stderr
d = re.search(r"Duration: (\S+),",o); res = re.search(r"(\d{3,4}x\d{3,4})", o)
print("f3_MASTER_4K done", d.group(1) if d else "?", res.group(1) if res else "?", os.path.getsize(out)//1048576,"MB")
