#!/usr/bin/env python3
"""Build subtitles.ass + bauchbinden.json from forced-alignment JSON (fa0..4.json).
Segment offsets match final_assemble timeline."""
import json, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
OFF = [0.4, 67.0, 204.5, 587.0, 699.1]  # absolute start of each segment's audio

def words_of(i):
    d = json.load(open(os.path.join(HERE, f"fa{i}.json")))
    out = []
    for w in d["words"]:
        t = w["text"]
        if t.strip() == "":
            continue
        out.append({"raw": t, "norm": re.sub(r"[^a-z0-9]", "", t.lower()),
                    "start": OFF[i] + w["start"], "end": OFF[i] + w["end"], "seg": i})
    return out

ALLW = []
for i in range(5):
    ALLW += words_of(i)
print("total real words:", len(ALLW))

# ---------- subtitle cues ----------
def sec_to_ass(t):
    h = int(t//3600); m = int((t%3600)//60); s = t%60
    return f"{h:d}:{m:02d}:{s:05.2f}"

cues = []
cur = []
for k, w in enumerate(ALLW):
    cur.append(w)
    raw = w["raw"]
    dur = cur[-1]["end"] - cur[0]["start"]
    nxt_gap = (ALLW[k+1]["start"] - w["end"]) if k+1 < len(ALLW) else 9
    end_sentence = raw.endswith((".", "?", "!", ":"))
    if len(cur) >= 8 or dur >= 3.0 or end_sentence or nxt_gap > 0.6:
        cues.append(cur); cur = []
if cur:
    cues.append(cur)

# clamp cue ends to next start
lines = []
for j, c in enumerate(cues):
    st = c[0]["start"]; en = c[-1]["end"] + 0.12
    if j+1 < len(cues):
        en = min(en, cues[j+1][0]["start"] - 0.02)
    txt = " ".join(x["raw"] for x in c)
    txt = re.sub(r"\s+([,.;:!?%])", r"\1", txt)   # no space before punctuation
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = txt.lstrip(",.;:  ").strip()              # drop stray leading punctuation
    lines.append((st, en, txt))

ass_head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SIG,DejaVu Sans,54,&H00FFFFFF,&H00FFFFFF,&H00201008,&H96000000,-1,0,0,0,100,100,0,0,1,3,1,2,120,120,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, Effect, Text
"""
with open(os.path.join(HERE, "subtitles.ass"), "w") as f:
    f.write(ass_head)
    for st, en, txt in lines:
        f.write(f"Dialogue: 0,{sec_to_ass(st)},{sec_to_ass(en)},SIG,,0,0,0,,{txt}\n")
print("subtitle cues:", len(lines))
for st, en, txt in lines[:4]:
    print(f"  [{st:.1f}-{en:.1f}] {txt}")

# ---------- bauchbinden anchors ----------
# join normalized words with positions for phrase search
norms = [w["norm"] for w in ALLW]
def find_time(phrase, after=0.0):
    toks = [re.sub(r"[^a-z0-9]", "", p.lower()) for p in phrase.split()]
    n = len(toks)
    for k in range(len(norms)-n+1):
        if ALLW[k]["start"] < after:
            continue
        if norms[k:k+n] == toks:
            return ALLW[k]["start"]
    return None

BB = [
    ("third interstellar object", "THIRD INTERSTELLAR OBJECT", "1I Oumuamua 2017  .  2I Borisov 2019  .  3I/ATLAS 2025"),
    ("highest ever measured", "ECCENTRICITY  e = 6.143", "Highest ever measured  .  unbound hyperbolic orbit"),
    ("catalogued", "LOEB SCALE:  4 / 10", "Anomalous, most likely natural  .  arXiv 2508.09167"),
    ("half billion", "AGE  >  7.6 BILLION YEARS", "Likely older than the Sun  .  Hopkins et al. 2025"),
    ("October 29th", "PERIHELION  29 OCT 2025", "q = 1.357 AU  .  between Earth and Mars"),
    ("December 19th", "CLOSEST TO EARTH  19 DEC 2025", "No course change  .  no maneuver observed"),
    ("87 percent", "JWST  .  AUG 2025  (pre-perihelion)", "87% CO2  .  9% CO  .  only ~4% water"),
    ("forty-fold", "DEC 2025  .  WATER x40, METHANE APPEARS", "SPHEREx / JWST MIRI  .  chemistry normalizes"),
    ("right alongside", "POST-PERIHELION  .  IRON APPEARS", "Ni/Fe falls in line with comet Tempel 1"),
    ("9 degrees", "9 deg FROM THE 'WOW!' SIGNAL", "Geometric coincidence  .  p = 0.6%"),
    ("Green Bank", "GREEN BANK  .  18 DEC 2025", "No signal above 100 mW  .  arXiv 2512.19763"),
    ("Allen Telescope", "SETI ALLEN ARRAY  .  74M HITS", "All human tech / satellites  .  0 from object"),
    ("Leans Noise", "VERDICT:  LEANS NOISE", "Most likely natural  .  not case-closed"),
]
bblist = []
for anchor, title, sub in BB:
    t = find_time(anchor)
    if t is None:
        print("  !! anchor NOT found:", anchor); continue
    bblist.append({"start": round(t, 2), "title": title, "sub": sub, "anchor": anchor})
bblist.sort(key=lambda x: x["start"])
json.dump(bblist, open(os.path.join(HERE, "bauchbinden.json"), "w"), indent=1)
print("bauchbinden:", len(bblist))
for b in bblist:
    print(f"  [{b['start']:.1f}] {b['title']}  //  {b['sub']}")
