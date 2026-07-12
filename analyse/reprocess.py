# -*- coding: utf-8 -*-
"""Definitiver Reprocess aus gespeicherten Roh-Dateien (KEINE neuen Requests).
Behandelt beide HTML-Formate (lockupViewModel + richItemRenderer/videoRenderer).
Klassifiziert isShort per DAUER (<=180s), nicht per Tab. Schreibt channels/*.json neu."""
import re, os, json, glob, html
from datetime import datetime
RAW="raw"; CH="analyse/channels"

def secs(mmss):
    p=[int(i) for i in mmss.split(':')]
    return p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2]

def norm_abbrev(s):
    if s is None: return None
    s=s.replace(",","").strip(); m=re.match(r'^([\d.]+)\s*([KMB]?)$',s)
    return int(float(m.group(1))*{'':1,'K':1e3,'M':1e6,'B':1e9}[m.group(2)]) if m else None

def parse_page(path):
    """-> dict videoId -> {dur, views_abbrev, pub_text}. Beide Formate."""
    if not os.path.exists(path): return {}
    t=open(path).read(); out={}
    if '"lockupViewModel"' in t:
        for chunk in t.split('"lockupViewModel"')[1:]:
            mid=re.search(r'"contentId":"([\w-]{11})"',chunk)
            if not mid: continue
            vid=mid.group(1)
            md=re.search(r'"text":"(\d{1,2}:\d{2}(?::\d{2})?)"',chunk)
            va=re.search(r'"([\d.,]+[KMB]?) views"',chunk)
            pb=re.search(r'"content":"([^"]*? ago)"',chunk)
            if vid not in out:
                out[vid]={"dur":secs(md.group(1)) if md else None,
                          "views_abbrev":norm_abbrev(va.group(1)) if va else None,
                          "pub_text":pb.group(1) if pb else None}
    else:  # old richItemRenderer / videoRenderer
        for chunk in re.split(r'"richItemRenderer"|"videoRenderer"',t)[1:]:
            mid=re.search(r'"videoId":"([\w-]{11})"',chunk)
            if not mid: continue
            vid=mid.group(1)
            lt=re.search(r'"lengthText":\{"accessibility".*?"simpleText":"([\d:]+)"',chunk) or re.search(r'"lengthText":\{"simpleText":"([\d:]+)"',chunk)
            va=re.search(r'"viewCountText":\{"simpleText":"([\d.,]+[KMB]?) views"',chunk)
            pb=re.search(r'"publishedTimeText":\{"simpleText":"([^"]+)"',chunk)
            if vid not in out:
                out[vid]={"dur":secs(lt.group(1)) if lt else None,
                          "views_abbrev":norm_abbrev(va.group(1)) if va else None,
                          "pub_text":pb.group(1) if pb else None}
    return out

def parse_rss(path):
    if not os.path.exists(path): return []
    t=open(path).read(); ents=[]
    for e in t.split("<entry>")[1:]:
        def g(p):
            m=re.search(p,e); return m.group(1) if m else None
        vid=g(r'<yt:videoId>([\w-]+)</yt:videoId>'); ttl=g(r'<title>([^<]*)</title>')
        pub=g(r'<published>([^<]+)</published>'); vw=g(r'<media:statistics views="(\d+)"')
        desc=g(r'<media:description>((?:.|\n)*?)</media:description>')
        ents.append({"videoId":vid,"title":html.unescape(ttl) if ttl else None,"published_ts":pub,
                     "views_exact":int(vw) if vw else None,"description":html.unescape(desc) if desc else None})
    return ents

from statistics import median
for fn in sorted(glob.glob(CH+"/*.json")):
    d=json.load(open(fn)); h=d["handle"]; safe=h.replace("/","_")
    pv=parse_page(f"{RAW}/videos__{safe}.html"); ps=parse_page(f"{RAW}/shorts__{safe}.html")
    page={**pv,**ps}  # union; both tabs
    rss=parse_rss(f"{RAW}/rss__{safe}.xml") or d.get("rss_entries",[])
    exact={e["videoId"]:e["views_exact"] for e in rss if e.get("videoId") and e.get("views_exact") is not None}
    ts={e["videoId"]:e["published_ts"] for e in rss if e.get("videoId")}
    # channel type by durations present
    durs=[m["dur"] for m in page.values() if m["dur"] is not None]
    if not durs:
        ctype="SHORTS"          # keine Dauer-Overlays -> reine Shorts
        dur_note="no_duration_overlays=pure_shorts"
    else:
        md=sorted(durs)[len(durs)//2]
        ctype="SHORTS" if md<=180 else "LONG"
        dur_note=f"median_dur={md}s over {len(durs)} items"
    # build unified videos
    vids=[]
    for vid,m in page.items():
        dur=m["dur"]
        if dur is None:
            is_short = (ctype=="SHORTS")   # in Shorts-Kanal ohne Overlay = Short
            short_basis="no_dur(channel=shorts)" if is_short else "no_dur(channel=long)->unknown"
        else:
            is_short = dur<=180; short_basis="by_duration"
        vx=exact.get(vid)
        vids.append({"videoId":vid,"dur_secs":dur,
                     "views": vx if vx is not None else m["views_abbrev"],
                     "views_source":"rss_exact" if vx is not None else ("page_abbrev" if m["views_abbrev"] is not None else "none"),
                     "published_ts":ts.get(vid),"published_text":m["pub_text"],
                     "isShort":is_short,"short_basis":short_basis})
    d["videos"]=vids
    d["channel_type"]=ctype
    d["channel_type_note"]=dur_note
    d["n_scraped"]=len(vids)
    d["n_shorts"]=sum(1 for v in vids if v["isShort"])
    d["n_long"]=sum(1 for v in vids if not v["isShort"])
    # exact watch-seconds UPPER BOUND (views*dur), nur wo beides exakt/vorhanden
    ws=[(v["views"],v["dur_secs"]) for v in vids if isinstance(v["views"],int) and v["dur_secs"]]
    d["watch_seconds_upperbound"]= sum(vw*ds for vw,ds in ws) if ws else None
    d["watch_hours_upperbound"]= round(d["watch_seconds_upperbound"]/3600) if d["watch_seconds_upperbound"] else None
    d["watch_ub_basis"]= f"sum(views*full_duration) ueber {len(ws)} videos (=100%-Retention-Obergrenze, NICHT reale Watch-Std)" if ws else "keine_dur+views_paare"
    d["rss_entries"]=rss
    json.dump(d,open(fn,"w"),ensure_ascii=False)
    print(f"{h:24s} type={ctype:6s} n={len(vids):3d} short={d['n_shorts']:3d} long={d['n_long']:3d} watch_h_UB={d['watch_hours_upperbound']}")
print("REPROCESS_DONE")
