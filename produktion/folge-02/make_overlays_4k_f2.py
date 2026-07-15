#!/usr/bin/env python3
"""SIGNAL Ep02 overlays at NATIVE 4K (3840x2160). Same design as make_overlays_f2.py, all
sizes/positions scaled by SC=2. Timings identical (time-based, from VO segment lengths).
Emits ov4k/*.png + overlays_4k.json."""
import os, json, subprocess, re, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__)); OV = os.path.join(HERE,"ov4k"); os.makedirs(OV, exist_ok=True)
SC = 2
W,H = 1920*SC,1080*SC
CY=(46,224,232,255); CYd=(46,224,232,150); INK=(233,239,247,255); MUT=(150,175,195,255)
NOISE=(242,178,76,255)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FM="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FMB="/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def f(p,s): return ImageFont.truetype(p,s*SC)

def dur(p):
    o=subprocess.run([FF,"-i",p],capture_output=True,text=True).stderr
    m=re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)",o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0

def make_hud():
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    m,ln=54*SC,34*SC
    for (cx,cy,dx,dy) in [(m,m,1,1),(W-m,m,-1,1),(m,H-m,1,-1),(W-m,H-m,-1,-1)]:
        d.line([(cx,cy),(cx+dx*ln,cy)],fill=CYd,width=2*SC)
        d.line([(cx,cy),(cx,cy+dy*ln)],fill=CYd,width=2*SC)
    d.ellipse([m+2*SC,m+20*SC,m+12*SC,m+30*SC],fill=CY)
    d.text((m+22*SC,m+13*SC),"SIGNAL",font=f(FMB,26),fill=INK)
    d.text((m+2*SC,m+46*SC),"EP.02 // K2-18B — A GAS ONLY LIFE MAKES",font=f(FM,15),fill=MUT)
    tag="TRK // K2-18b · 124 ly · 3σ?"
    tb=d.textbbox((0,0),tag,font=f(FM,15))
    d.text((W-m-(tb[2]-tb[0]),m+13*SC),tag,font=f(FM,15),fill=MUT)
    d.text((W-m-96*SC,m+40*SC),"● REC",font=f(FMB,15),fill=(230,90,90,255))
    bx,by=m+2*SC,H-m-22*SC
    d.text((bx,by-20*SC),"SIGNAL STRENGTH",font=f(FM,13),fill=MUT)
    hs=[6,10,8,13,9,15,11,7,12,8]
    for i,hh in enumerate(hs):
        d.rectangle([bx+i*9*SC,by+(16-hh)*SC,bx+i*9*SC+6*SC,by+16*SC],fill=CYd if i%2==0 else CY)
    im.save(os.path.join(OV,"hud.png"))

def make_meter():
    mw,mh=820*SC,150*SC; im=Image.new("RGBA",(mw,mh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,mw-1,mh-1],fill=(8,12,20,205),outline=CYd,width=2*SC)
    d.text((26*SC,16*SC),"VERDICT — IS IT LIFE?",font=f(FMB,17),fill=MUT)
    d.text((26*SC,38*SC),"SIGNAL  ↔  NOISE",font=f(FM,13),fill=MUT)
    gx,gy,gw,gh=26*SC,78*SC,mw-52*SC,16*SC
    for i in range(gw):
        t=i/gw
        r=int(46+(242-46)*t); g=int(224+(178-224)*t); b=int(232+(76-232)*t)
        d.line([(gx+i,gy),(gx+i,gy+gh)],fill=(r,g,b,255))
    d.rectangle([gx,gy,gx+gw,gy+gh],outline=(40,60,80,255),width=1*SC)
    nx=gx+int(gw*0.86)
    d.line([(nx,gy-8*SC),(nx,gy+gh+8*SC)],fill=INK,width=3*SC)
    d.ellipse([nx-7*SC,gy-16*SC,nx+7*SC,gy-2*SC],fill=NOISE,outline=(8,12,20,255),width=2*SC)
    labels=["Signal","Leans Sig.","Mixed","Leans Noise","Noise"]
    for i,lb in enumerate(labels):
        lx=gx+int(gw*(i/(len(labels)-1)))
        col=NOISE if lb=="Noise" else MUT
        fo=f(FMB,13) if lb=="Noise" else f(FM,12)
        tb=d.textbbox((0,0),lb,font=fo); d.text((lx-(tb[2]-tb[0])/2,gy+gh+10*SC),lb,font=fo,fill=col)
    im.save(os.path.join(OV,"meter.png")); return (mw,mh)

def make_lt(idx, source, detail):
    lw,lh=880*SC,116*SC; im=Image.new("RGBA",(lw,lh),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,lw-1,lh-1],fill=(8,12,20,200))
    d.rectangle([0,0,6*SC,lh],fill=CY)
    d.text((26*SC,20*SC),"◉ SOURCE",font=f(FM,13),fill=CYd)
    d.text((26*SC,40*SC),source,font=f(FB,27),fill=INK)
    d.text((26*SC,80*SC),detail,font=f(FM,16),fill=MUT)
    im.save(os.path.join(OV,f"lt_{idx:02d}.png"))

LEAD,GAP,TAIL=0.5,0.3,0.6
D=[dur(os.path.join(HERE,f"vo_seg{i:02d}.mp3")) for i in range(1,14)]
off=[]; t=LEAD
for i,dd in enumerate(D):
    off.append(t); t+= dd + (TAIL if i==len(D)-1 else GAP)

make_hud(); mw,mh=make_meter()

# (segment_index 0-based, seconds_into_segment, source, detail)
LT=[
 (2, 14, "MADHUSUDHAN ET AL. 2025", "DMS/DMDS at ~3σ · ApJL 983, L40 · DOI 10.3847/2041-8213/adc1c8"),
 (4, 33, "TAYLOR 2025 · RNAAS", "flat line preferred in 5 of 6 tests · χ²ᵥ = 1.06"),
 (4, 52, "STEVENSON ET AL. 2025 · AJ 170, 257", "noise 663 ppm vs. signal ~250 ppm · red noise"),
 (5, 32, "LUQUE ET AL. 2025 · A&A 700, A284", "insufficient evidence · ethane fits as well or better"),
 (5, 66, "PICA-CIAMARRA ET AL. 2025 · CAMBRIDGE", "650 molecules searched · ≥2.7σ for many"),
 (6, 14, "CNN STATEMENT — N. MADHUSUDHAN", "“at or below 3σ … not a strong detection”"),
 (7, 22, "TREMBLAY ET AL. 2026 · arXiv 2602.09553", "VLA + MeerKAT · millions of signals · none from K2-18b"),
 (8, 8,  "TSAI ET AL. 2026 · arXiv 2603.19803", "lab opacities → ordinary sub-Neptune · no DMS required"),
 (8, 62, "TSAI ET AL. 2024", "~20× Earth's ocean flux → ethane expected · not seen"),
 (9, 78, "WOGAN 2024 · SHORTTLE 2024", "gas-rich mini-Neptune · magma-ocean world — both still open"),
]
timings=[]
for i,(seg,sub,src,det) in enumerate(LT):
    make_lt(i,src,det)
    st=off[seg]+sub
    timings.append({"png":f"ov4k/lt_{i:02d}.png","start":round(st,2),"dur":6.0,"x":72*SC,"y":H-116*SC-70*SC})
# Meter im Verdict (seg10, 0-based 9): bei "The needle isn't in the middle" ~ +58s
meter_start=off[9]+58
meta={"hud":"ov4k/hud.png","meter":{"png":"ov4k/meter.png","start":round(meter_start,2),"dur":18.0,
      "x":(W-mw)//2,"y":H-mh-60*SC,"w":mw,"h":mh},
      "lowerthirds":timings,"video_dur":round(t,2)}
json.dump(meta,open(os.path.join(HERE,"overlays_4k.json"),"w"),indent=2)
print("4K overlays built:",len(LT),"lower-thirds + HUD + meter; video_dur",round(t,1),"at",W,"x",H)
print("meter at",round(meter_start,1),"s")
