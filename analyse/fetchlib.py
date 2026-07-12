# -*- coding: utf-8 -*-
"""Gedrosselter Fetcher. ~2 req/s, Backoff bei 429, Roh-Response nach ./raw/."""
import subprocess, time, os, re, sys
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
RAW=os.path.join(os.path.dirname(__file__),"..","raw")
os.makedirs(RAW,exist_ok=True)
_last=[0.0]
MIN_GAP=0.5  # 2 req/s

def _sleep_gap():
    dt=time.time()-_last[0]
    if dt<MIN_GAP: time.sleep(MIN_GAP-dt)
    _last[0]=time.time()

def fetch(url, rawname, tries=5):
    """Return (text, http_code, note). Speichert Roh nach ./raw/rawname."""
    backoff=2
    note=""
    for attempt in range(tries):
        _sleep_gap()
        try:
            p=subprocess.run(
                ["curl","-sL","--compressed","--max-time","35",
                 "-H","Accept-Language: en-US,en;q=0.9","-H","User-Agent: "+UA,
                 "--cookie","SOCS=CAI; CONSENT=YES+cb","-w","\n@@HTTP@@%{http_code}",url],
                capture_output=True,text=True,timeout=45)
            out=p.stdout
            m=re.search(r"@@HTTP@@(\d+)\s*$",out)
            code=int(m.group(1)) if m else 0
            body=out[:m.start()] if m else out
        except Exception as e:
            code=0; body=""; note="curl_exc:"+str(e)[:40]
        # save raw (last attempt content)
        try:
            with open(os.path.join(RAW,rawname),"w") as f: f.write(body)
        except Exception: pass
        if code==429 or code==403:
            note=f"http{code}_retry{attempt}"
            time.sleep(backoff); backoff*=2; continue
        if code==0 or len(body)<500:
            note=f"empty_or_err_code{code}_retry{attempt}"
            time.sleep(backoff); backoff*=2; continue
        if "consent.youtube.com" in body[:5000] or "Before you continue to YouTube" in body[:8000]:
            note="consent_wall"; time.sleep(backoff); backoff*=2; continue
        return body, code, note
    return body if 'body' in dir() else "", code if 'code' in dir() else 0, note or "exhausted"
