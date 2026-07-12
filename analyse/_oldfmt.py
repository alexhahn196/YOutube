import re,os
RAW="raw"
def parse_old(fn):
    if not os.path.exists(fn): return []
    t=open(fn).read()
    out=[]
    for chunk in re.split(r'"richItemRenderer"|"videoRenderer"',t)[1:]:
        vid=re.search(r'"videoId":"([\w-]{11})"',chunk)
        if not vid: continue
        # duration
        lt=re.search(r'"lengthText":\{"accessibility".*?"simpleText":"([\d:]+)"',chunk) or re.search(r'"lengthText":\{"simpleText":"([\d:]+)"',chunk)
        vc=re.search(r'"viewCountText":\{"simpleText":"([\d.,]+[KMB]?) views"',chunk)
        sec=None
        if lt:
            p=[int(i) for i in lt.group(1).split(':')]; sec=p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2]
        out.append((vid.group(1),sec))
    # dedupe
    seen=set(); o=[]
    for v,s in out:
        if v in seen: continue
        seen.add(v); o.append((v,s))
    return o
for h in ['thedramatalesx','MovidTV1','LOVERSINUSA','CheathanMust']:
    vv=parse_old(f"{RAW}/videos__{h}.html"); ss=parse_old(f"{RAW}/shorts__{h}.html")
    alld=[s for _,s in (vv+ss) if s is not None]
    n_none=sum(1 for _,s in (vv+ss) if s is None)
    if alld:
        alld_s=sorted(alld); md=alld_s[len(alld_s)//2]
        ns=sum(1 for x in alld if x<=180); nl=sum(1 for x in alld if x>180)
        print(f"{h:16s} videos_items={len(vv)} shorts_items={len(ss)} with_dur={len(alld)} no_dur={n_none} median={md}s shorts<=180:{ns} long:{nl} -> {'SHORTS' if md<=180 else 'LONG'}")
    else:
        print(f"{h:16s} videos_items={len(vv)} shorts_items={len(ss)} NO DURATIONS (n_none={n_none})")
