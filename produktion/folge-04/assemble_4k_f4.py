#!/usr/bin/env python3
"""SIGNAL Ep04 (Wow!-Signal) — 4K (2160p) silent montage, built directly at 4K.
NY01 hero is native 4K; alle anderen (1080p neu + Pool-Reuse) lanczos-upscale.
Boomerang bases + slot fill + concat — same proven technique as F1-F3."""
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

# EDL: 10 Segmente -> Shot-Listen (NY = neu, NV/C/NW/NX = Pool-Reuse aus F1-F3)
EDL = [
 ["NY12","NY01","NY03","NY01"],                  # 1 cold open (Archiv -> Printout -> Drucker -> Wow!)
 ["NY02","NY03","NY01"],                         # 2 the night 1977 (Big Ear, Drucker, Ehman-Fund)
 ["NY05","NW05","NY04","NX07","NY02"],           # 3 why different (H-Linie, Schmalband, Sagittarius, Kurve, 2 Hoerner)
 ["NV10","NV11","C17","NY11"],                   # 4 the hunt (Follow-ups, Stille, Golfplatz-Killer-Beat)
 ["NV15","NY09"],                                # 5 claim wave (Schlagzeilen, Arecibo-Antwort)
 ["NZ01","NV08","NV14","C19","NY01","NX07"],     # 6 verdict Q1 (BLC1-Forensik CLEAN, Standard, Verdict, Ehman-Zitat, Flip)
 ["NV13","NY04","NZ01","NY02","NV14"],           # 7 explanations die (Komet, Stern, RFI-CLEAN, Horn-Fail, Urteil)
 ["NY09","NY06","NY07","NY08","NY12"],           # 8 new suspect (Arecibo-Scans, H-Wolke, Magnetar, Blaze, 40k Blips)
 ["NY11","NY10","NY01","NY12"],                  # 9 closing (Golfplatz, Ruine, Printout, Archiv)
 ["NY01","C19","C20"],                           # 10 outro (Hero-Printout-Callback, Verdict, F5-Tease) — NV05 raus (ERR-404-Slop)
]
assert len(EDL)==10
slots=[]; idx=0
for si,cids in enumerate(EDL):
    per = vslot[si]/len(cids)
    for c in cids:
        slots.append(fill_clip(c, per, idx)); idx+=1
    print(f"seg{si+1:02d} {round(vslot[si],1)}s / {len(cids)} shots", flush=True)

listf = os.path.join(WORK,"vlist.txt"); open(listf,"w").write("".join(f"file '{p}'\n" for p in slots))
silent = os.path.join(HERE,"f4_video_silent_4k.mp4")
run([FF,"-y","-f","concat","-safe","0","-i",listf,"-c","copy",silent])
print("SILENT 4K:", round(dur(silent),1),"s", os.path.getsize(silent)//1048576,"MB")
print("done")
