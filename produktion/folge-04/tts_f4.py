#!/usr/bin/env python3
# Vertonung Folge 1 v4 — de3-Stimme. Segmentiert nach Szenen, TTS je Segment.
import os, re, json, time, urllib.request, urllib.error

KEY = open("/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad/.eleven_key").read().strip()
VOICE = "LWuqGg44QZ1wFYrHkX98"
SRC = "/home/user/YOutube/skript/signal-04-VO.md"
OUT = "/home/user/YOutube/produktion/folge-04"
CA  = "/root/.ccr/ca-bundle.crt"
os.environ.setdefault("SSL_CERT_FILE", CA)

raw = open(SRC).read().splitlines()
segments = []
cur_title, cur_lines = None, []
def flush():
    global cur_title, cur_lines
    if cur_title is not None:
        segments.append((cur_title, cur_lines[:]))
    cur_lines = []
for ln in raw:
    s = ln.strip()
    if s.startswith("══"):
        flush()
        cur_title = re.sub(r"[═\s]+"," ", s).strip()
        continue
    if cur_title is None:      # skip preamble (title + Stimme note)
        continue
    if not s: continue
    if re.match(r"^\[MID-ROLL", s, re.I): continue
    if re.match(r"^\[TITLE", s, re.I): continue
    # pause markers -> ellipsis pauses
    s = re.sub(r"^\[LANGER BEAT\]$", "… …", s, flags=re.I)
    s = re.sub(r"^\[BEAT\]$", "…", s, flags=re.I)
    cur_lines.append(s)
flush()

# merge tiny segments (< 120 chars) into previous to avoid choppy TTS
merged = []
for title, lines in segments:
    text = " ".join(lines).strip()
    text = re.sub(r"\s+…\s+", " … ", text)
    if merged and len(text) < 120:
        merged[-1] = (merged[-1][0], (merged[-1][1] + " " + text).strip())
    else:
        merged.append((title, text))

print(f"{len(merged)} segments")
total_chars = 0
manifest = []
for i,(title,text) in enumerate(merged, 1):
    total_chars += len(text)
    body = json.dumps({
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability":0.45,"similarity_boost":0.75,"style":0.10,"use_speaker_boost":True}
    }).encode()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}?output_format=mp3_44100_128"
    outp = f"{OUT}/vo_seg{i:02d}.mp3"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=body, headers={
                "xi-api-key": KEY, "Content-Type":"application/json", "Accept":"audio/mpeg"})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            open(outp,"wb").write(data)
            print(f"seg{i:02d} OK  {len(text):4d} chars  {len(data)//1024:5d} KB  {title[:40]}")
            manifest.append({"seg":i,"title":title,"chars":len(text),"file":os.path.basename(outp)})
            break
        except urllib.error.HTTPError as e:
            print(f"seg{i:02d} HTTP {e.code}: {e.read()[:200]}")
            if e.code in (401,403): raise
            time.sleep(2**attempt)
        except Exception as e:
            print(f"seg{i:02d} err {e}"); time.sleep(2**attempt)
    time.sleep(0.4)

json.dump(manifest, open(f"{OUT}/vo_manifest.json","w"), indent=2)
print(f"=== TOTAL {total_chars} chars = {total_chars} ElevenLabs credits ===")
print("done")
