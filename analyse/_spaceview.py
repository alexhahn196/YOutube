import json
def f(n): return f"{n:,}" if isinstance(n,int) else "?"
def mmss(s): return f"{s//60}:{s%60:02d}" if isinstance(s,int) else "?"
for h in ["Cosmicus-w6s","TheSpaceRaceYT","Space_Chip","DestinySpace","Proof-n9y"]:
    d=json.load(open("space/"+h+".json"))
    print("\n"+"="*72)
    print("### %s | subs=%s | vids=%s | join=%s"%(h,f(d['subs']),d['video_count'],d['join']))
    print("Top-Videos (gescrapt):")
    for v in d["top5"]:
        print("  %11s  [%6s]  %s"%(f(v['views']),mmss(v['dur']),str(v['title'])[:60]))
    for w in d["top_watch"]:
        print("  > %s | %s views | %s"%(str(w.get('listed_title'))[:56],f(w.get('views_exact')),mmss(w.get('length_s'))))
        desc=(w.get("description") or "").replace(chr(10)," / ")
        print("    HOOK: "+desc[:190])
        ch=w.get("chapters") or []
        if ch: print("    KAPITEL(%d): "%len(ch)+" | ".join("%s %s"%(c['t'],c['label'][:20]) for c in ch[:7]))
        kw=w.get("keywords") or []
        if kw: print("    TAGS: "+", ".join(kw[:8]))
