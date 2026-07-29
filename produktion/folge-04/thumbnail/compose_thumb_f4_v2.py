#!/usr/bin/env python3
"""SIGNAL F4 Thumbnail v2 — datengetriebener Redesign (28.07.2026).

Anlass: erste echte CTR-Daten (1,06 % Longform, gesundes Band 4-6 %).
Konkurrenz-Analyse (Proof-Hits 2,69M + 1,27M Views) — uebernommen wurden NUR die
legitimen Design-Mechaniken, NICHT das Fake-News-Branding:
  UEBERNOMMEN: Split-Screen-Vergleich (Neugier "was ist der Unterschied?"),
               Text in hellem Vollflaechen-Banner (max. Kontrast, liest sich bei 168x94),
               ein saettigungsstarkes Fokusobjekt je Haelfte, Zahl + Mysterium im Text.
  VERWORFEN:   Fake-"NASA LIVE"-Badge, CNN-Nachbau-Logo, "NASA IN PANIC!"-Dauertext,
               nachtraeglich gezeichnete rote Kreise (Impersonation + §13.7 + Policy-Risiko).
Diegetischer roter Kreis (Ehmans echte Handschrift auf dem Printout) bleibt erlaubt (§13.7-Praezedenz).

Fix gegenueber v1: (1) liest in 0,3 s als SPACE (v1 war ein beiges Dokument),
(2) mittlere Luminanz deutlich hoeher, (3) Text stellt eine FRAGE statt eine Feststellung.
"""
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMGS = os.path.join(HERE, "..", "imgs")
FONTS = "/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad/fonts"
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

W, H = 1280, 720
BANNER_H = 168
IMG_H = H - BANNER_H
HALF = W // 2
PAPER = (247, 245, 238)      # Banner-Hintergrund
INK = (12, 14, 18)           # Banner-Text
AMBER = (214, 108, 32)       # warmer Akzent
CY = (46, 224, 232)          # Marke


def fill_crop(path, tw, th, brighten=1.0, sat=1.0, cx=0.5):
    """Bild auf Zielformat fuellen (Center-Crop, cx verschiebt den Bildausschnitt)."""
    im = Image.open(path).convert("RGB")
    target = tw / th
    w, h = im.size
    if w / h > target:                      # zu breit -> seitlich beschneiden
        nw = int(h * target)
        x0 = int((w - nw) * cx)
        im = im.crop((x0, 0, x0 + nw, h))
    else:                                   # zu hoch -> oben/unten beschneiden
        nh = int(w / target)
        y0 = (h - nh) // 2
        im = im.crop((0, y0, w, y0 + nh))
    im = im.resize((tw, th), Image.LANCZOS)
    if brighten != 1.0:
        im = ImageEnhance.Brightness(im).enhance(brighten)
    if sat != 1.0:
        im = ImageEnhance.Color(im).enhance(sat)
    return im


def fit_font(text, max_w, max_h, start=200):
    """Groesste Anton-Groesse, die in die Box passt."""
    for size in range(start, 20, -2):
        f = ImageFont.truetype(ANTON, size)
        box = f.getbbox(text)
        if box[2] - box[0] <= max_w and box[3] - box[1] <= max_h:
            return f, box
    f = ImageFont.truetype(ANTON, 20)
    return f, f.getbbox(text)


def build(main_text, sub_text, out_name):
    im = Image.new("RGB", (W, H), (8, 10, 14))

    # LINKS: Sagittarius-Sternfeld (sagt in 0,3 s "Weltraum")
    left = fill_crop(os.path.join(IMGS, "img_NY04.png"), HALF, IMG_H, brighten=1.18, sat=1.22)
    im.paste(left, (0, 0))
    # RECHTS: der echte 6EQUJ5-Printout mit Ehmans Kreis (diegetisch)
    right = fill_crop(os.path.join(IMGS, "img_NY01.png"), W - HALF, IMG_H,
                      brighten=1.12, sat=1.08, cx=0.42)
    im.paste(right, (HALF, 0))

    d = ImageDraw.Draw(im)
    # Trennlinie in Markenfarbe
    d.rectangle([HALF - 3, 0, HALF + 2, IMG_H], fill=CY)

    # Banner
    d.rectangle([0, IMG_H, W, H], fill=PAPER)
    d.rectangle([0, IMG_H, W, IMG_H + 6], fill=AMBER)   # warme Kante

    # Haupttext (schwarz auf hell = maximaler Kontrast, liest sich im Feed)
    pad = 34
    sub_w = 300 if sub_text else 0
    f_main, box = fit_font(main_text, W - 2 * pad - sub_w, BANNER_H - 44, start=190)
    tx = pad - box[0]
    ty = IMG_H + (BANNER_H - (box[3] - box[1])) // 2 - box[1] + 4
    d.text((tx, ty), main_text, font=f_main, fill=INK)

    # Sub-Zeile rechts im Banner
    if sub_text:
        f_sub = ImageFont.truetype(ANTON, 46)
        lines = sub_text.split("|")
        total_h = len(lines) * 52
        sy = IMG_H + (BANNER_H - total_h) // 2 + 2
        for ln in lines:
            b = f_sub.getbbox(ln)
            d.text((W - pad - (b[2] - b[0]) - b[0], sy - b[1]), ln, font=f_sub, fill=AMBER)
            sy += 52

    # Marken-Chip oben links
    fc = ImageFont.truetype(MONO, 26)
    d.ellipse([30, 30, 48, 48], fill=CY)
    d.text((58, 27), "SIGNAL", font=fc, fill=(255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0))

    out = os.path.join(HERE, out_name)
    im.save(out, quality=94)

    # QC: Luminanz + Squint-Test
    g = im.convert("L")
    px = list(g.getdata())
    mean = sum(px) / len(px)
    dark = sum(1 for p in px if p < 40) / len(px) * 100
    im.resize((168, 94), Image.LANCZOS).save(
        os.path.join(HERE, "feed_" + out_name.replace(".jpg", "") + ".jpg"), quality=90)
    g.resize((168, 94), Image.LANCZOS).save(
        os.path.join(HERE, "gray_" + out_name.replace(".jpg", "") + ".jpg"), quality=90)
    print(f"{out_name}: mittlere Luminanz {mean:.0f}/255 (Ziel >=85), Fast-Schwarz {dark:.0f}% (Ziel <=35)")
    return out


if __name__ == "__main__":
    build("72 SECONDS", "THEN|SILENCE", "v2master_f4_72SECONDS.jpg")
    build("WHO SENT IT?", "72 sec|once", "v2variantB_f4_WHOSENTIT.jpg")
