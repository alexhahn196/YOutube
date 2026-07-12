# -*- coding: utf-8 -*-
"""Deep-Dive Top-5 Space-Kanäle. About/videos/shorts/RSS + Watch-Seiten der Top-Videos
(Beschreibung/Kapitel/Hook/Tags/exakte Views). Gedrosselt, Roh nach raw_space/."""
import re, os, json, sys, html
sys.path.insert(0,os.path.dirname(__file__))
import fetchlib
fetchlib.RAW=os.path.join(os.path.dirname(__file__),"..","raw_space"); os.makedirs(fetchlib.RAW,exist_ok=True)
from fetchlib import fetch
OUT=os.path.join(os.path.dirname(__file__),"space"); os.makedirs(OUT,exist_ok=True)

def norm(s):
    if s is None: return None
    s=s.replace(",","").strip(); m=re.match(r'^([\d.]+)\s*([KMB]?)$',s)
    return int(float(m.group(1))*{'':1,'K':1e3,'M':1e6,'B':1e9}[m.group(2)]) if m else None
def dsec(t):
    p=[int(i) for i in t.split(':')]; return p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2]

def parse_tab(t):
    out={}
    if '"lockupViewModel"' in t:
        for c in t.split('"lockupViewModel"')[1:]:
            mid=re.search(r'"contentId":"([\w-]{11})"',c)
            if not mid: continue
            vid=mid.group(1)
            if vid in out: continue
            ti=re.search(r'"title":\{"content":"((?:[^"\\]|\\.)*?)"\}',c)
            va=re.search(r'"([\d.,]+[KMB]?) views"',c); du=re.search(r'"text":"(\d{1,2}:\d{2}(?::\d{2})?)"',c)
            pb=re.search(r'"content":"([^"]*? ago)"',c)
            out[vid]={"title":html.unescape(ti.group(1)) if ti else None,"views_abbrev":norm(va.group(1)) if va else None,
                      "dur":dsec(du.group(1)) if du else None,"pub":pb.group(1) if pb else None}
    else:
        for c in re.split(r'"richItemRenderer"|"videoRenderer"',t)[1:]:
            mid=re.search(r'"videoId":"([\w-]{11})"',c)
            if not mid: continue
            vid=mid.group(1)
            if vid in out: continue
            ti=re.search(r'"title":\{"runs":\[\{"text":"((?:[^"\\]|\\.)*?)"',c) or re.search(r'"title":\{"simpleText":"((?:[^"\\]|\\.)*?)"',c)
            va=re.search(r'"viewCountText":\{"simpleText":"([\d.,]+[KMB]?) views"',c)
            lt=re.search(r'"lengthText":\{.*?"simpleText":"([\d:]+)"',c); pb=re.search(r'"publishedTimeText":\{"simpleText":"([^"]+)"',c)
            out[vid]={"title":html.unescape(ti.group(1)) if ti else None,"views_abbrev":norm(va.group(1)) if va else None,
                      "dur":dsec(lt.group(1)) if lt else None,"pub":pb.group(1) if pb else None}
    return out

def parse_rss(t):
    ents={}
    for e in t.split("<entry>")[1:]:
        vid=re.search(r'<yt:videoId>([\w-]+)',e)
        if not vid: continue
        vw=re.search(r'<media:statistics views="(\d+)"',e); ds=re.search(r'<media:description>((?:.|\n)*?)</media:description>',e)
        pb=re.search(r'<published>([^<]+)',e); ti=re.search(r'<title>([^<]*)',e)
        ents[vid.group(1)]={"views_exact":int(vw.group(1)) if vw else None,"desc":html.unescape(ds.group(1)) if ds else None,
                            "pub_ts":pb.group(1) if pb else None,"title":html.unescape(ti.group(1)) if ti else None}
    return ents

def parse_watch(t):
    d={}
    sd=re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"',t)
    if sd:
        try: d["description"]=bytes(sd.group(1),"utf-8").decode("unicode_escape").encode("latin1","ignore").decode("utf-8","ignore")
        except: d["description"]=sd.group(1)
        d["description"]=d["description"].replace("\\n","\n")
    vc=re.search(r'"viewCount":"(\d+)"',t); d["views_exact"]=int(vc.group(1)) if vc else None
    ls=re.search(r'"lengthSeconds":"(\d+)"',t); d["length_s"]=int(ls.group(1)) if ls else None
    kw=re.search(r'"keywords":\[((?:[^\]])*)\]',t); d["keywords"]=re.findall(r'"([^"]+)"',kw.group(1))[:15] if kw else []
    ti=re.search(r'"title":"((?:[^"\\]|\\.)*?)","lengthSeconds"',t); d["title"]=ti.group(1) if ti else None
    # chapters aus Beschreibung (timestamp am Zeilenanfang)
    ch=[]
    for line in (d.get("description") or "").split("\n"):
        m=re.match(r'\s*((?:\d+:)?\d+:\d{2})\s+(.+)',line.strip())
        if m: ch.append({"t":m.group(1),"label":m.group(2)[:60]})
    d["chapters"]=ch
    return d

def gather(h):
    fn=os.path.join(OUT,h+".json")
    rec={"handle":h}
    ab,c,_=fetch(f"https://www.youtube.com/@{h}/about","about__"+h+".html")
    rec["subs"]=norm((re.search(r'"subscriberCountText":"([^"]*?) subscribers?"',ab) or [None,None])[1] if re.search(r'"subscriberCountText":"([^"]*?) subscribers?"',ab) else None)
    m=re.search(r'"subscriberCountText":"([^"]*?) subscribers?"',ab); rec["subs"]=norm(m.group(1)) if m else None
    m=re.search(r'"viewCountText":"([\d,]+) views?"',ab); rec["total_views"]=int(m.group(1).replace(",","")) if m else None
    m=re.search(r'"videoCountText":"([\d,]+) videos?"',ab); rec["video_count"]=int(m.group(1).replace(",","")) if m else None
    m=re.search(r'"joinedDateText":\{"content":"Joined ([^"]+)"',ab); rec["join"]=m.group(1) if m else None
    m=re.search(r'"externalId":"(UC[\w-]+)"',ab); cid=m.group(1) if m else None; rec["channel_id"]=cid
    vt,_,_=fetch(f"https://www.youtube.com/@{h}/videos","videos__"+h+".html")
    st,_,_=fetch(f"https://www.youtube.com/@{h}/shorts","shorts__"+h+".html")
    vids={**parse_tab(vt),**parse_tab(st)}
    rss=parse_rss(fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}","rss__"+h+".xml")[0]) if cid else {}
    # merge
    merged=[]
    for vid,v in vids.items():
        ex=rss.get(vid,{})
        merged.append({"videoId":vid,"title":v["title"] or ex.get("title"),
                       "views": ex.get("views_exact") if ex.get("views_exact") is not None else v["views_abbrev"],
                       "views_exact": ex.get("views_exact") is not None,
                       "dur":v["dur"],"pub":v["pub"],"pub_ts":ex.get("pub_ts"),"desc_rss":ex.get("desc")})
    merged=[v for v in merged if isinstance(v["views"],int)]
    merged.sort(key=lambda x:-x["views"])
    rec["all_videos"]=merged
    rec["top5"]=merged[:5]
    # Watch-Seiten der Top-3
    watch=[]
    for v in merged[:3]:
        wt,_,_=fetch(f"https://www.youtube.com/watch?v={v['videoId']}","watch__"+v["videoId"]+".html")
        w=parse_watch(wt); w["videoId"]=v["videoId"]; w["listed_title"]=v["title"]; watch.append(w)
    rec["top_watch"]=watch
    json.dump(rec,open(fn,"w"),ensure_ascii=False)
    print(f"{h}: subs={rec['subs']} vids={rec['video_count']} scraped={len(merged)} top={merged[0]['views'] if merged else 0:,}")
    return rec

if __name__=="__main__":
    for h in ["Cosmicus-w6s","TheSpaceRaceYT","Space_Chip","DestinySpace","Proof-n9y"]:
        gather(h)
    print("SPACE_GATHER_DONE")
