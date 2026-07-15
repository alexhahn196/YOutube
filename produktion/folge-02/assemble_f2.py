#!/usr/bin/env python3
"""SIGNAL Ep02 (K2-18b): silent visual timed to 13 VO segments (boomerang fill) + vo_full.wav.
1080p master. Same technique as Folge 1 v4 (boomerang bases, slot fill, concat)."""
import os, re, subprocess, math, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, "clips"); WORK = os.path.join(HERE, "work"); os.makedirs(WORK, exist_ok=True)
W, H, FPS, SLOW = 1920, 1080, 30, 1.5
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
         "-fps_mode","cfr","-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",base])
    return base
def fill_clip(cid, target, idx):
    base = boomerang_base(cid); bd = dur(base); loops = max(1, math.ceil(target/bd))
    out = os.path.join(WORK, f"slot_{idx:03d}_{cid}.mp4")
    if os.path.exists(out): return out
    run([FF,"-y","-stream_loop",str(loops),"-i",base,"-t",f"{target:.3f}","-r",str(FPS),
         "-fps_mode","cfr","-c:v","libx264","-preset","fast","-crf","17","-pix_fmt","yuv420p",out])
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

# EDL: 13 Segmente -> Shot-Listen (NW = neu, NV/C = Folge-1-Reuse)
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
 ["NV05","C17","C19"],                            # 13 outro
]
assert len(EDL)==13
slots=[]; idx=0
for si,cids in enumerate(EDL):
    per = vslot[si]/len(cids)
    for c in cids:
        slots.append(fill_clip(c, per, idx)); idx+=1
    print(f"seg{si+1:02d} {round(vslot[si],1)}s / {len(cids)} shots", flush=True)

listf = os.path.join(WORK,"vlist.txt"); open(listf,"w").write("".join(f"file '{p}'\n" for p in slots))
silent = os.path.join(HERE,"f2_video_silent.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",listf,"-c","copy",silent])
print("SILENT:", round(dur(silent),1),"s")

def sil(name,d):
    p=os.path.join(WORK,name)
    run([FF,"-y","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-t",f"{d}","-c:a","pcm_s16le",p]); return p
def seg_wav(mp3,i):
    p=os.path.join(WORK,f"vw_{i:02d}.wav")
    run([FF,"-y","-i",mp3,"-ar","44100","-ac","2","-c:a","pcm_s16le",p]); return p
lead=sil("sil_lead.wav",LEAD); gap=sil("sil_gap.wav",GAP); tail=sil("sil_tail.wav",TAIL)
seq=[lead]
for i,mp3 in enumerate(vo):
    seq.append(seg_wav(mp3,i))
    seq.append(tail if i==len(vo)-1 else gap)
alistf=os.path.join(WORK,"alist.txt"); open(alistf,"w").write("".join(f"file '{p}'\n" for p in seq))
vo_full=os.path.join(HERE,"f2_vo_full.wav")
run([FF,"-y","-f","concat","-safe","0","-i",alistf,"-c","copy",vo_full])
print("VO_FULL:", round(dur(vo_full),1),"s")
print("done")
