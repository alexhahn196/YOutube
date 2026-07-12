import re,os,glob
RAW="raw"
def durs_from(fn):
    if not os.path.exists(fn): return None,0
    t=open(fn).read()
    n_lockup=t.count('"lockupViewModel"')
    ds=re.findall(r'"thumbnailOverlayBadgeViewModel".{0,400}?"text":"(\d{1,2}:\d{2}(?::\d{2})?)"',t)
    if not ds:  # fallback any MM:SS in lockup context
        ds=re.findall(r'"text":"(\d{1,2}:\d{2}(?::\d{2})?)"',t)
    return ds[:8], n_lockup
for h in ['Bestorytales','Gaonstory-q1p','HiddenPower-e9n','AaluTamatarTales','MovidTV1','AALUBIGTV','FuntooBabaTV','TrioHistory111']:
    vd,vn=durs_from(f"{RAW}/videos__{h}.html")
    sd,sn=durs_from(f"{RAW}/shorts__{h}.html")
    def secs(x):
        p=[int(i) for i in x.split(':')]; return p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2]
    vsec=[secs(x) for x in (vd or [])]
    print(f"{h:20s} | /videos lockups={vn} durs={vd} | /shorts lockups={sn} durs_sample={sd[:3] if sd else []}")
