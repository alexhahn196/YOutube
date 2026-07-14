#!/usr/bin/env python3
"""SIGNAL Ep01 v4 — 4K (2160p) silent montage. Same EDL/timing as the 1080p build, but
native-4K NV shots stay 4K and 1080p reused clips upscale to 4K (lanczos). Audio reused
from the 1080p mix (identical timing) — NOT regenerated here. Separate work dir (work4k)
so it does NOT reuse the cached 1080p boomerang bases."""
import os, re, subprocess, math, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, "clips"); WORK = os.path.join(HERE, "work4k"); os.makedirs(WORK, exist_ok=True)
W, H, FPS, SLOW = 3840, 2160, 30, 1.5
LEAD, GAP, TAIL = 0.5, 0.3, 0.6

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("ERR:", " ".join(cmd)[:200], "\n", r.stderr[-1500:]); raise SystemExit(1)
    return r
def dur(p):
    o = subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0

def boomerang_base(cid):
    src = os.path.join(CLIPS, f"vid_{cid}.mp4"); base = os.path.join(WORK, f"base_{cid}.mp4")
    if os.path.exists(base): return base
    sc = (f"scale={W}:{H}:force_original_aspect_ratio=decrease:flags=lanczos,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={FPS},format=yuv420p")
    fc = (f"[0:v]{sc},setpts=PTS-STARTPTS[f];[0:v]{sc},reverse,setpts=PTS-STARTPTS[r];"
          f"[f][r]concat=n=2:v=1:a=0,setpts={SLOW}*PTS[bm]")
    run([FF,"-y","-i",src,"-filter_complex",fc,"-map","[bm]","-an","-r",str(FPS),
         "-fps_mode","cfr","-c:v","libx264","-preset","faster","-crf","18","-pix_fmt","yuv420p",base])
    return base
def fill_clip(cid, target, idx):
    base = boomerang_base(cid); bd = dur(base); loops = max(1, math.ceil(target/bd))
    out = os.path.join(WORK, f"slot_{idx:03d}_{cid}.mp4")
    run([FF,"-y","-stream_loop",str(loops),"-i",base,"-t",f"{target:.3f}","-r",str(FPS),
         "-fps_mode","cfr","-c:v","libx264","-preset","faster","-crf","18","-pix_fmt","yuv420p",out])
    return out

vo = [os.path.join(HERE, f"vo_seg{i:02d}.mp3") for i in range(1,15)]
D = [dur(p) for p in vo]
vslot = []
for i,d in enumerate(D):
    s = d
    if i==0: s += LEAD
    s += (TAIL if i==len(D)-1 else GAP)
    vslot.append(s)
print("VO total", round(sum(D),1), "visual total", round(sum(vslot),1))

EDL = [
 ["NV01","C01","C02","C04","NV02"],
 ["C05","NV03","C11","C03","NV04"],
 ["NV06","NV05","NV02"],
 ["NV08","C03"],
 ["NV07","C12","NV07"],
 ["C07","C12","C13","NV07"],
 ["C14","NV07"],
 ["C11","NV08","NV09","C02"],
 ["NV14","NV04","NV14"],
 ["NV10","C17","NV11","NV10","C17","NV13","C10","NV13"],
 ["C06","NV15","C06"],
 ["C19","C11","C14","NV13","C16","NV07","C20","C13"],
 ["NV01","C21","NV02","NV01"],
 ["C20","C19","NV02"],
]
assert len(EDL)==14
slots=[]; idx=0
for si,cids in enumerate(EDL):
    per = vslot[si]/len(cids)
    for c in cids:
        slots.append(fill_clip(c, per, idx)); idx+=1
    print(f"seg{si+1:02d} {round(vslot[si],1)}s / {len(cids)} shots", flush=True)

listf = os.path.join(WORK,"vlist.txt"); open(listf,"w").write("".join(f"file '{p}'\n" for p in slots))
silent = os.path.join(HERE,"v4_video_silent_4k.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",listf,"-c","copy",silent])
print("SILENT 4K:", round(dur(silent),1),"s", os.path.getsize(silent)//1048576,"MB")
print("done")
