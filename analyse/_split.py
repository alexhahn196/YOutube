import re,os,glob,json
RAW="raw"
def parse_durs(fn):
    if not os.path.exists(fn): return {}
    t=open(fn).read()
    out={}
    for chunk in t.split('"lockupViewModel"')[1:]:
        mid=re.search(r'"contentId":"([\w-]{11})"',chunk)
        md=re.search(r'"text":"(\d{1,2}:\d{2}(?::\d{2})?)"',chunk)
        if mid and md:
            p=[int(i) for i in md.group(1).split(':')]
            sec=p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2]
            out[mid.group(1)]=sec
    return out
handles=[l.strip() for l in open('analyse/_handles33.txt') if l.strip()]
print("%-24s %6s %6s %8s  %s"%("handle","nDur","nShort","nLong","median_dur_s / classify"))
summary=[]
for h in handles:
    d=parse_durs(f"{RAW}/videos__{h}.html"); d.update(parse_durs(f"{RAW}/shorts__{h}.html"))
    durs=sorted(d.values())
    if not durs:
        print("%-24s %6s"%(h,"0")," NO_DUR_DATA"); summary.append((h,None)); continue
    md=durs[len(durs)//2]
    ns=sum(1 for x in durs if x<=180); nl=sum(1 for x in durs if x>180)
    typ="SHORTS" if md<=180 else "LONG"
    print("%-24s %6d %6d %8d  median=%ds -> %s"%(h,len(durs),ns,nl,md,typ))
    summary.append((h,typ))
from collections import Counter
print("\nTYP-Verteilung:",Counter(t for _,t in summary))
