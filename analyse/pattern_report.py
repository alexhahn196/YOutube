# -*- coding: utf-8 -*-
"""Muster-Report über alle gescrapten Space-Kanäle (space/*.json).
Je Kanal: Alter, Kadenz, Subs/Monat, Views/Monat, Median/Max (Konsistenz), Hit-Länge,
Titel-Formel-Quoten. Ausgabe: Markdown-Tabelle + gepoolte Muster, sortiert nach Subs/Monat."""
import json, re, os, glob, statistics as st
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
TODAY = date(2026, 7, 14)
MON = {m: i+1 for i, m in enumerate(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}

PAT = {
 "urgency": r"^(JUST NOW|BREAKING|\d+\s*(MINUTES?|HOURS?)\s*AGO)|\bjust\b",
 "authority": r"\b(NASA|James Webb|JWST|Voyager|Hubble|Artemis|SpaceX|Kepler|ESA)\b",
 "fear": r"\b(terrif|scar|horrif|worse|dangerous|warning|threat|nightmare|chilling|shock)\w*\b",
 "mystery": r"\b(something|it'?s not|isn'?t|shouldn'?t|can'?t explain|unexplain|no one|nobody)\b",
 "twoact": r"—|-\s",
 "question": r"\?",
}

def parse_join(j):
    if not j: return None
    m = re.match(r"(\w{3})\w* (\d{1,2}), (\d{4})", j)
    return date(int(m.group(3)), MON[m.group(1)], int(m.group(2))) if m else None

rows = []
for fp in sorted(glob.glob(os.path.join(HERE, "space", "*.json"))):
    d = json.load(open(fp))
    h = d["handle"]
    vids = [v for v in d.get("all_videos", []) if isinstance(v.get("views"), int)]
    jd = parse_join(d.get("join"))
    months = max(0.5, (TODAY - jd).days / 30.4) if jd else None
    views = [v["views"] for v in vids]
    med = int(st.median(views)) if views else 0
    mx = max(views) if views else 0
    top10 = sorted(vids, key=lambda v: -v["views"])[:10]
    tdur = [v["dur"] for v in top10 if v.get("dur")]
    titles = [v["title"] for v in vids if v.get("title")]
    quota = {k: (sum(1 for t in titles if re.search(rx, t, re.I)) / len(titles) if titles else 0) for k, rx in PAT.items()}
    rows.append({
        "handle": h, "subs": d.get("subs") or 0, "months": months,
        "vidcount": d.get("video_count") or len(vids),
        "upl_mon": (d.get("video_count") or len(vids)) / months if months else None,
        "subs_mon": (d.get("subs") or 0) / months if months else None,
        "views_mon": (d.get("total_views") or 0) / months if months else None,
        "median": med, "max": mx, "consist": med / mx if mx else 0,
        "hitlen": st.median(tdur) / 60 if tdur else None,
        **{("q_" + k): v for k, v in quota.items()},
        "n_scraped": len(vids),
    })

rows.sort(key=lambda r: -(r["subs_mon"] or 0))
def fm(x, spec=",.0f"):
    return format(x, spec) if isinstance(x, (int, float)) and x is not None else "?"

print("| Kanal | Subs | Alter (Mon) | Upl/Mon | Subs/Mon | Views/Mon | Median-Views | Max | Konsistenz | Hit-Länge |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['handle']} | {fm(r['subs'])} | {fm(r['months'],'.1f')} | {fm(r['upl_mon'],'.1f')} | "
          f"{fm(r['subs_mon'])} | {fm(r['views_mon'])} | {fm(r['median'])} | {fm(r['max'])} | "
          f"{r['consist']:.1%} | {fm(r['hitlen'],'.1f')} min |")

print("\n**Titel-Formel-Quoten (Anteil der Titel):**\n")
print("| Kanal | Urgency/Just | Autorität | Angst | Mystery | Zweiakter | Frage |")
print("|---|---|---|---|---|---|---|")
for r in rows:
    print(f"| {r['handle']} | {r['q_urgency']:.0%} | {r['q_authority']:.0%} | {r['q_fear']:.0%} | "
          f"{r['q_mystery']:.0%} | {r['q_twoact']:.0%} | {r['q_question']:.0%} |")
