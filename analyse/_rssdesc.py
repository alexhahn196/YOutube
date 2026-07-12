import json
for h in ["Cosmicus-w6s","TheSpaceRaceYT","DestinySpace","Proof-n9y"]:
    d=json.load(open("space/"+h+".json"))
    print("\n===== %s ====="%h)
    shown=0
    for v in d["all_videos"]:
        if v.get("desc_rss") and shown<2:
            desc=v["desc_rss"].replace(chr(10)," / ")
            print("VIDEO: %s (%s views)"%(str(v['title'])[:55],f"{v['views']:,}"))
            print("  DESC: "+desc[:300])
            print()
            shown+=1
