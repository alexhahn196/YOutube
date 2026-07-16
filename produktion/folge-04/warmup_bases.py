#!/usr/bin/env python3
"""Baut Boomerang-Bases fuer alle bereits vorhandenen Clips vor (parallel zum Rendern
der letzten 4 Videos), damit assemble_4k_f4.py spaeter nur noch Slots fuellen muss."""
import os, glob, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("asm", os.path.join(HERE,"assemble_4k_f4.py"))
# assemble laeuft bei Import bis zum EDL-Teil durch — stattdessen nur die Funktion nachbauen:
import re, subprocess, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
CLIPS = os.path.join(HERE,"clips"); WORK = os.path.join(HERE,"work4k"); os.makedirs(WORK, exist_ok=True)
W,H,FPS,SLOW = 3840,2160,30,1.5
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print("ERR:", r.stderr[-800:], flush=True); raise SystemExit(1)
for src in sorted(glob.glob(os.path.join(CLIPS,"vid_*.mp4"))):
    cid = os.path.basename(src)[4:-4]
    base = os.path.join(WORK,f"base_{cid}.mp4")
    if os.path.exists(base): print("skip", cid, flush=True); continue
    sc = (f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p")
    fc = (f"[0:v]{sc},setpts=PTS-STARTPTS[f];[0:v]{sc},reverse,setpts=PTS-STARTPTS[r];"
          f"[f][r]concat=n=2:v=1:a=0,setpts={SLOW}*PTS[bm]")
    run([FF,"-y","-i",src,"-filter_complex",fc,"-map","[bm]","-an","-r",str(FPS),
         "-fps_mode","cfr","-c:v","libx264","-preset","faster","-crf","18","-pix_fmt","yuv420p",base])
    print("base", cid, "OK", flush=True)
print("WARMUP DONE", flush=True)
