import sys; sys.path.insert(0,'analyse')
from fetchlib import fetch
import re
for h in ['thedramatalesx','MovidTV1','LOVERSINUSA','CheathanMust']:
    for tab in ['videos','shorts']:
        body,code,note=fetch(f"https://www.youtube.com/@{h}/{tab}",f"{tab}__{h}.html")
        n=body.count('"lockupViewModel"'); nr=body.count('richItemRenderer'); nre=body.count('reelItemRenderer')
        # durations
        durs=[]
        for chunk in body.split('"lockupViewModel"')[1:]:
            md=re.search(r'"text":"(\d{1,2}:\d{2}(?::\d{2})?)"',chunk)
            if md:
                p=[int(i) for i in md.group(1).split(':')]; durs.append(p[0]*60+p[1] if len(p)==2 else p[0]*3600+p[1]*60+p[2])
        print(f"{h:16s} /{tab:6s} code={code} lockup={n} richItem={nr} reelItem={nre} note={note} durs_sample={sorted(durs)[:6]}")
