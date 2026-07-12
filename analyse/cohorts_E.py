# -*- coding: utf-8 -*-
import json, csv, re
from collections import defaultdict, Counter
from statistics import median
from datetime import date
rows=json.load(open('_full.json'))
verified=json.load(open('_verified33.json'))  # original: alle haben verifizierten >=480k topVideo
topmap={v['handle']:v for v in verified}

# ---- CHECK C ----
# Alle 33 wurden fuer >=480k-Hit selektiert (topVideo aus Erst-Recherche). join_date frisch gescrapt.
def jd(r):
    return date.fromisoformat(r['join_date']) if r.get('join_date') else None
withhit=[r for r in rows if (topmap.get(r['handle'],{}).get('topVideo',0) or 0)>=480000]
joins=[(r['handle'],jd(r),topmap[r['handle']]['topVideo']) for r in withhit if jd(r)]
latest=max(joins,key=lambda x:x[1])
after_june=[j for j in joins if j[1]>=date(2026,6,1)]
print("=== CHECK C ===")
print("Kanäle mit verifiziertem >=480k-Hit:",len(withhit),"/ 33 (alle selektiert)")
print("(a) SPÄTESTES join_date mit >=480k-Hit:",latest[1].isoformat(),"->",latest[0],f"(Hit {latest[2]:,})")
print("(b) Kanäle gestartet NACH 01.06.2026 mit Viral-Hit:",len(after_june))
for h,d,t in sorted(after_june,key=lambda x:-x[1].toordinal()):
    print(f"     {d.isoformat()}  {h:24s}  Hit {t:,}")

# Kohorten-Tabelle nach Start-Monat
coh=defaultdict(list)
for r in rows:
    d=jd(r)
    if not d: continue
    coh[f"{d.year}-{d.month:02d}"].append(r)
coh_rows=[]
for mo in sorted(coh):
    chans=coh[mo]
    nhit=sum(1 for r in chans if (topmap.get(r['handle'],{}).get('topVideo',0) or 0)>=480000)
    tops=[topmap.get(r['handle'],{}).get('topVideo',0) or 0 for r in chans]
    med=int(median(tops)) if tops else None
    coh_rows.append({"kohorte_start_monat":mo,"n_kanaele":len(chans),"n_mit_480k_hit":nhit,
                     "median_top_video_views":med,"quelle":"33_verifizierte(selektiert_auf_hit)"})
    print(f"  Kohorte {mo}: {len(chans)} Kanäle, {nhit} mit >=480k, Median-Top-Video {med:,}")

# ---- CHECK E ----
print("\n=== CHECK E — Netzwerk-Cluster ===")
# 1) gleiche Beschreibungs-Boilerplate (hash)
byhash=defaultdict(list)
for r in rows:
    if r.get('desc_boiler_hash'): byhash[r['desc_boiler_hash']].append(r['handle'])
dup_hash={k:v for k,v in byhash.items() if len(v)>1}
print("Gleiche Beschreibungs-Boilerplate (=selber Operator-Verdacht):")
if dup_hash:
    for k,v in dup_hash.items(): print(f"   hash {k}: {v}")
else: print("   keine identischen Boilerplate-Hashes")
# 2) gleiche externe Domain
bydom=defaultdict(list)
for r in rows:
    for dom in (r.get('external_domains') or "").split(";"):
        if dom: bydom[dom].append(r['handle'])
dup_dom={k:v for k,v in bydom.items() if len(v)>1}
print("Gleiche externe Domain/Link:")
if dup_dom:
    for k,v in dup_dom.items(): print(f"   {k}: {v}")
else: print("   keine geteilten externen Domains")
# 3) Upload-Stunde (UTC) Histogramm
print("Dominante Upload-Stunde (UTC) je Kanal:")
hourc=Counter(r['dominant_upload_hour_utc'] for r in rows if r.get('dominant_upload_hour_utc') is not None)
print("   Verteilung:",dict(sorted(hourc.items())))
# 4) Handle-Namensmuster (Wellen)
patterns=defaultdict(list)
for r in rows:
    h=r['handle'].lower()
    for kw in ['aalu','sabzi','veg','drama','giant','tales','story','cartoon','toon','mango']:
        if kw in h: patterns[kw].append(r['handle']); break
print("Handle-Namensmuster (Wellen-Indikator):")
for k,v in patterns.items():
    if len(v)>1: print(f"   '{k}': {v}")

# write kohorten.csv (C part; D wird angehaengt)
with open('kohorten.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=["kohorte_start_monat","n_kanaele","n_mit_480k_hit","median_top_video_views","quelle"])
    w.writeheader()
    for cr in coh_rows: w.writerow(cr)
print("\nWROTE kohorten.csv (C-Teil)")
