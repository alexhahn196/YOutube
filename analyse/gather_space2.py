# -*- coding: utf-8 -*-
"""Welle 2: Mid-/Low-Tier + weitere Space-Kanäle (leicht: about+videos+rss, keine Watch-Seiten).
Tolerant: Handle-Fehlschläge werden geloggt und übersprungen. Output: space/<handle>.json (gleiches Schema, top_watch=[])."""
import re, os, json, sys, html
sys.path.insert(0, os.path.dirname(__file__))
import fetchlib
fetchlib.RAW = os.path.join(os.path.dirname(__file__), "..", "raw_space")
os.makedirs(fetchlib.RAW, exist_ok=True)
from fetchlib import fetch
from gather_space import norm, parse_tab, parse_rss
OUT = os.path.join(os.path.dirname(__file__), "space")

HANDLES = [
    "VoyagerSpace", "astrumextra", "fexl", "CosmicLens", "spacemattersdoc",
    "Acronium", "insanecuriosity", "Eternityinspace", "NSpaceNews",
    "officialcosmosprodigy", "Kosmo_off", "Ridddle", "RealHyperspeed",
    "Starlight_Ai", "beyonddiscovery",
]

def gather_light(h):
    fn = os.path.join(OUT, h + ".json")
    if os.path.exists(fn):
        print(f"{h}: exists, skip"); return
    rec = {"handle": h}
    ab, code, note = fetch(f"https://www.youtube.com/@{h}/about", "about__" + h + ".html")
    if not ab or '"subscriberCountText"' not in ab:
        print(f"{h}: FAIL about (code={code} {note})"); return
    m = re.search(r'"subscriberCountText":"([^"]*?) subscribers?"', ab)
    rec["subs"] = norm(m.group(1)) if m else None
    m = re.search(r'"viewCountText":"([\d,]+) views?"', ab)
    rec["total_views"] = int(m.group(1).replace(",", "")) if m else None
    m = re.search(r'"videoCountText":"([\d,]+) videos?"', ab)
    rec["video_count"] = int(m.group(1).replace(",", "")) if m else None
    m = re.search(r'"joinedDateText":\{"content":"Joined ([^"]+)"', ab)
    rec["join"] = m.group(1) if m else None
    m = re.search(r'"externalId":"(UC[\w-]+)"', ab)
    cid = m.group(1) if m else None
    rec["channel_id"] = cid
    vt, _, _ = fetch(f"https://www.youtube.com/@{h}/videos", "videos__" + h + ".html")
    vids = parse_tab(vt or "")
    rss = parse_rss(fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}", "rss__" + h + ".xml")[0]) if cid else {}
    merged = []
    for vid, v in vids.items():
        ex = rss.get(vid, {})
        merged.append({"videoId": vid, "title": v["title"] or ex.get("title"),
                       "views": ex.get("views_exact") if ex.get("views_exact") is not None else v["views_abbrev"],
                       "views_exact": ex.get("views_exact") is not None,
                       "dur": v["dur"], "pub": v["pub"], "pub_ts": ex.get("pub_ts"), "desc_rss": ex.get("desc")})
    merged = [v for v in merged if isinstance(v["views"], int)]
    merged.sort(key=lambda x: -x["views"])
    rec["all_videos"] = merged
    rec["top5"] = merged[:5]
    rec["top_watch"] = []
    json.dump(rec, open(fn, "w"), ensure_ascii=False)
    top = merged[0]["views"] if merged else 0
    print(f"{h}: subs={rec['subs']} vids={rec['video_count']} scraped={len(merged)} top={top:,}")

if __name__ == "__main__":
    for h in HANDLES:
        try:
            gather_light(h)
        except Exception as e:
            print(f"{h}: EXC {type(e).__name__}: {str(e)[:80]}")
    print("SPACE2_DONE")
