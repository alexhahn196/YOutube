#!/usr/bin/env python3
"""SIGNAL v4 overlays (Pillow RGBA): persistent HUD, verdict meter (Mostly Noise),
timed lower-thirds (source + measurement date). Emits PNGs + overlays.json with timings."""
import os, json, math, subprocess, re, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__)); OV = os.path.join(HERE,"ov"); os.makedirs(OV, exist_ok=True)
W,H = 1920,1080
CY=(46,224,232,255); CYd=(46,224,232,150); INK=(233,239,247,255); MUT=(150,175,195,255)
NOISE=(242,178,76,255)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FM="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def f(p,s): return ImageFont.truetype(p,s)

def dur(p):
    o=subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m=re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)",o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0

# ---------- persistent HUD ----------
def make_hud():
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    m,ln=54,34
    for (cx,cy,dx,dy) in [(m,m,1,1),(W-m,m,-1,1),(m,H-m,1,-1),(W-m,H-m,-1,-1)]:
        d.line([(cx,cy),(cx+dx*ln,cy)],fill=CYd,width=2)
        d.line([(cx,cy),(cx,cy+dy*ln)],fill=CYd,width=2)
    # wordmark TL
    d.ellipse([m+2,m+20,m+12,m+30],fill=CY)
    d.text((m+22,m+13),"SIGNAL",font=f(FMB,26),fill=INK)
    d.text((m+2,m+46),"EP.01 // INTERSTELLAR OBJECT 3I/ATLAS",font=f(FM,15),fill=MUT)
    # tracking tag TR
    tag="TRK // e=6.143  v∞=57.99 km/s"
    tb=d.textbbox((0,0),tag,font=f(FM,15))
    d.text((W-m-(tb[2]-tb[0]),m+13),tag,font=f(FM,15),fill=MUT)
    d.text((W-m-96,m+40),"● REC",font=f(FMB,15),fill=(230,90,90,255))
    # signal-strength bar BL
    bx,by=m+2,H-m-22
    d.text((bx,by-20),"SIGNAL STRENGTH",font=f(FM,13),fill=MUT)
    import random
    hs=[6,10,8,13,9,15,11,7,12,8]
    for i,hh in enumerate(hs):
        d.rectangle([bx+i*9,by+ (16-hh),bx+i*9+6,by+16],fill=CYd if i%2==0 else CY)
    im.save(os.path.join(OV,"hud.png")); return

# ---------- verdict meter ----------
def make_meter():
    mw,mh=820,150; im=Image.new("RGBA",(mw,mh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,mw-1,mh-1],fill=(8,12,20,205),outline=CYd,width=2)
    d.text((26,16),"VERDICT",font=f(FMB,17),fill=MUT)
    d.text((26,38),"SIGNAL  ↔  NOISE",font=f(FM,13),fill=MUT)
    # gauge
    gx,gy,gw,gh=26,78,mw-52,16
    for i in range(gw):
        t=i/gw
        # signal(cyan) -> noise(amber)
        r=int(46+(242-46)*t); g=int(224+(178-224)*t); b=int(232+(76-232)*t)
        d.line([(gx+i,gy),(gx+i,gy+gh)],fill=(r,g,b,255))
    d.rectangle([gx,gy,gx+gw,gy+gh],outline=(40,60,80,255),width=1)
    # needle at 78% (Mostly Noise)
    nx=gx+int(gw*0.78)
    d.line([(nx,gy-8),(nx,gy+gh+8)],fill=INK,width=3)
    d.ellipse([nx-7,gy-16,nx+7,gy-2],fill=NOISE,outline=(8,12,20,255),width=2)
    labels=["Signal","Leans Sig.","Mixed","Leans Noise","Mostly Noise","Noise"]
    for i,lb in enumerate(labels):
        lx=gx+int(gw*(i/(len(labels)-1)))
        col=NOISE if lb=="Mostly Noise" else MUT
        fo=f(FMB,13) if lb=="Mostly Noise" else f(FM,12)
        tb=d.textbbox((0,0),lb,font=fo); d.text((lx-(tb[2]-tb[0])/2,gy+gh+10),lb,font=fo,fill=col)
    im.save(os.path.join(OV,"meter.png")); return (mw,mh)

# ---------- lower-thirds ----------
def make_lt(idx, source, detail):
    lw,lh=880,116; im=Image.new("RGBA",(lw,lh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,lw-1,lh-1],fill=(8,12,20,200))
    d.rectangle([0,0,6,lh],fill=CY)
    d.text((26,20),"◉ SOURCE",font=f(FM,13),fill=CYd)
    d.text((26,40),source,font=f(FB,27),fill=INK)
    d.text((26,80),detail,font=f(FM,16),fill=MUT)
    im.save(os.path.join(OV,f"lt_{idx:02d}.png")); return

# ---------- segment offsets ----------
LEAD,GAP,TAIL=0.5,0.3,0.6
D=[dur(os.path.join(HERE,f"vo_seg{i:02d}.mp3")) for i in range(1,15)]
off=[]; t=LEAD
for i,dd in enumerate(D):
    off.append(t); t+= dd + (TAIL if i==len(D)-1 else GAP)

make_hud(); mw,mh=make_meter()

# lower-thirds: (segment_index, seconds_into_segment, source, detail)
LT=[
 (1, 8,  "ORBIT SOLUTION", "e = 6.143 · v∞ = 57.99 km/s · Seligman et al. 2025"),
 (2, 12, "WOW! SIGNAL, 1977", "Big Ear, Ohio · direction match 9° · p ≈ 0.6%"),
 (5, 20, "JWST NIRSpec, 6 Aug 2025", "CO₂/H₂O = 7.6 (pre-perihelion) · arXiv 2508.18209"),
 (6, 6,  "OPTICAL SPECTROSCOPY", "Fe I + Ni I detected post-perihelion · arXiv 2605.07652"),
 (7, 30, "SEKANINA, 1974", "Comet Kohoutek anti-tail = large-grain projection"),
 (8, 6,  "LOOK-ELSEWHERE", "1 in ~100 coincidence out of 22 anomalies → not significant"),
 (9, 10, "GREEN BANK TELESCOPE, 18 Dec 2025", "no transmitter above 0.1 W · 471,198→9→RFI · arXiv 2512.19763"),
 (10,8,  "LOEB SCALE", "3I/ATLAS = Level 4 (‘most likely natural’) · arXiv 2508.09167"),
 (11,58, "NON-GRAV. ACCELERATION", "transverse component unresolved · arXiv 2603.00782"),
]
timings=[]
for i,(seg,sub,src,det) in enumerate(LT):
    make_lt(i,src,det)
    st=off[seg]+sub
    timings.append({"png":f"ov/lt_{i:02d}.png","start":round(st,2),"dur":6.0,"x":72,"y":H-116-70})
# meter: verdict segment (index 11 = seg12) — show for ~16s
meter_start=off[11]+2
meta={"hud":"ov/hud.png","meter":{"png":"ov/meter.png","start":round(meter_start,2),"dur":18.0,
      "x":(W-mw)//2,"y":H-mh-60,"w":mw,"h":mh},
      "lowerthirds":timings,"video_dur":round(t,2)}
json.dump(meta,open(os.path.join(HERE,"overlays.json"),"w"),indent=2)
print("overlays built:",len(LT),"lower-thirds + HUD + meter; video_dur",round(t,1))
print("meter at",round(meter_start,1),"s")
