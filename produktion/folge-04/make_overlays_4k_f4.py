#!/usr/bin/env python3
"""SIGNAL Ep04 overlays, nativ 4K (3840x2160): persistenter HUD (EP.04), Verdict-Meter
(Nadel 0.90 in NOISE, Frage: PROOF OF CONTACT?), 9 Quellen-Bauchbinden (inkl. Ehman-Zitat).
Meter + Zitat-Timing datengetrieben (Zeichen-Anteil im Segment-Text x gemessene VO-Dauer).
Emits ov4k/*.png + overlays_4k.json."""
import os, json, subprocess, re, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__)); OV = os.path.join(HERE,"ov4k"); os.makedirs(OV, exist_ok=True)
SRC = "/home/user/YOutube/skript/signal-04-VO.md"
SC = 2
W,H = 1920*SC,1080*SC
CY=(46,224,232,255); CYd=(46,224,232,150); INK=(233,239,247,255); MUT=(150,175,195,255)
NOISE=(242,178,76,255); RED=(230,90,90,255)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FM="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def f(p,s): return ImageFont.truetype(p,s*SC)

def dur(p):
    o=subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m=re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)",o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0

# --- Segment-Texte replizieren (wie tts_f4.py) fuer datengetriebene Marker ---
def seg_texts():
    raw=open(SRC).read().splitlines()
    segments=[]; cur_title=None; cur=[]
    def flush():
        nonlocal cur_title,cur
        if cur_title is not None: segments.append((cur_title,cur[:]))
        cur=[]
    for ln in raw:
        s=ln.strip()
        if s.startswith("══"):
            flush(); cur_title=re.sub(r"[═\s]+"," ",s).strip(); continue
        if cur_title is None: continue
        if not s: continue
        if re.match(r"^\[MID-ROLL",s,re.I) or re.match(r"^\[TITLE",s,re.I): continue
        s=re.sub(r"^\[LANGER BEAT\]$","… …",s,flags=re.I)
        s=re.sub(r"^\[BEAT\b[^\]]*\]$","…",s,flags=re.I)
        cur.append(s)
    flush()
    merged=[]
    for title,lines in segments:
        text=" ".join(lines).strip(); text=re.sub(r"\s+…\s+"," … ",text)
        if merged and len(text)<120: merged[-1]=(merged[-1][0],(merged[-1][1]+" "+text).strip())
        else: merged.append((title,text))
    return [t for _,t in merged]

TXT = seg_texts(); assert len(TXT)==10
def mark(seg, needle):
    """Sekunden in Segment seg (0-based), an denen 'needle' gesprochen wird (proportional)."""
    t = TXT[seg]; i = t.index(needle)
    return D[seg]*i/len(t)

def make_hud():
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    m,ln=54*SC,34*SC
    for (cx,cy,dx,dy) in [(m,m,1,1),(W-m,m,-1,1),(m,H-m,1,-1),(W-m,H-m,-1,-1)]:
        d.line([(cx,cy),(cx+dx*ln,cy)],fill=CYd,width=2*SC)
        d.line([(cx,cy),(cx,cy+dy*ln)],fill=CYd,width=2*SC)
    d.ellipse([m+2*SC,m+20*SC,m+12*SC,m+30*SC],fill=CY)
    d.text((m+22*SC,m+13*SC),"SIGNAL",font=f(FMB,26),fill=INK)
    d.text((m+2*SC,m+46*SC),"EP.04 // THE WOW! SIGNAL — ONE WORD IN RED INK",font=f(FM,15),fill=MUT)
    tag="TRK // 1420 MHz · 72 s · 1 detection"
    tb=d.textbbox((0,0),tag,font=f(FM,15))
    d.text((W-m-(tb[2]-tb[0]),m+13*SC),tag,font=f(FM,15),fill=MUT)
    d.text((W-m-96*SC,m+40*SC),"● REC",font=f(FMB,15),fill=RED)
    bx,by=m+2*SC,H-m-22*SC
    d.text((bx,by-20*SC),"SIGNAL STRENGTH",font=f(FM,13),fill=MUT)
    hs=[6,10,8,13,9,15,11,7,12,8]
    for i,hh in enumerate(hs):
        d.rectangle([bx+i*9*SC,by+(16-hh)*SC,bx+i*9*SC+6*SC,by+16*SC],fill=CYd if i%2==0 else CY)
    im.save(os.path.join(OV,"hud.png"))

def make_meter():
    mw,mh=820*SC,150*SC; im=Image.new("RGBA",(mw,mh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,mw-1,mh-1],fill=(8,12,20,205),outline=CYd,width=2*SC)
    d.text((26*SC,16*SC),"VERDICT — PROOF OF CONTACT?",font=f(FMB,17),fill=MUT)
    d.text((26*SC,38*SC),"SIGNAL  ↔  NOISE",font=f(FM,13),fill=MUT)
    gx,gy,gw,gh=26*SC,78*SC,mw-52*SC,16*SC
    for i in range(gw):
        t=i/gw
        r=int(46+(242-46)*t); g=int(224+(178-224)*t); b=int(232+(76-232)*t)
        d.line([(gx+i,gy),(gx+i,gy+gh)],fill=(r,g,b,255))
    d.rectangle([gx,gy,gx+gw,gy+gh],outline=(40,60,80,255),width=1*SC)
    nx=gx+int(gw*0.90)
    d.line([(nx,gy-8*SC),(nx,gy+gh+8*SC)],fill=INK,width=3*SC)
    d.ellipse([nx-7*SC,gy-16*SC,nx+7*SC,gy-2*SC],fill=NOISE,outline=(8,12,20,255),width=2*SC)
    labels=["Signal","Leans Sig.","Mixed","Leans Noise","Noise"]
    for i,lb in enumerate(labels):
        lx=gx+int(gw*(i/(len(labels)-1)))
        col=NOISE if lb=="Noise" else MUT
        fo=f(FMB,13) if lb=="Noise" else f(FM,12)
        tb=d.textbbox((0,0),lb,font=fo); d.text((lx-(tb[2]-tb[0])/2,gy+gh+10*SC),lb,font=fo,fill=col)
    im.save(os.path.join(OV,"meter.png")); return (mw,mh)

def make_lt(idx, source, detail, accent=CY):
    lw,lh=880*SC,116*SC; im=Image.new("RGBA",(lw,lh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,lw-1,lh-1],fill=(8,12,20,200))
    d.rectangle([0,0,6*SC,lh],fill=accent)
    d.text((26*SC,20*SC),"◉ SOURCE",font=f(FM,13),fill=CYd)
    d.text((26*SC,40*SC),source,font=f(FB,27),fill=INK)
    d.text((26*SC,80*SC),detail,font=f(FM,16),fill=MUT)
    im.save(os.path.join(OV,f"lt_{idx:02d}.png"))

LEAD,GAP,TAIL=0.5,0.3,0.6
D=[dur(os.path.join(HERE,f"vo_seg{i:02d}.mp3")) for i in range(1,11)]
off=[]; t=LEAD
for i,dd in enumerate(D):
    off.append(t); t+= dd + (TAIL if i==len(D)-1 else GAP)

make_hud(); mw,mh=make_meter()

# (segment_index 0-based, seconds_into_segment, source, detail, accent, dur)
LT=[
 (1, mark(1,"The Big Ear radio telescope"), "BIG EAR — OSU RADIO OBSERVATORY", "Kraus-type transit telescope · Delaware, Ohio · ran unattended", CY, 6.0),
 (2, mark(2,"Two physicists had predicted"), "COCCONI & MORRISON · NATURE 1959", "1420 MHz hydrogen line — the channel a civilization would pick", CY, 6.0),
 (2, mark(2,"Third: the shape"), "EHMAN · BIG EAR WOW! REPORT", "bell-curve fit better than 99% · seen in ONE horn only", CY, 6.0),
 (3, mark(3,"Then came the follow-ups"), "GRAY ET AL. · APJ 2001 & 2002", "META · VLA '95 · Hobart '99 · Breakthrough Listen '22 — all silent", CY, 6.0),
 (4, mark(4,"In 2012, we even answered"), "'WOW! REPLY' — ARECIBO · 15 AUG 2012", "10,000 crowdsourced messages · 35th anniversary of the signal", CY, 6.0),
 (5, mark(5,"In 2019, a telescope in Australia"), "SHEIKH ET AL. · NATURE ASTRONOMY 2021", "BLC1 'Proxima signal' · 39 h re-observation · verdict: interference", CY, 6.0),
 (5, mark(5,"vast conclusions")-1.5, "JERRY EHMAN — IN HIS OWN WORDS", "„…vast conclusions from half-vast data.“ · Wow! anniversary report", NOISE, 7.0),
 (7, mark(7,"an astronomer named Abel"), "MÉNDEZ ET AL. — 'ARECIBO WOW!' 2024/25", "H-line ghosts ~100× weaker · cold interstellar hydrogen clouds", CY, 6.0),
 (7, mark(7,"In June of twenty twenty-six"), "MÉNDEZ, DIXON & CHILDERS · JUN 2026", "first full Big Ear survey accounting · 40,000+ unexplained blips", CY, 6.0),
]
timings=[]
for i,(seg,sub,src,det,acc,dr) in enumerate(LT):
    make_lt(i,src,det,acc)
    st=off[seg]+max(0.5,sub)
    timings.append({"png":f"ov4k/lt_{i:02d}.png","start":round(st,2),"dur":dr,"x":72*SC,"y":H-116*SC-70*SC})
# Meter datengetrieben: bei "So. Signal, or noise?" in Seg 6 (0-based 5)
meter_start=off[5]+mark(5,"So. Signal, or noise?")
meta={"hud":"ov4k/hud.png","meter":{"png":"ov4k/meter.png","start":round(meter_start,2),"dur":16.0,
      "x":(W-mw)//2,"y":H-mh-60*SC,"w":mw,"h":mh},
      "lowerthirds":timings,"video_dur":round(t,2)}
json.dump(meta,open(os.path.join(HERE,"overlays_4k.json"),"w"),indent=2)
print("4K overlays:",len(LT),"lower-thirds + HUD + meter; video_dur",round(t,1))
print("meter at",round(meter_start,1),"s; LT starts:",[round(x['start'],1) for x in timings])
