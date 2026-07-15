#!/usr/bin/env python3
"""SIGNAL Ep03 (Voyager 1) — 4K (2160p) silent montage, built directly at 4K.
Native-4K clips (NX01 + 8 NV-reuse) stay 4K; 1080p clips upscale (lanczos).
Boomerang bases + slot fill + concat — same proven technique as F1/F2."""
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
    if os.path.exists(out): return out
    run([FF,"-y","-stream_loop",str(loops),"-i",base,"-t",f"{target:.3f}","-r",str(FPS),
         "-fps_mode","cfr","-c:v","libx264","-preset","faster","-crf","18","-pix_fmt","yuv420p",out])
    return out

vo = [os.path.join(HERE, f"vo_seg{i:02d}.mp3") for i in range(1,11)]
D = [dur(p) for p in vo]
vslot = []
for i,d in enumerate(D):
    s = d
    if i==0: s += LEAD
    s += (TAIL if i==len(D)-1 else GAP)
    vslot.append(s)
print("VO total", round(sum(D),1), "visual total", round(sum(vslot),1), flush=True)

# EDL: 10 Segmente -> Shot-Listen (NX = neu, NV/C/NW = Pool-Reuse)
EDL = [
 ["NV15","NX01","NX05","NX09","NX01"],           # 1 cold open (viral wave -> hero -> big bang tease)
 ["NX02","NX03","NV03","NX03","NX01"],           # 2 machine 1977 (launch, record, druyan, 48 years)
 ["NX01","NX05","NX06","NX07","NV01"],           # 3 edge (crossing, heat, field, hum) + sub-CTA
 ["NW05","NX08","NX09","NV08"],                  # 4 glitch (garble, chip, surgery)
 ["NV15","NX01"],                                # 5 wave (why we click)
 ["NX10","NX04","NX05","NX07","C19","NV14"],     # 6 verdict (4 claims -> needle -> tool)
 ["NX06","NX07","NX05"],                         # 7 real mystery (field, hum, wake)
 ["NX09","NX13","NV10","NX01"],                  # 8 endgame (feb dip, lecp, big bang now)
 ["NX04","NX12","NX03","C20"],                   # 9 closing (light-day, 2036, red dwarf, record)
 ["NV05","C17","C19"],                           # 10 outro (wow tease)
]
assert len(EDL)==10
slots=[]; idx=0
for si,cids in enumerate(EDL):
    per = vslot[si]/len(cids)
    for c in cids:
        slots.append(fill_clip(c, per, idx)); idx+=1
    print(f"seg{si+1:02d} {round(vslot[si],1)}s / {len(cids)} shots", flush=True)

listf = os.path.join(WORK,"vlist.txt"); open(listf,"w").write("".join(f"file '{p}'\n" for p in slots))
silent = os.path.join(HERE,"f3_video_silent_4k.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",listf,"-c","copy",silent])
print("SILENT 4K:", round(dur(silent),1),"s", os.path.getsize(silent)//1048576,"MB")
print("done")
