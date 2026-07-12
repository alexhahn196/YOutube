# -*- coding: utf-8 -*-
"""Sammelt pro Kanal: about, /videos, /shorts, RSS. Parst und speichert JSON.
Resumierbar (ueberspringt bereits vorhandene JSON). NICHTS geschaetzt: nicht sauber
extrahierbare Werte -> None + Vermerk in data_quality."""
import re, json, os, sys, html
from fetchlib import fetch

OUT=os.path.join(os.path.dirname(__file__),"channels")
os.makedirs(OUT,exist_ok=True)

def norm_abbrev(s):
    """'1.2M' -> 1200000 (gerundet, YouTube-Anzeige). '' -> None."""
    if s is None: return None
    s=s.replace(",","").strip()
    m=re.match(r'^([\d.]+)\s*([KMB]?)$',s)
    if not m: return None
    return int(float(m.group(1))*{'':1,'K':1e3,'M':1e6,'B':1e9}[m.group(2)])

def sxt(pattern, text, grp=1):
    m=re.search(pattern,text)
    return m.group(grp) if m else None

def parse_about(h, txt):
    d={"data_quality":[]}
    d["channel_id"]=sxt(r'"externalId":"(UC[\w-]+)"',txt)
    # subs (abbreviated on about page)
    d["subs_text"]=sxt(r'"subscriberCountText":"([^"]*?) subscribers?"',txt)
    d["subs"]=norm_abbrev(d["subs_text"]) if d["subs_text"] else None
    if d["subs"] is None: d["data_quality"].append("subs:not_found")
    # total views (EXACT on about page)
    tv=sxt(r'"viewCountText":"([\d,]+) views?"',txt)
    d["total_channel_views"]=int(tv.replace(",","")) if tv else None
    if d["total_channel_views"] is None: d["data_quality"].append("total_views:not_found")
    # video count (exact)
    vc=sxt(r'"videoCountText":"([\d,]+) videos?"',txt)
    d["video_count"]=int(vc.replace(",","")) if vc else None
    d["join_text"]=sxt(r'"joinedDateText":\{"content":"Joined ([^"]+)"',txt)
    d["country"]=sxt(r'"country":"([^"]+)"',txt)
    # monetization signals
    d["has_sponsor_button"]=("sponsorButtonRenderer" in txt) or ("membershipsPortalRenderer" in txt)
    d["has_store_tab"]=("merchShelfRenderer" in txt) or bool(re.search(r'"tabRenderer".{0,200}"(Store|Shopping)"',txt))
    # external links
    links=[]
    for m in re.finditer(r'"channelExternalLinkViewModel":\{"title":\{"content":"([^"]*)"\},"link":\{"content":"([^"]*)"',txt):
        links.append({"title":m.group(1),"url":m.group(2)})
    if not links:
        for m in re.finditer(r'\{"url":"(https?://[^"]+)","startIndex"',txt):
            links.append({"title":None,"url":m.group(1)})
    d["external_links"]=links[:10]
    return d

VID_RE=re.compile(r'"contentId":"([\w-]{11})"')
def parse_tab(txt, is_shorts_tab):
    """lockupViewModel-Bloecke -> Liste {videoId,title,views_abbrev,published_text,has_duration}."""
    items=[]
    for chunk in txt.split('"lockupViewModel"')[1:]:
        vid=None
        mv=VID_RE.search(chunk)
        if mv: vid=mv.group(1)
        if not vid: continue
        title=None
        mt=re.search(r'"title":\{"content":"((?:[^"\\]|\\.)*?)"\}',chunk)
        if mt: title=html.unescape(mt.group(1).encode().decode('unicode_escape','ignore')) if '\\u' in mt.group(1) else html.unescape(mt.group(1))
        va=re.search(r'"([\d.,]+[KMB]?) views"',chunk)
        pub=re.search(r'"content":"([^"]*? ago)"',chunk)
        dur=re.search(r'"text":"(\d{1,2}:\d{2}(?::\d{2})?)"',chunk)
        items.append({"videoId":vid,"title":title,
                      "views_abbrev": norm_abbrev(va.group(1)) if va else None,
                      "published_text": pub.group(1) if pub else None,
                      "has_duration": bool(dur),
                      "from_shorts_tab": is_shorts_tab})
    # dedupe by videoId keep first
    seen=set(); out=[]
    for it in items:
        if it["videoId"] in seen: continue
        seen.add(it["videoId"]); out.append(it)
    return out

def parse_rss(txt):
    """RSS -> exakte views (media:statistics), exakte timestamps, descriptions."""
    ents=[]
    for e in txt.split("<entry>")[1:]:
        vid=sxt(r'<yt:videoId>([\w-]+)</yt:videoId>',e)
        title=sxt(r'<title>([^<]*)</title>',e)
        pub=sxt(r'<published>([^<]+)</published>',e)
        views=sxt(r'<media:statistics views="(\d+)"',e)
        desc=sxt(r'<media:description>((?:.|\n)*?)</media:description>',e)
        ents.append({"videoId":vid,"title":html.unescape(title) if title else None,
                     "published_ts":pub,
                     "views_exact": int(views) if views else None,
                     "description": html.unescape(desc) if desc else None})
    return ents

AFF=re.compile(r'(amzn\.to|amazon\.[a-z.]+/|bit\.ly|linktr\.ee|/ref=|utm_|patreon|ko-fi|buymeacoffee|gumroad|shopify|discord\.gg|sponsor|paid promotion|use code|promo code|affiliate)',re.I)

def gather_one(h):
    fn=os.path.join(OUT,h.replace("/","_")+".json")
    if os.path.exists(fn):
        return "skip"
    rec={"handle":h}
    ab,abc,abn=fetch(f"https://www.youtube.com/@{h}/about","about__"+h.replace("/","_")+".html")
    if abc!=200 or len(ab)<1000:
        rec["data_quality"]=["about:fetch_failed:"+str(abn)]
        json.dump(rec,open(fn,"w"),ensure_ascii=False)
        return "fail_about"
    ab_parsed=parse_about(h,ab)
    rec.update(ab_parsed)
    cid=rec.get("channel_id")
    # videos + shorts
    vt,vc_,vn=fetch(f"https://www.youtube.com/@{h}/videos","videos__"+h.replace("/","_")+".html")
    st,sc_,sn=fetch(f"https://www.youtube.com/@{h}/shorts","shorts__"+h.replace("/","_")+".html")
    long_items=parse_tab(vt,False) if vc_==200 else []
    short_items=parse_tab(st,True) if sc_==200 else []
    if vc_!=200: rec["data_quality"].append("videos_tab:"+str(vn))
    if sc_!=200: rec["data_quality"].append("shorts_tab:"+str(sn))
    shorts_ids=set(it["videoId"] for it in short_items)
    # RSS exact
    rss_entries=[]
    if cid:
        rt,rc_,rn=fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}","rss__"+h.replace("/","_")+".xml")
        if rc_==200: rss_entries=parse_rss(rt)
        else: rec["data_quality"].append("rss:"+str(rn))
    else:
        rec["data_quality"].append("channel_id:not_found->no_rss")
    exact_views={e["videoId"]:e["views_exact"] for e in rss_entries if e["videoId"] and e["views_exact"] is not None}
    ts_map={e["videoId"]:e["published_ts"] for e in rss_entries if e["videoId"]}
    # merge unified video list
    vids={}
    for it in long_items+short_items:
        vid=it["videoId"]
        if vid not in vids: vids[vid]=dict(it)
    # classify isShort: in shorts tab OR (in videos tab without duration)
    unified=[]
    for vid,it in vids.items():
        is_short = it["from_shorts_tab"] or (vid in shorts_ids) or (not it["has_duration"])
        vx = exact_views.get(vid)
        unified.append({
            "videoId":vid,"title":it["title"],
            "views": vx if vx is not None else it["views_abbrev"],
            "views_source": "rss_exact" if vx is not None else ("page_abbrev" if it["views_abbrev"] is not None else "none"),
            "published_text": it["published_text"],
            "published_ts": ts_map.get(vid),
            "isShort": is_short,
        })
    rec["videos"]=unified
    rec["n_scraped"]=len(unified)
    rec["n_shorts_scraped"]=sum(1 for v in unified if v["isShort"])
    rec["n_long_scraped"]=sum(1 for v in unified if not v["isShort"])
    # monetization from last 5 descriptions
    descs=[e["description"] or "" for e in rss_entries[:5]]
    rec["desc_affiliate_hits"]=sorted(set(m.group(1).lower() for d in descs for m in AFF.finditer(d)))
    rec["off_platform_monetization"]= bool(rec["desc_affiliate_hits"]) or rec.get("has_sponsor_button") or rec.get("has_store_tab") or bool(rec.get("external_links"))
    rec["rss_entries"]=rss_entries  # for Check E (timestamps) + descriptions
    json.dump(rec,open(fn,"w"),ensure_ascii=False)
    return "ok"

if __name__=="__main__":
    handles=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    done=0
    for i,h in enumerate(handles):
        r=gather_one(h)
        done+=1
        print(f"[{i+1}/{len(handles)}] {h}: {r}",flush=True)
    print("GATHER_DONE",done)
