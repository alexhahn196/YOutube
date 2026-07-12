#!/usr/bin/env python3
"""ElevenLabs pipeline helper. Shells out to curl (proxy+CA already work for curl).
Key read from .eleven_key. Never prints the key."""
import base64, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
KEY = open(os.path.join(HERE, ".eleven_key")).read().strip()
CA = "/root/.ccr/ca-bundle.crt"
BASE = "https://api.elevenlabs.io"

def _curl(method, path, json_body=None, out=None, extra_qs=""):
    url = BASE + path + extra_qs
    cmd = ["curl", "-sS", "--cacert", CA, "-X", method, url,
           "-H", f"xi-api-key: {KEY}"]
    if json_body is not None:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(json_body)]
    if out:
        cmd += ["-o", out, "-w", "%{http_code}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout.strip()  # http code
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout

def design_voice(description, sample_text, name):
    print("Voice Design: creating previews...")
    resp = _curl("POST", "/v1/text-to-voice/create-previews",
                 {"voice_description": description, "text": sample_text})
    data = json.loads(resp)
    previews = data.get("previews", [])
    if not previews:
        print("NO PREVIEWS:", resp[:500]); sys.exit(1)
    print(f"got {len(previews)} previews")
    ids = []
    for i, p in enumerate(previews):
        gid = p["generated_voice_id"]
        ids.append(gid)
        with open(os.path.join(HERE, f"voice_preview_{i}.mp3"), "wb") as f:
            f.write(base64.b64decode(p["audio_base_64"]))
        print(f"  preview {i}: {gid}")
    # create voice from preview 0
    chosen = ids[0]
    resp2 = _curl("POST", "/v1/text-to-voice/create-voice-from-preview",
                  {"voice_name": name, "voice_description": description,
                   "generated_voice_id": chosen})
    d2 = json.loads(resp2)
    vid = d2.get("voice_id")
    print("VOICE_ID:", vid)
    json.dump({"voice_id": vid, "preview_ids": ids}, open(os.path.join(HERE, "voice.json"), "w"))
    return vid

if __name__ == "__main__":
    if sys.argv[1] == "design":
        DESC = ("A calm, authoritative male narrator, late 30s to 40s. Warm but sober, "
                "intelligent and measured, with a quiet sense of wonder, like a mission-control "
                "analyst or a premium science documentary host. Neutral American accent, clear "
                "diction, deep and grounded, unhurried and trustworthy. Never theatrical, never "
                "salesy. Clean studio quality, no background noise.")
        SAMPLE = ("On July 1st, 2025, a survey telescope in Chile caught something falling through "
                  "our solar system that did not come from here. It was moving too fast for the Sun "
                  "to have ever captured it. Today, we look at what the evidence really says.")
        design_voice(DESC, SAMPLE, "SIGNAL Analyst")
