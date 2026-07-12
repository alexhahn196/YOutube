# -*- coding: utf-8 -*-
"""CHECK D — Basisrate der Klon-Welle. 260 Handles -> filter new(<90d)+small(<200k) -> ~77.
Fuer die 77: max Video-Views (RSS exakt + Seiten-Abbrev), Trefferquote >=480k.
Gedrosselt, resumierbar, Roh in ./raw_d/. Nichts geschaetzt."""
import re, os, json, sys
sys.path.insert(0,os.path.dirname(__file__))
import fetchlib
fetchlib.RAW=os.path.join(os.path.dirname(__file__),"..","raw_d"); os.makedirs(fetchlib.RAW,exist_ok=True)
from fetchlib import fetch
OUT=os.path.join(os.path.dirname(__file__),"channels_d"); os.makedirs(OUT,exist_ok=True)
MONTHS={m:i for i,m in enumerate(["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}

def norm(s):
    s=s.replace(",","").strip(); m=re.match(r'^([\d.]+)\s*([KMB]?)$',s)
    return int(float(m.group(1))*{'':1,'K':1e3,'M':1e6,'B':1e9}[m.group(2)]) if m else None

def about_info(h):
    body,code,note=fetch(f"https://www.youtube.com/@{h}/about","about__"+h+".html")
    if code!=200: return {"handle":h,"stage":"about","error":note}
    subs_t=re.search(r'"subscriberCountText":"([^"]*?) subscribers?"',body)
    subs=norm(subs_t.group(1)) if subs_t else None
    jt=re.search(r'"joinedDateText":\{"content":"Joined ([A-Za-z]+) (\d+), (\d{4})"',body)
    join=None; jok=False
    if jt:
        join=f"{jt.group(3)}-{MONTHS.get(jt.group(1)[:3],0):02d}-{int(jt.group(2)):02d}"
        jok=(jt.group(3)=="2026" and MONTHS.get(jt.group(1)[:3],0)>=4)  # <90d ~ Apr+ 2026
    tv=re.search(r'"viewCountText":"([\d,]+) views?"',body)
    total=int(tv.group(1).replace(",","")) if tv else None
    cid=re.search(r'"externalId":"(UC[\w-]+)"',body)
    return {"handle":h,"subs":subs,"join_date":join,"is_new":jok,"total_channel_views":total,
            "channel_id":cid.group(1) if cid else None,
            "small_new": (jok and subs is not None and subs<200000)}

def max_views(h, cid):
    mx=0; srcs=[]; note=[]
    for tab in ["videos","shorts"]:
        body,code,_=fetch(f"https://www.youtube.com/@{h}/{tab}",f"{tab}__{h}.html")
        if code!=200: note.append(f"{tab}:{code}"); continue
        for v in re.findall(r'"([\d.,]+[KMB]?) views"',body):
            n=norm(v)
            if n and n>mx: mx=n
    # RSS exact
    if cid:
        rss,rc,_=fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}","rss__"+h+".xml")
        if rc==200:
            for m in re.findall(r'<media:statistics views="(\d+)"',rss):
                if int(m)>mx: mx=int(m)
        else: note.append("rss:"+str(rc))
    return mx, ";".join(note)

if __name__=="__main__":
    handles=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    # Stage 1: about
    infos={}
    for i,h in enumerate(handles):
        fn=os.path.join(OUT,"a__"+h+".json")
        if os.path.exists(fn): infos[h]=json.load(open(fn));
        else:
            info=about_info(h); json.dump(info,open(fn,"w"),ensure_ascii=False); infos[h]=info
        print(f"[about {i+1}/{len(handles)}] {h}: subs={infos[h].get('subs')} join={infos[h].get('join_date')} small_new={infos[h].get('small_new')}",flush=True)
    smallnew=[h for h in handles if infos[h].get("small_new")]
    print(f"SMALL_NEW_COUNT {len(smallnew)}",flush=True)
    # Stage 2: max views for small_new
    for i,h in enumerate(smallnew):
        fn=os.path.join(OUT,"m__"+h+".json")
        if os.path.exists(fn):
            print(f"[max {i+1}/{len(smallnew)}] {h}: cached",flush=True); continue
        mx,note=max_views(h, infos[h].get("channel_id"))
        rec={"handle":h,"subs":infos[h]["subs"],"join_date":infos[h]["join_date"],
             "total_channel_views":infos[h].get("total_channel_views"),
             "max_video_views":mx,"note":note,
             "hit_480k": mx>=480000,
             "hit_determinable": (mx>=480000) or (infos[h].get("total_channel_views") is not None and infos[h]["total_channel_views"]<480000)}
        json.dump(rec,open(fn,"w"),ensure_ascii=False)
        print(f"[max {i+1}/{len(smallnew)}] {h}: max={mx:,} hit={rec['hit_480k']} {note}",flush=True)
    print("GATHER_D_DONE",flush=True)
