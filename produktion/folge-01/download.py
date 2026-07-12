#!/usr/bin/env python3
"""Download rendered clips into clips/<clipid>.mp4 using manifest (clip->job) + url_map.json (job->url)."""
import json, os, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
CLIPDIR = os.path.join(HERE, "clips"); os.makedirs(CLIPDIR, exist_ok=True)
m = json.load(open(os.path.join(HERE, "manifest.json")))
urlmap = json.load(open(os.path.join(HERE, "url_map.json")))
missing = []
for c in m["clips"]:
    job = c["video_job"]
    url = urlmap.get(job)
    if not url:
        missing.append(c["id"]); continue
    dst = os.path.join(CLIPDIR, f"{c['id']}.mp4")
    if os.path.exists(dst) and os.path.getsize(dst) > 10000:
        print("skip", c["id"]); continue
    try:
        urllib.request.urlretrieve(url, dst)
        print("ok", c["id"], round(os.path.getsize(dst)/1e6, 1), "MB")
    except Exception as e:
        print("ERR", c["id"], e); missing.append(c["id"])
print("MISSING:", missing)
