#!/usr/bin/env python3
# Musik-Betten Folge 1 v4 via ElevenLabs Music. 3 Betten (Akt 1/2/3).
import os, json, time, urllib.request, urllib.error
KEY = open("/tmp/claude-0/-home-user-YOutube/49ca386a-7ebb-5a62-a8e4-ca474812989b/scratchpad/.eleven_key").read().strip()
OUT = "/home/user/YOutube/produktion/folge-01-v4"
os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")
BEDS = [
 ("music_act1", 180000, "Slow mysterious ambient orchestral underscore for a space documentary. Deep sub-bass drone, distant shimmering high strings, vast cold emptiness and rising unease. Patient, minimal, no drums, cinematic, minor key."),
 ("music_act2", 180000, "Tense procedural investigative underscore. Cold pulsing synth arpeggio, a subtle ticking pulse, restrained strings, analytical and forensic, quiet building suspense, no big drums, cinematic documentary."),
 ("music_act3", 200000, "Resolving cinematic underscore moving from tension to awe and wonder. Warm swelling strings, a hopeful rising motif, gentle piano, a sense of revelation and calm resolution, uplifting but restrained, no vocals, no drums."),
]
for name, ms, prompt in BEDS:
    body = json.dumps({"prompt": prompt, "music_length_ms": ms}).encode()
    url = "https://api.elevenlabs.io/v1/music?output_format=mp3_44100_128"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, data=body, headers={
                "xi-api-key": KEY, "Content-Type":"application/json", "Accept":"audio/mpeg"})
            with urllib.request.urlopen(req, timeout=300) as r:
                data = r.read()
            open(f"{OUT}/{name}.mp3","wb").write(data)
            print(f"{name} OK  {len(data)//1024} KB  ({ms/1000:.0f}s target)")
            break
        except urllib.error.HTTPError as e:
            msg=e.read()[:300]
            print(f"{name} HTTP {e.code}: {msg}")
            if e.code in (401,403): raise
            # if length too long, halve and retry
            if e.code in (400,422) and ms>90000:
                ms=ms//2; body=json.dumps({"prompt":prompt,"music_length_ms":ms}).encode()
            time.sleep(2**attempt)
        except Exception as e:
            print(f"{name} err {e}"); time.sleep(2**attempt)
    time.sleep(0.5)
print("music done")
