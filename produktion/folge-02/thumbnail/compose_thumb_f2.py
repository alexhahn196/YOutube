#!/usr/bin/env python3
"""SIGNAL F2 Thumbnail v2 — panel-regelkonform:
- 1 Textelement (2-4 Woerter), Cap-Height >=25% Framehoehe, weiss+amber, 6px schwarzer Stroke
- KEIN Verdict/Meter (Schaufenster-Regel), Mini-Brand-Chip klein
- Ziel: mittlere Luminanz >=90/255, <=35% near-black
- Outputs: 1280x720 JPG (<2MB) + 168x94 Feed-Mock + Graustufen-Squint
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import os
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = "/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad/fonts"
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
MONO  = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
W, H = 1280, 720
INK = (245, 243, 232)      # near-white
AMBER = (255, 179, 71)     # warm accent
CY = (46, 224, 232)

def load_plate(name, brighten=1.0, sat=1.0, gamma=0.78):
    im = Image.open(os.path.join(HERE, name)).convert("RGB")
    im = im.resize((W, H), Image.LANCZOS)
    lut = [min(255, int(255 * (i/255) ** gamma)) for i in range(256)] * 3
    im = im.point(lut)
    if brighten != 1.0: im = ImageEnhance.Brightness(im).enhance(brighten)
    if sat != 1.0: im = ImageEnhance.Color(im).enhance(sat)
    return im

def stroke_text(d, xy, txt, font, fill, stroke=6):
    d.text(xy, txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=(5,8,12))

def brand_chip(d):
    f = ImageFont.truetype(MONO, 26)
    d.ellipse([28, 30, 42, 44], fill=CY)
    d.text((52, 26), "SIGNAL", font=f, fill=INK, stroke_width=3, stroke_fill=(5,8,12))

def metrics(im):
    g = im.convert("L"); hist = g.histogram()
    total = sum(hist); mean = sum(i*c for i,c in enumerate(hist))/total
    near_black = sum(hist[:26])/total
    return mean, near_black

# ---- V1: Plate A, "SIGNS OF LIFE?" zweizeilig links ----
def v1():
    im = load_plate("plate_A.png", brighten=1.06, sat=1.08)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(ANTON, 128)   # "SIGNS OF"
    f2 = ImageFont.truetype(ANTON, 208)   # "LIFE?" ~29% von 720
    stroke_text(d, (48, 208), "SIGNS OF", f1, INK, 6)
    stroke_text(d, (44, 348), "LIFE?", f2, AMBER, 8)
    brand_chip(d)
    return im

# ---- V2: Plate B, "IS IT ALIVE?" oben links ----
def v2():
    im = load_plate("plate_B.png", brighten=1.04, sat=1.05)
    d = ImageDraw.Draw(im)
    f1 = ImageFont.truetype(ANTON, 150)
    f2 = ImageFont.truetype(ANTON, 190)
    stroke_text(d, (48, 96), "IS IT", f1, INK, 6)
    stroke_text(d, (44, 250), "ALIVE?", f2, AMBER, 8)
    brand_chip(d)
    return im

# ---- V3: Plate A, solo "LIFE?" riesig ----
def v3():
    im = load_plate("plate_A.png", brighten=1.06, sat=1.08)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(ANTON, 300)    # ~42% von 720
    stroke_text(d, (40, 250), "LIFE?", f, AMBER, 10)
    f_sub = ImageFont.truetype(ANTON, 74)
    stroke_text(d, (52, 580), "WEBB'S STRANGEST FIND", f_sub, INK, 5)
    brand_chip(d)
    return im

outs = {"v1_SIGNSOFLIFE": v1(), "v2_ISITALIVE": v2(), "v3_LIFE": v3()}
feed = Image.new("RGB", (3*168+40, 94+20), (15,15,15))
for i,(name,im) in enumerate(outs.items()):
    p = os.path.join(HERE, f"cand_{name}.jpg")
    im.save(p, quality=92)
    mean, nb = metrics(im)
    print(f"{name}: mean_lum={mean:.0f}/255  near_black={nb*100:.0f}%  {'OK' if mean>=85 and nb<=0.40 else 'CHECK'}")
    # Feed-Mock + Squint
    small = im.resize((168, 94), Image.LANCZOS)
    small.save(os.path.join(HERE, f"feed_{name}.jpg"), quality=90)
    feed.paste(small, (10+i*(168+10), 10))
    im.convert("L").resize((168,94)).save(os.path.join(HERE, f"gray_{name}.jpg"), quality=90)
feed.save(os.path.join(HERE, "feedmock_all.jpg"), quality=92)
print("3 Kandidaten + Feed-Mocks + Graustufen gebaut")

# ---- FINAL: V1 + Judge-Fixes ----
def final_master():
    im = load_plate("plate_A.png", brighten=1.06, sat=1.12)
    # Fix 3a: Orange-Flare oben rechts ~30% dimmen (radialer Dunkel-Verlauf)
    ov = Image.new("L", (W, H), 0)
    dov = ImageDraw.Draw(ov)
    for r in range(420, 0, -6):
        a = int(80 * (1 - r/420))
        dov.ellipse([W-180-r, -160-r, W-180+r, -160+r+320], fill=a)
    dark = Image.new("RGB", (W, H), (5, 8, 14))
    im = Image.composite(dark, im, ov.point(lambda x: min(x, 75)))
    # Fix 3b: Plume-Region leicht aufhellen (radial um x=800,y=180)
    glow = Image.new("L", (W, H), 0)
    dg = ImageDraw.Draw(glow)
    for r in range(300, 0, -8):
        a = int(38 * (1 - r/300))
        dg.ellipse([800-r, 170-int(r*1.3), 800+r, 170+int(r*1.3)], fill=a)
    bright = ImageEnhance.Brightness(im).enhance(1.28)
    im = Image.composite(bright, im, glow)
    # Fix 2: Links-Scrim hinter Textzone (0 -> 20% schwarz)
    scrim = Image.new("L", (W, H), 0)
    ds = ImageDraw.Draw(scrim)
    for x in range(0, 560):
        a = int(58 * (1 - x/560))
        ds.line([(x, 140), (x, 640)], fill=a)
    im = Image.composite(Image.new("RGB", (W, H), (3, 5, 9)), im, scrim)
    d = ImageDraw.Draw(im)
    # Fix 1: Textblock ~+9%
    f1 = ImageFont.truetype(ANTON, 140)
    f2 = ImageFont.truetype(ANTON, 228)
    stroke_text(d, (48, 182), "SIGNS OF", f1, INK, 7)
    stroke_text(d, (44, 334), "LIFE?", f2, AMBER, 10)
    brand_chip(d)
    return im

m = final_master()
m.save(os.path.join(HERE, "master_f2_SIGNSOFLIFE.jpg"), quality=93)
mean, nb = metrics(m)
print(f"MASTER: mean_lum={mean:.0f}/255 near_black={nb*100:.0f}%  size={os.path.getsize(os.path.join(HERE,'master_f2_SIGNSOFLIFE.jpg'))//1024}KB")
m.resize((168, 94), Image.LANCZOS).save(os.path.join(HERE, "feed_master_f2.jpg"), quality=90)
m.convert("L").resize((168, 94)).save(os.path.join(HERE, "gray_master_f2.jpg"), quality=90)
