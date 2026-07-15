#!/usr/bin/env python3
import os, glob, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
# reuse the functions from assemble script via exec of its defs (simple copy)
import re, subprocess, math, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
CLIPS = os.path.join(HERE,"clips"); WORK = os.path.join(HERE,"work4k"); os.makedirs(WORK, exist_ok=True)
W,H,FPS,SLOW = 3840,2160,30,1.5
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print("ERR:", r.stderr[-500:]); raise SystemExit(1)
def base(cid):
    src=os.path.join(CLIPS,f"vid_{cid}.mp4"); b=os.path.join(WORK,f"base_{cid}.mp4")
    if os.path.exists(b): print("cached",cid); return
    sc=(f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p")
    fc=(f"[0:v]{sc},setpts=PTS-STARTPTS[f];[0:v]{sc},reverse,setpts=PTS-STARTPTS[r];"
        f"[f][r]concat=n=2:v=1:a=0,setpts={SLOW}*PTS[bm]")
    run([FF,"-y","-i",src,"-filter_complex",fc,"-map","[bm]","-an","-r",str(FPS),
         "-fps_mode","cfr","-c:v","libx264","-preset","faster","-crf","18","-pix_fmt","yuv420p",b])
    print("built",cid, flush=True)
for f in sorted(glob.glob(os.path.join(CLIPS,"vid_*.mp4"))):
    base(os.path.basename(f)[4:-4])
print("warmup done")
