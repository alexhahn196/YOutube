# -*- coding: utf-8 -*-
"""CHECK D Auswertung: Basisrate der Welle aus channels_d/m__*.json + Kohorten nach Nische."""
import json, glob, os, csv, re
from statistics import median
from collections import defaultdict
HERE=os.path.dirname(__file__)
recs=[json.load(open(f)) for f in glob.glob(os.path.join(HERE,"channels_d","m__*.json"))]
n=len(recs)
hits=[r for r in recs if r["hit_480k"]]
undet=[r for r in recs if not r.get("hit_determinable")]
tops=[r["max_video_views"] for r in recs if isinstance(r["max_video_views"],int)]
med=int(median(tops)) if tops else None
print("=== CHECK D — Basisrate der Klon-Welle ===")
print(f"neue Kleinkanäle (neu<90T + <200k Abos) gescrapt: N = {n}")
print(f"davon mit >=480k-Hit (im Scrape-Fenster bestätigt): M = {len(hits)}")
print(f"Trefferquote M/N = {len(hits)/n*100:.1f}%  (harte Untergrenze: ältere Hits ausserhalb Fenster nicht erfasst)")
print(f"Kanäle mit unbestimmbarem Hit (total>=480k aber kein Video>=480k im Fenster): {len(undet)}")
print(f"Median Top-Video-Views über GESAMTE Kohorte (n={len(tops)}): {med:,}")
print()
print("Kanäle mit >=480k-Hit:")
for r in sorted(hits,key=lambda x:-x["max_video_views"]):
    print(f"   {r['handle']:28s} max={r['max_video_views']:>10,} subs={r['subs']} join={r['join_date']}")
# Wellen/Nische aus Handle-Namensmuster
def wave(h):
    hl=h.lower()
    for kw,name in [('aalu','Gemüse-Aalu'),('sabzi','Gemüse-Sabzi'),('veg','Gemüse-Veg'),
                    ('giant','GiantFood'),('mango','GiantFood'),('drama','Drama/Karma'),
                    ('karma','Drama/Karma'),('revenge','Drama/Karma'),('billionaire','Billionaire'),
                    ('tales','Tales/Story'),('story','Tales/Story'),('cartoon','Cartoon'),
                    ('toon','Cartoon'),('bahu','Sasural'),('sasural','Sasural'),('asmr','ASMR')]:
        if kw in hl: return name
    return 'sonstige'
byw=defaultdict(list)
for r in recs: byw[wave(r["handle"])].append(r)
print("\nBasisrate je Welle/Nische:")
crows=[]
for w in sorted(byw,key=lambda x:-len(byw[x])):
    ch=byw[w]; nh=sum(1 for r in ch if r["hit_480k"])
    tp=[r["max_video_views"] for r in ch if isinstance(r["max_video_views"],int)]
    m=int(median(tp)) if tp else None
    print(f"   {w:16s} N={len(ch):3d}  Hits={nh:2d}  Quote={nh/len(ch)*100:4.1f}%  Median-Top={m:,}")
    crows.append({"kohorte_start_monat":f"WELLE:{w}","n_kanaele":len(ch),"n_mit_480k_hit":nh,
                  "median_top_video_views":m,"quelle":"Check_D_77er_Wellen-Kohorte(unverzerrt)"})
# Gesamt-Zeile
crows.append({"kohorte_start_monat":"WELLE:GESAMT","n_kanaele":n,"n_mit_480k_hit":len(hits),
              "median_top_video_views":med,"quelle":"Check_D_Basisrate_gesamt"})
# an kohorten.csv anhaengen
with open(os.path.join(HERE,"kohorten.csv"),"a",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["kohorte_start_monat","n_kanaele","n_mit_480k_hit","median_top_video_views","quelle"])
    for cr in crows: w.writerow(cr)
print("\nan kohorten.csv angehängt")
# Rueckgabe fuer BEFUND
json.dump({"N":n,"M":len(hits),"quote_pct":round(len(hits)/n*100,1),"median_top":med,"undet":len(undet)},
          open(os.path.join(HERE,"_d_summary.json"),"w"))
