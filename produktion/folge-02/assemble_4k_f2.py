#!/usr/bin/env python3
"""SIGNAL Ep02 (K2-18b) — 4K (2160p) silent montage. Same EDL/timing as the 1080p build, but
native-4K NW01 stays 4K and all 1080p clips upscale to 4K (lanczos). Audio is reused from the
1080p mix (f2_FINAL.mp4, identical timing) — NOT regenerated here. Separate work4k dir so it
does NOT reuse the cached 1080p boomerang bases."""
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

vo = [os.path.join(HERE, f"vo_seg{i:02d}.mp3") for i in range(1,14)]
D = [dur(p) for p in vo]
vslot = []
for i,d in enumerate(D):
    s = d
    if i==0: s += LEAD
    s += (TAIL if i==len(D)-1 else GAP)
    vslot.append(s)
print("VO total", round(sum(D),1), "visual total", round(sum(vslot),1), flush=True)

# EDL: 13 Segmente -> Shot-Listen (identisch zur 1080p-Montage)
EDL = [
 ["NW02","NW06","NW01","NV15","NW03"],            # 1 cold open
 ["NW04","NW01","NV03"],                          # 2 dream
 ["NW03","NW06","NV15","NW01"],                   # 3 claim
 ["NV01"],                                        # 4 sub-cta
 ["NV14","NV08","NW05","NV13","NW05"],            # 5 war
 ["NW06","NW07","NV08","NW05","NW09"],            # 6 doppelgaenger
 ["NV03","NV11"],                                 # 7 steelman
 ["NV10","C17","NV11","NW02"],                    # 8 listened
 ["NW09","NW13","NW08","NW07","NV14"],            # 9 fork
 ["C19","NW05","NW10","NW01","NW11","NW13","NW03","C20"],  # 10 verdict
 ["NV14","NW05","NW06"],                          # 11 tools
 ["NW12","NW01"],                                 # 12 closing
 ["NY01","C17","C19"],                            # 13 outro — NV05 raus (ERR-404/Falschdatum-Slop, QC 17.07.), NY01 = echter 6EQUJ5-Printout passt zum 1977-Tease
]
assert len(EDL)==13
slots=[]; idx=0
for si,cids in enumerate(EDL):
    per = vslot[si]/len(cids)
    for c in cids:
        slots.append(fill_clip(c, per, idx)); idx+=1
    print(f"seg{si+1:02d} {round(vslot[si],1)}s / {len(cids)} shots", flush=True)

listf = os.path.join(WORK,"vlist.txt"); open(listf,"w").write("".join(f"file '{p}'\n" for p in slots))
silent = os.path.join(HERE,"f2_video_silent_4k.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",listf,"-c","copy",silent])
print("SILENT 4K:", round(dur(silent),1),"s", os.path.getsize(silent)//1048576,"MB")
print("done")
