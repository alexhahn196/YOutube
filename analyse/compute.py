# -*- coding: utf-8 -*-
"""Liest channels/*.json und berechnet Check A, B, C, E. Nichts geschaetzt:
fehlende Werte -> None + data_quality. Schreibt kanaele_full.csv (+ _full.json)."""
import json, os, re, csv, glob, hashlib
from datetime import date, datetime
from statistics import median

HERE=os.path.dirname(__file__)
TODAY=date(2026,7,12)
MONTHS={m:i for i,m in enumerate(["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"])}

def parse_join(t):
    if not t: return None
    m=re.match(r'([A-Za-z]+) (\d+), (\d{4})',t)
    if not m: return None
    mo=MONTHS.get(m.group(1)[:3],0)
    if not mo: return None
    return date(int(m.group(3)),mo,int(m.group(2)))

def ts_date(ts):
    if not ts: return None
    try: return datetime.fromisoformat(ts.replace("Z","+00:00")).date()
    except: return None

def pctile(sorted_vals, p):
    if not sorted_vals: return None
    k=(len(sorted_vals)-1)*p
    f=int(k)
    if f+1<len(sorted_vals): return sorted_vals[f]+(sorted_vals[f+1]-sorted_vals[f])*(k-f)
    return sorted_vals[f]

def norm_boiler(descs):
    """Beschreibungs-Boilerplate normalisieren (Hashtags/Zahlen/URLs raus) + hash."""
    joined=" ".join(descs)
    j=re.sub(r'https?://\S+',' ',joined)
    j=re.sub(r'#\w+',' ',j); j=re.sub(r'\d+',' ',j); j=re.sub(r'\s+',' ',j).strip().lower()
    j=j[:400]
    return hashlib.md5(j.encode()).hexdigest()[:12] if j else None

rows=[]
for fn in sorted(glob.glob(os.path.join(HERE,"channels","*.json"))):
    d=json.load(open(fn))
    h=d["handle"]; dq=list(d.get("data_quality",[]))
    r={"handle":h}
    subs=d.get("subs"); total=d.get("total_channel_views"); vcount=d.get("video_count")
    r["subs"]=subs; r["total_channel_views"]=total; r["video_count"]=vcount
    vids=d.get("videos",[])
    r["n_scraped"]=d.get("n_scraped"); r["n_shorts_scraped"]=d.get("n_shorts"); r["n_long_scraped"]=d.get("n_long")
    # views list (only where we have a number)
    vv=[v["views"] for v in vids if isinstance(v.get("views"),int)]
    n_noviews=sum(1 for v in vids if not isinstance(v.get("views"),int))
    if n_noviews: dq.append(f"views_missing_on_{n_noviews}_vids")
    if vcount and d.get("n_scraped") and vcount>d["n_scraped"]:
        dq.append(f"scraped_{d['n_scraped']}_of_{vcount}_vids(median_on_newest)")
    # ---- Check A ----
    if vv:
        sv=sorted(vv)
        r["median_views"]=int(median(sv)); r["p25"]=int(pctile(sv,.25)); r["p75"]=int(pctile(sv,.75))
        r["max_views"]=max(sv); r["n_ueber_100k"]=sum(1 for x in sv if x>=100000); r["n_ueber_480k"]=sum(1 for x in sv if x>=480000)
        base=vcount if vcount else len(sv)
        r["hit_ratio"]=round(r["n_ueber_480k"]/base,4) if base else None
        r["median_to_max_ratio"]=round(r["median_views"]/r["max_views"],4) if r["max_views"] else None
    else:
        for k in ["median_views","p25","p75","max_views","n_ueber_100k","n_ueber_480k","hit_ratio","median_to_max_ratio"]: r[k]=None
        dq.append("no_view_data->A_null")
    # uploads/tag
    jd=parse_join(d.get("join_text")); r["join_date"]=jd.isoformat() if jd else None
    ts=[ts_date(v.get("published_ts")) for v in vids if v.get("published_ts")]
    ts=[x for x in ts if x]
    if jd and ts:
        span=(max(ts)-jd).days or 1
        r["uploads_pro_tag"]=round((vcount if vcount else len(vids))/span,3)
    else: r["uploads_pro_tag"]=None
    # verdict_A
    mv=r["median_views"]; hr=r["hit_ratio"]
    if mv is None or hr is None: r["verdict_A"]="UNKLAR(no_data)"
    elif mv<10000 and hr<0.05: r["verdict_A"]="LOTTERIE"
    elif mv>=100000: r["verdict_A"]="SYSTEM"
    else: r["verdict_A"]="UNKLAR"
    # ---- Check B (korrigiert: Kanal-Typ per Dauer) ----
    ctype=d.get("channel_type"); r["channel_type"]=ctype; r["channel_type_note"]=d.get("channel_type_note")
    r["n_shorts"]=d.get("n_shorts"); r["n_long"]=d.get("n_long")
    r["subs_ge_1000"]= (subs is not None and subs>=1000)
    r["subs_ge_500"]= (subs is not None and subs>=500)
    if ctype=="SHORTS":
        if d.get("n_long")==0 and total is not None:
            r["shorts_views_90d"]=total; r["shorts_views_90d_basis"]="pure_shorts=exact_total_views"
        else:
            ssum=sum(v["views"] for v in vids if v.get("isShort") and isinstance(v.get("views"),int))
            miss=sum(1 for v in vids if v.get("isShort") and not isinstance(v.get("views"),int))
            r["shorts_views_90d"]=ssum
            r["shorts_views_90d_basis"]=f"sum_shorts_views(missing_on_{miss})" if miss else "sum_shorts_views"
    else:
        r["shorts_views_90d"]=None
        r["shorts_views_90d_basis"]="N/A_long_form_channel(shorts_gate_gilt_nicht)"
    sv90=r["shorts_views_90d"]
    # Nutzer-Formel: ypp_ad_eligible nur ueber Shorts-Pfad sinnvoll -> nur Shorts-Kanaele koennen TRUE sein
    r["ypp_ad_eligible"]= (ctype=="SHORTS" and subs is not None and subs>=1000 and sv90 is not None and sv90>=10_000_000)
    r["ypp_fanfund_eligible"]= (ctype=="SHORTS" and subs is not None and subs>=500 and sv90 is not None and sv90>=3_000_000)
    # Long-Form-Gate (4000 Watch-Std) ist extern NICHT messbar -> Obergrenze + noetige Retention ausweisen
    wub=d.get("watch_hours_upperbound"); r["watch_hours_upperbound"]=wub; r["watch_ub_basis"]=d.get("watch_ub_basis")
    r["retention_needed_for_4000h"]= round(4000/wub,4) if (wub and wub>0) else None
    if ctype=="LONG":
        r["longform_ad_eligible"]= "UNBESTIMMBAR(watch_hours_nicht_exponiert)"
    else:
        r["longform_ad_eligible"]="N/A_shorts_channel"
    r["mon_sponsor_button"]=d.get("has_sponsor_button")
    r["mon_store_tab"]=d.get("has_store_tab")
    r["mon_external_links"]=len(d.get("external_links") or [])
    r["mon_affiliate_hits"]=";".join(d.get("desc_affiliate_hits") or [])
    r["off_platform_monetization"]=d.get("off_platform_monetization")
    # ---- Check C ----
    viral=None
    cand=[v for v in vids if isinstance(v.get("views"),int) and v["views"]>=480000]
    if cand:
        viral=max(cand,key=lambda v:v["views"])
        r["viral_video_id"]=viral["videoId"]; r["viral_video_views"]=viral["views"]
        vd=ts_date(viral.get("published_ts"))
        if vd:
            r["viral_video_upload_date"]=vd.isoformat(); r["viral_date_source"]="rss_exact"
            r["days_channel_to_hit"]=(vd-jd).days if jd else None
            r["days_since_hit"]=(TODAY-vd).days
        else:
            r["viral_video_upload_date"]=None; r["viral_date_source"]="published_text:"+str(viral.get("published_text"))
            r["days_channel_to_hit"]=None; r["days_since_hit"]=None
            dq.append("viral_upload_date:only_relative_text")
    else:
        for k in ["viral_video_id","viral_video_views","viral_video_upload_date","viral_date_source","days_channel_to_hit","days_since_hit"]: r[k]=None
        dq.append("no_480k_in_scraped(maybe_older_than_scraped)")
    # ---- Check E ----
    hrs=[]
    for v in vids:
        if v.get("published_ts"):
            try: hrs.append(datetime.fromisoformat(v["published_ts"].replace("Z","+00:00")).hour)
            except: pass
    r["upload_hours_utc"]=";".join(str(x) for x in sorted(set(hrs)))
    from collections import Counter
    r["dominant_upload_hour_utc"]=Counter(hrs).most_common(1)[0][0] if hrs else None
    descs=[e.get("description") or "" for e in d.get("rss_entries",[])[:5]]
    r["desc_boiler_hash"]=norm_boiler(descs)
    doms=sorted(set(re.sub(r'^https?://(www\.)?','',l["url"]).split("/")[0].lower() for l in (d.get("external_links") or []) if l.get("url")))
    r["external_domains"]=";".join(doms)
    r["data_quality"]="; ".join(dq)
    rows.append(r)

# write
cols=["handle","channel_type","channel_type_note","subs","total_channel_views","video_count","n_scraped","n_shorts_scraped","n_long_scraped",
      "median_views","p25","p75","max_views","n_ueber_100k","n_ueber_480k","hit_ratio","median_to_max_ratio","uploads_pro_tag","verdict_A",
      "subs_ge_1000","subs_ge_500","shorts_views_90d","shorts_views_90d_basis","ypp_ad_eligible","ypp_fanfund_eligible",
      "longform_ad_eligible","watch_hours_upperbound","watch_ub_basis","retention_needed_for_4000h",
      "mon_sponsor_button","mon_store_tab","mon_external_links","mon_affiliate_hits","off_platform_monetization",
      "join_date","viral_video_id","viral_video_views","viral_video_upload_date","viral_date_source","days_channel_to_hit","days_since_hit",
      "dominant_upload_hour_utc","upload_hours_utc","desc_boiler_hash","external_domains","data_quality"]
with open(os.path.join(HERE,"kanaele_full.csv"),"w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in rows: w.writerow({k:r.get(k) for k in cols})
json.dump(rows,open(os.path.join(HERE,"_full.json"),"w"),ensure_ascii=False,indent=1)
print("WROTE kanaele_full.csv rows:",len(rows))
