#!/usr/bin/env python3
"""Approximate .srt for v4: re-derive 14 segment texts (same as tts.py), use vo_seg mp3
durations + LEAD/GAP offsets, split each segment into sentence cues, distribute time by
character length. Segment boundaries are exact; within-segment is proportional (de3 is even-paced)."""
import os, re, subprocess, imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = "/home/user/YOutube/skript/signal-03-VO.md"
LEAD, GAP, TAIL = 0.5, 0.3, 0.6
def dur(p):
    o=subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m=re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)",o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0

# --- replicate tts.py segmentation ---
raw=open(SRC).read().splitlines()
segments=[]; cur_title=None; cur=[]
def flush():
    global cur_title,cur
    if cur_title is not None: segments.append((cur_title,cur[:]))
    cur=[]
for ln in raw:
    s=ln.strip()
    if s.startswith("══"):
        flush(); cur_title=re.sub(r"[═\s]+"," ",s).strip(); continue
    if cur_title is None: continue
    if not s: continue
    if re.match(r"^\[MID-ROLL",s,re.I) or re.match(r"^\[TITLE",s,re.I): continue
    s=re.sub(r"^\[LANGER BEAT\]$","…",s,flags=re.I); s=re.sub(r"^\[BEAT\]$","",s,flags=re.I)
    cur.append(s)
flush()
merged=[]
for title,lines in segments:
    text=" ".join(lines).strip(); text=re.sub(r"\s*…\s*"," ",text); text=re.sub(r"\s+"," ",text)
    if merged and len(text)<120: merged[-1]=(merged[-1][0],(merged[-1][1]+" "+text).strip())
    else: merged.append((title,text))

D=[dur(os.path.join(HERE,f"vo_seg{i:02d}.mp3")) for i in range(1,11)]
assert len(D)==len(merged), f"{len(D)} vs {len(merged)}"

def cues(text):
    # split into sentences, then merge to <=~90 char cues
    sent=re.split(r"(?<=[.!?])\s+", text)
    out=[]; buf=""
    for s in sent:
        if not s.strip(): continue
        if len(buf)+len(s)+1<=90: buf=(buf+" "+s).strip()
        else:
            if buf: out.append(buf)
            if len(s)<=90: buf=s
            else:
                # hard-split long sentence on commas/words
                w=s.split(); b2=""
                for x in w:
                    if len(b2)+len(x)+1<=90: b2=(b2+" "+x).strip()
                    else: out.append(b2); b2=x
                buf=b2
    if buf: out.append(buf)
    return out

def wrap(t):  # <=42 chars/line, max 2 lines
    w=t.split(); L=[""]
    for x in w:
        if len(L[-1])+len(x)+1<=42: L[-1]=(L[-1]+" "+x).strip()
        else: L.append(x)
    return "\n".join(L[:2]) if len(L)<=2 else L[0]+"\n"+" ".join(L[1:])

def tc(s):
    h=int(s//3600); m=int((s%3600)//60); sec=s%60
    return f"{h:02d}:{m:02d}:{int(sec):02d},{int((sec-int(sec))*1000):03d}"

off=LEAD; idx=1; out=[]
for i,((title,text),d) in enumerate(zip(merged,D)):
    cs=cues(text); tot=sum(len(c) for c in cs) or 1; t=off
    for c in cs:
        cd=d*len(c)/tot; st=t; en=t+cd; t=en
        out.append(f"{idx}\n{tc(st)} --> {tc(en-0.06)}\n{wrap(c)}\n"); idx+=1
    off += d + (TAIL if i==len(D)-1 else GAP)

open(os.path.join(HERE,"signal_f3.srt"),"w").write("\n".join(out))
print(f"signal_f3.srt: {idx-1} cues, ends {tc(off)}")
