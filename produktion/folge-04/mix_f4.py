#!/usr/bin/env python3
"""Mix F4: 3 Musik-Beds (Reuse aus F1/F2) je Akt loopen, unter VO ducken (Sidechain),
mit Silent-4K-Video muxen -> f4_FINAL_4k.mp4. Akte: Seg 1-3 / 4-6 / 7-10."""
import os, re, subprocess, math, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__)); WORK = os.path.join(HERE,"work4k")
F2 = os.path.join(HERE,"..","folge-02")
LEAD, GAP, TAIL = 0.5, 0.3, 0.6
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print("ERR:"," ".join(cmd)[:200],"\n",r.stderr[-1500:]); raise SystemExit(1)
    return r
def dur(p):
    o=subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m=re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)",o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0

D=[dur(os.path.join(HERE,f"vo_seg{i:02d}.mp3")) for i in range(1,11)]
vslot=[]
for i,d in enumerate(D):
    s=d + (LEAD if i==0 else 0) + (TAIL if i==len(D)-1 else GAP); vslot.append(s)
act=[sum(vslot[0:3]), sum(vslot[3:6]), sum(vslot[6:10])]
print("acts:", [round(a,1) for a in act], "total", round(sum(act),1))

beds=[os.path.join(F2,"music_act1.mp3"),os.path.join(F2,"music_act2.mp3"),os.path.join(F2,"music_act3.mp3")]
actwavs=[]
for i,(bed,adur) in enumerate(zip(beds,act)):
    bd=dur(bed); loops=max(1,math.ceil(adur/bd)+1)
    o=os.path.join(WORK,f"actmus_{i}.wav")
    fade_out_st=max(0.1, adur-2.0)
    run([FF,"-y","-stream_loop",str(loops),"-i",bed,"-t",f"{adur:.3f}",
         "-af",f"afade=t=in:st=0:d=1.8,afade=t=out:st={fade_out_st:.2f}:d=2.0,aformat=sample_rates=44100:channel_layouts=stereo",
         "-c:a","pcm_s16le",o]); actwavs.append(o)
listf=os.path.join(WORK,"mlist.txt"); open(listf,"w").write("".join(f"file '{p}'\n" for p in actwavs))
music_full=os.path.join(WORK,"music_full.wav")
run([FF,"-y","-f","concat","-safe","0","-i",listf,"-c","copy",music_full])
print("music_full",round(dur(music_full),1))

# VO-Vollspur bauen
def sil(name,d):
    p=os.path.join(WORK,name)
    run([FF,"-y","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-t",f"{d}","-c:a","pcm_s16le",p]); return p
def seg_wav(mp3,i):
    p=os.path.join(WORK,f"vw_{i:02d}.wav")
    run([FF,"-y","-i",mp3,"-ar","44100","-ac","2","-c:a","pcm_s16le",p]); return p
lead=sil("sil_lead.wav",LEAD); gap=sil("sil_gap.wav",GAP); tail=sil("sil_tail.wav",TAIL)
seq=[lead]
for i in range(1,11):
    seq.append(seg_wav(os.path.join(HERE,f"vo_seg{i:02d}.mp3"),i))
    seq.append(tail if i==10 else gap)
alistf=os.path.join(WORK,"alist.txt"); open(alistf,"w").write("".join(f"file '{p}'\n" for p in seq))
vo_full=os.path.join(WORK,"f4_vo_full.wav")
run([FF,"-y","-f","concat","-safe","0","-i",alistf,"-c","copy",vo_full])
print("VO_FULL:", round(dur(vo_full),1),"s")

silent=os.path.join(HERE,"f4_video_silent_4k.mp4")
final=os.path.join(HERE,"f4_FINAL_4k.mp4")
run([FF,"-y","-i",silent,"-i",vo_full,"-i",music_full,"-filter_complex",
     "[1:a]asplit=2[vomix][vosc];[2:a]volume=0.30[m0];"
     "[m0][vosc]sidechaincompress=threshold=0.05:ratio=8:attack=15:release=400[md];"
     "[vomix][md]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]",
     "-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest",final])
print("FINAL",final,round(dur(final),1),"s")
