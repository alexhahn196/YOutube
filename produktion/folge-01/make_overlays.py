#!/usr/bin/env python3
"""Render SIGNAL overlay PNGs (RGBA): HUD (persistent), verdict meter, bauchbinden cards."""
import json, os
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1920, 1080
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CY = (34, 211, 238)      # cyan
CYd = (34, 211, 238, 190)
WH = (232, 244, 250)
AM = (245, 185, 95)      # amber (noise side)
def font(p, s): return ImageFont.truetype(p, s)

# ---------------- HUD (persistent, subtle) ----------------
def hud():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    a = 150
    col = (34, 211, 238, a)
    L, T, R, B, ln, th = 46, 40, W-46, H-40, 54, 2
    # corner brackets
    for (x, y, dx, dy) in [(L,T,1,1),(R,T,-1,1),(L,B,1,-1),(R,B,-1,-1)]:
        d.line([(x, y), (x+dx*ln, y)], fill=col, width=th)
        d.line([(x, y), (x, y+dy*ln)], fill=col, width=th)
    # top-right wordmark + signal strength bar
    fw = font(FB, 30); fs = font(FR, 20)
    d.ellipse([R-224, T+6, R-210, T+20], fill=(34,211,238,220))
    d.text((R-198, T+2), "SIGNAL", font=fw, fill=(34,211,238,225))
    d.text((R-300, T+40), "SIGNAL STRENGTH", font=fs, fill=(200,230,238,170))
    bx = R-300
    for i in range(10):
        filled = i < 6
        c = (34,211,238,210) if filled else (120,150,160,90)
        d.rectangle([bx+i*20, T+66, bx+i*20+14, T+80], fill=c)
    # faint center reticle
    cx, cy = W//2, H//2
    rc = (34,211,238,60)
    d.ellipse([cx-26, cy-26, cx+26, cy+26], outline=rc, width=2)
    d.line([(cx-40,cy),(cx-14,cy)], fill=rc, width=2); d.line([(cx+14,cy),(cx+40,cy)], fill=rc, width=2)
    d.line([(cx,cy-40),(cx,cy-14)], fill=rc, width=2); d.line([(cx,cy+14),(cx,cy+40)], fill=rc, width=2)
    # bottom-left tracking tag
    ft = font(FR, 22)
    d.text((L+6, B-30), "3I/ATLAS  //  TRACKING", font=ft, fill=(200,230,238,150))
    img.save(os.path.join(HERE, "hud.png")); print("hud.png")

# ---------------- bauchbinde card ----------------
def bb_card(idx, title, sub):
    cw, ch = 900, 108
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, cw-1, ch-1], radius=10, fill=(8, 12, 18, 175))
    d.rectangle([0, 0, 7, ch-1], fill=CY)                 # left accent bar
    d.rounded_rectangle([0, 0, cw-1, ch-1], radius=10, outline=(34,211,238,110), width=2)
    d.text((28, 20), title, font=font(FB, 34), fill=CY)
    d.text((28, 62), sub, font=font(FR, 25), fill=WH)
    p = os.path.join(HERE, f"bb_{idx:02d}.png"); img.save(p); return p

# ---------------- verdict meter ----------------
def meter():
    cw, ch = 940, 230
    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, cw-1, ch-1], radius=14, fill=(6, 10, 16, 200))
    d.rounded_rectangle([0, 0, cw-1, ch-1], radius=14, outline=(34,211,238,120), width=2)
    d.text((40, 22), "THE VERDICT", font=font(FB, 30), fill=CY)
    d.text((cw-330, 28), "signal  or  noise ?", font=font(FR, 24), fill=(200,225,235))
    # track
    tx0, tx1, ty = 60, cw-60, 120
    # 5 zones colored from cyan(signal) to amber(noise)
    zones = 5
    zc = [(34,211,238),(90,200,210),(150,170,180),(220,160,110),(245,150,90)]
    zw = (tx1-tx0)/zones
    for i in range(zones):
        d.rounded_rectangle([tx0+i*zw+3, ty-9, tx0+(i+1)*zw-3, ty+9], radius=6, fill=zc[i]+(220,))
    d.text((tx0-4, ty+22), "SIGNAL", font=font(FB, 22), fill=CY)
    d.text((tx1-86, ty+22), "NOISE", font=font(FB, 22), fill=AM)
    # pointer at "leans noise" = ~ zone 4 center = 3.5/5 = 70%..78% -> use 0.76
    px = tx0 + (tx1-tx0)*0.76
    d.polygon([(px-16, ty-34),(px+16, ty-34),(px, ty-12)], fill=WH)
    d.text((px-96, ty-70), "LEANS NOISE", font=font(FB, 26), fill=(245,205,120))
    img.save(os.path.join(HERE, "meter.png")); print("meter.png")

if __name__ == "__main__":
    hud(); meter()
    bbs = json.load(open(os.path.join(HERE, "bauchbinden.json")))
    for i, b in enumerate(bbs):
        bb_card(i, b["title"], b["sub"])
    print(f"{len(bbs)} bauchbinden cards")
