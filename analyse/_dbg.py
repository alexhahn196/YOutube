import json,os
for h in ['Bestorytales','Gaonstory-q1p','HiddenPower-e9n','AaluTamatarTales','MovidTV1']:
    d=json.load(open('channels/'+h+'.json'))
    print("=== %s | vcount=%s n_scraped=%s shorts=%s long=%s dq=%s"%(
        h,d.get('video_count'),d.get('n_scraped'),d.get('n_shorts_scraped'),d.get('n_long_scraped'),d.get('data_quality')))
    for v in d.get('videos',[])[:4]:
        print("   short=%-5s views=%-9s src=%-11s | %s"%(str(v['isShort']),str(v['views']),v['views_source'],str(v['title'])[:38]))
    print("   rss_entries:",len(d.get('rss_entries',[])), "raw video file bytes:", os.path.getsize('raw/videos__%s.html'%h) if os.path.exists('raw/videos__%s.html'%h) else 'NA')
