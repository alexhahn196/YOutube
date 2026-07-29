#!/usr/bin/env python3
"""Thumbnail-Bauer im v2-Muster (§13b) — gemeinsame Pipeline statt Pro-Folge-Kopie.

Rezept (aus den ersten eigenen CTR-Daten abgeleitet, 28.07.2026):
  Split-Screen  |  linke Haelfte = eindeutig Weltraum (0,3-Sekunden-Test)
                |  rechte Haelfte = das konkrete Beweisstueck
  Vollflaechen-Banner unten, near-white, Text SCHWARZ (Feed-Lesbarkeit bei 168x94)
  Text stellt eine FRAGE, nie eine Feststellung — und verraet nie das Verdict
  Ziel: mittlere Luminanz >= 120/255, Fast-Schwarz <= 25 %

Neu gegenueber compose_thumb_f4_v2.py: Die Helligkeit wird nicht mehr von Hand geraten,
sondern gesucht, bis das Luminanz-Ziel erreicht ist (die F1-Quellbilder sind extrem dunkel —
das live laufende F1-Thumbnail kam auf 41/255 bei 68 % Fast-Schwarz).

Nutzung:
  python3 make_thumb.py --left a.png --right b.png --main "IS IT ALIVE?" --sub "K2-18b" \
      --out ../folge-02/thumbnail/v2master_f2.jpg
"""
import argparse, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.environ.get("SIGNAL_FONTS", "/tmp/claude-0/-home-user-YOutube/"
                       "49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad/fonts")
ANTON = os.path.join(FONTS, "Anton-Regular.ttf")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

W, H = 1280, 720
BANNER_H = 168
IMG_H = H - BANNER_H
HALF = W // 2
PAPER = (247, 245, 238)
INK = (12, 14, 18)
AMBER = (214, 108, 32)
CY = (46, 224, 232)

# Damit das Gesamtbild >=120 erreicht, muss die Bildflaeche (77 % der Hoehe) ueber ~85 liegen —
# das Banner (near-white, 23 %) steuert rund 57 Punkte bei.
IMG_MEAN_TARGET = 96
IMG_DARK_MAX = 30.0


def stats(im):
    h = im.convert("L").histogram()
    n = sum(h)
    return sum(v * c for v, c in enumerate(h)) / n, sum(h[:40]) / n * 100


def strip_letterbox(im):
    """Schwarze Balken oben/unten entfernen.

    Nur die Bildmitte wird abgetastet (35–65 % der Breite): am Rand sitzen HUD-Ecken
    und Vignetten, die sonst als Balken durchgehen — genau der Fehler, der bei
    make_short.py erst 107 statt 285 px gemessen hat.
    """
    g = im.convert("L")
    w, h = g.size
    x0, x1 = int(w * 0.35), int(w * 0.65)
    rows = [sum(g.crop((x0, y, x1, y + 1)).histogram()[:24]) / (x1 - x0) for y in range(h)]
    top = 0
    while top < h // 3 and rows[top] > 0.97:
        top += 1
    bot = h - 1
    while bot > h * 2 // 3 and rows[bot] > 0.97:
        bot -= 1
    return im.crop((0, top, w, bot + 1)) if (top or bot < h - 1) else im


def fill_crop(path, tw, th, cx=0.5):
    im = strip_letterbox(Image.open(path).convert("RGB"))
    target = tw / th
    w, h = im.size
    if w / h > target:
        nw = int(h * target)
        x0 = int((w - nw) * cx)
        im = im.crop((x0, 0, x0 + nw, h))
    else:
        nh = int(w / target)
        y0 = (h - nh) // 2
        im = im.crop((0, y0, w, y0 + nh))
    return im.resize((tw, th), Image.LANCZOS)


def lift(im, sat=1.15, mean_target=None):
    """Helligkeit hochziehen, bis das Luminanz-Ziel steht — ohne die Farben auszuwaschen.

    Reihenfolge: erst Gamma (hebt die Schatten, laesst Lichter stehen), dann lineare
    Helligkeit als Rest. Umgekehrt waeren die hellen Stellen zuerst ausgebrannt.
    """
    goal = mean_target or IMG_MEAN_TARGET
    im = ImageEnhance.Color(im).enhance(sat)
    for gamma in (1.0, 1.3, 1.6, 1.9, 2.2, 2.5):
        lut = [min(255, int(((v / 255) ** (1 / gamma)) * 255)) for v in range(256)]
        cand = im.point(lut * 3)
        for br in (1.0, 1.15, 1.3, 1.45, 1.6):
            out = ImageEnhance.Brightness(cand).enhance(br) if br > 1 else cand
            mean, dark = stats(out)
            if mean >= goal and dark <= IMG_DARK_MAX:
                return out, gamma, br
    return out, gamma, br


MARKER_RED = (228, 42, 38)


def draw_marker(d, spec):
    """Roter Kreis/Pfeil — §13.7: NUR auf etwas, das wirklich im Bild ist.

    Bewusst leicht unrund und mit ungleicher Strichstaerke gezeichnet: ein perfekter
    Vektorkreis liest sich als Grafik-Overlay (= Aggregator-Marker), eine unruhige Linie
    als Annotation von Hand. Nie um leeren Raum ziehen — der Klick bricht dann nach
    10 Sekunden ab, und wir brauchen Wiedergabezeit, nicht Klicks.

    spec: "circle,cx,cy,rx,ry" oder "arrow,x1,y1,x2,y2" (alles 0..1 der Gesamtflaeche)
    """
    kind, *vals = spec.split(",")
    v = [float(x) for x in vals]
    if kind == "circle":
        cx, cy, rx, ry = v[0] * W, v[1] * H, v[2] * W, v[3] * H
        for i, (dx, dy, wd) in enumerate([(0, 0, 7), (2, -1, 5), (-2, 2, 4)]):
            d.ellipse([cx - rx + dx, cy - ry + dy, cx + rx + dx, cy + ry + dy],
                      outline=MARKER_RED, width=wd)
            rx, ry = rx * 1.03, ry * 1.02          # jede Lage minimal versetzt
    elif kind == "arrow":
        x1, y1, x2, y2 = v[0] * W, v[1] * H, v[2] * W, v[3] * H
        d.line([x1, y1, x2, y2], fill=MARKER_RED, width=9)
        import math
        ang = math.atan2(y2 - y1, x2 - x1)
        for s in (2.5, -2.5):
            d.line([x2, y2, x2 - 42 * math.cos(ang + s / 3 * 2),
                    y2 - 42 * math.sin(ang + s / 3 * 2)], fill=MARKER_RED, width=9)


def fit_font(text, max_w, max_h, start=190):
    for size in range(start, 20, -2):
        f = ImageFont.truetype(ANTON, size)
        box = f.getbbox(text)
        if box[2] - box[0] <= max_w and box[3] - box[1] <= max_h:
            return f, box
    f = ImageFont.truetype(ANTON, 20)
    return f, f.getbbox(text)


def build(left_path, right_path, main_text, sub_text, out, cx_left=0.5, cx_right=0.5,
          goal=IMG_MEAN_TARGET, mark=None):
    im = Image.new("RGB", (W, H), (8, 10, 14))
    l, gl, bl = lift(fill_crop(left_path, HALF, IMG_H, cx_left), mean_target=goal)
    r, gr, br = lift(fill_crop(right_path, W - HALF, IMG_H, cx_right), mean_target=goal)
    im.paste(l, (0, 0))
    im.paste(r, (HALF, 0))

    d = ImageDraw.Draw(im)
    d.rectangle([HALF - 3, 0, HALF + 2, IMG_H], fill=CY)
    d.rectangle([0, IMG_H, W, H], fill=PAPER)
    d.rectangle([0, IMG_H, W, IMG_H + 6], fill=AMBER)

    pad = 34
    sub_w = 300 if sub_text else 0
    f_main, box = fit_font(main_text, W - 2 * pad - sub_w, BANNER_H - 44)
    d.text((pad - box[0], IMG_H + (BANNER_H - (box[3] - box[1])) // 2 - box[1] + 4),
           main_text, font=f_main, fill=INK)

    if sub_text:
        f_sub = ImageFont.truetype(ANTON, 46)
        lines = sub_text.split("|")
        sy = IMG_H + (BANNER_H - len(lines) * 52) // 2 + 2
        for ln in lines:
            b = f_sub.getbbox(ln)
            d.text((W - pad - (b[2] - b[0]) - b[0], sy - b[1]), ln, font=f_sub, fill=AMBER)
            sy += 52

    if mark:
        draw_marker(d, mark)

    fc = ImageFont.truetype(MONO, 26)
    d.ellipse([30, 30, 48, 48], fill=CY)
    d.text((58, 27), "SIGNAL", font=fc, fill=(255, 255, 255),
           stroke_width=3, stroke_fill=(0, 0, 0))

    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    im.save(out, quality=94)
    mean, dark = stats(im)
    base = os.path.splitext(out)[0]
    im.resize((168, 94), Image.LANCZOS).save(base + "_feed.jpg", quality=90)   # Squint-Test
    ok = "✅" if (mean >= 120 and dark <= 25) else "⚠️ "
    print(f"{ok} {os.path.basename(out)}: Luminanz {mean:.0f}/255 (Ziel ≥120) · "
          f"Fast-Schwarz {dark:.0f} % (Ziel ≤25) · lift L γ{gl}/×{bl} R γ{gr}/×{br}")
    return mean, dark


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--left", required=True)
    p.add_argument("--right", required=True)
    p.add_argument("--main", required=True)
    p.add_argument("--sub", default="")
    p.add_argument("--out", required=True)
    p.add_argument("--cx-left", type=float, default=0.5)
    p.add_argument("--cx-right", type=float, default=0.5)
    p.add_argument("--mark", help="circle,cx,cy,rx,ry | arrow,x1,y1,x2,y2 (0..1)")
    a = p.parse_args()
    # Nachziehen, bis das Gesamtziel (>=120) steht — die Regel soll das Skript garantieren,
    # nicht der Mensch von Hand nachjustieren.
    goal = IMG_MEAN_TARGET
    while True:
        mean, dark = build(a.left, a.right, a.main, a.sub, a.out, a.cx_left, a.cx_right,
                           goal, a.mark)
        if mean >= 120 or dark > 25 or goal >= 130:
            break
        goal += 6


if __name__ == "__main__":
    main()
