#!/usr/bin/env python3
"""
Stimmproben-Generator (ElevenLabs) — Gegenstueck zum ersten Stimmentest.

Erzeugt pro Stimme zwei Proben (Zieltempo schnell / langsam), misst das
tatsaechlich erreichte Tempo exakt und protokolliert den Zeichenverbrauch.

Warum die Messung exakt ist: statt der normalen TTS-Route benutzen wir
/v1/text-to-speech/{voice_id}/with-timestamps. Die Antwort enthaelt neben dem
Audio ein Alignment mit Start-/Endzeit JEDES Zeichens. Die letzte Endzeit ist
die Netto-Sprechdauer — kein ffmpeg, kein Schaetzen ueber die Dateigroesse.

Tempo-Treffer: ElevenLabs kennt keinen WPM-Parameter, nur `speed` (0.7–1.2).
Deshalb ein Kalibrierlauf bei speed=1.0, gemessenes WPM -> benoetigter Faktor
= ziel_wpm / gemessen_wpm, geklemmt auf den erlaubten Bereich. Der Kalibrierlauf
wird wiederverwendet, wenn er ein Ziel schon trifft (spart Zeichen).

Kosten: /v1/user/subscription wird vor und nach dem Lauf abgefragt; die
Differenz von character_count ist der real abgerechnete Verbrauch (nicht meine
Schaetzung).

Der API-Key kommt aus der Umgebungsvariable ELEVEN_API_KEY oder aus der Datei
.eleven_key neben diesem Skript. Er wird nie geloggt und nie ausgegeben.
"""
import base64
import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = "https://api.elevenlabs.io"
CA = "/root/.ccr/ca-bundle.crt"

# Ziel-Tempi in Woertern pro Minute.
WPM_FAST = 219.0          # Vorgabe aus dem ersten Stimmentest
WPM_SLOW = 185.0          # "etwas langsamer" — ca. 15 % unter dem Zieltempo
SPEED_MIN, SPEED_MAX = 0.7, 1.2   # von der API erlaubter Bereich
TOLERANCE_WPM = 4.0       # Kalibrierlauf gilt als Treffer, wenn er so nah dran ist

MODEL = os.environ.get("EL_MODEL", "eleven_multilingual_v2")
OUTPUT_FORMAT = "mp3_44100_128"


# ---------------------------------------------------------------- HTTP-Basis

def _key():
    k = os.environ.get("ELEVEN_API_KEY")
    if not k:
        p = os.path.join(HERE, ".eleven_key")
        if os.path.exists(p):
            k = open(p).read().strip()
    if not k:
        sys.exit("Kein API-Key: ELEVEN_API_KEY setzen oder .eleven_key anlegen.")
    return k


def _ctx():
    return ssl.create_default_context(cafile=CA) if os.path.exists(CA) else ssl.create_default_context()


def _request(method, path, body=None, headers=None, raw=False, retries=4):
    """Ein Aufruf gegen die ElevenLabs-API. Key steckt im Header, nie in argv."""
    url = BASE + path
    hdr = {"xi-api-key": _key()}
    if headers:
        hdr.update(headers)
    data = None
    if body is not None and not raw:
        data = json.dumps(body).encode()
        hdr["Content-Type"] = "application/json"
    elif raw:
        data = body
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=hdr, method=method)
        try:
            with urllib.request.urlopen(req, context=_ctx(), timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            # 4xx ausser 429 sind Eingabefehler — Wiederholen bringt nichts.
            if e.code != 429 and 400 <= e.code < 500:
                raise RuntimeError(f"HTTP {e.code} auf {path}: {detail}")
            last = RuntimeError(f"HTTP {e.code} auf {path}: {detail}")
        except (urllib.error.URLError, TimeoutError) as e:
            last = RuntimeError(f"Netzfehler auf {path}: {e}")
        time.sleep(2 ** attempt)
    raise last


# ---------------------------------------------------------------- Bausteine

def subscription():
    d = json.loads(_request("GET", "/v1/user/subscription"))
    return {
        "tier": d.get("tier"),
        "character_count": d.get("character_count"),
        "character_limit": d.get("character_limit"),
    }


def list_voices():
    d = json.loads(_request("GET", "/v2/voices?page_size=100"))
    out = []
    for v in d.get("voices", []):
        lab = v.get("labels") or {}
        out.append({
            "voice_id": v["voice_id"],
            "name": v.get("name"),
            "gender": (lab.get("gender") or "").lower(),
            "age": lab.get("age"),
            "accent": lab.get("accent"),
            "use_case": lab.get("use_case") or lab.get("description"),
            "category": v.get("category"),
        })
    return out


def words(text):
    return len([w for w in re.split(r"\s+", text.strip()) if w])


def tts(voice_id, text, speed, dict_locators=None, stability=0.45,
        similarity=0.75, style=0.0, speaker_boost=True):
    """Erzeugt eine Probe und liefert (mp3_bytes, netto_sprechdauer_sekunden)."""
    body = {
        "text": text,
        "model_id": MODEL,
        "voice_settings": {
            "stability": stability,
            "similarity_boost": similarity,
            "style": style,
            "use_speaker_boost": speaker_boost,
            "speed": round(speed, 3),
        },
    }
    if dict_locators:
        body["pronunciation_dictionary_locators"] = dict_locators
    path = f"/v1/text-to-speech/{voice_id}/with-timestamps?output_format={OUTPUT_FORMAT}"
    d = json.loads(_request("POST", path, body))
    audio = base64.b64decode(d["audio_base64"])
    al = d.get("alignment") or d.get("normalized_alignment") or {}
    ends = al.get("character_end_times_seconds") or []
    if not ends:
        raise RuntimeError("Antwort ohne Alignment — Dauer nicht messbar.")
    return audio, float(ends[-1])


def measure(text, seconds):
    return words(text) / seconds * 60.0 if seconds > 0 else 0.0


def speed_for(target_wpm, measured_wpm, base_speed):
    """Aus einem Messpunkt den noetigen speed-Faktor ableiten (linear)."""
    if measured_wpm <= 0:
        return 1.0
    want = base_speed * (target_wpm / measured_wpm)
    return max(SPEED_MIN, min(SPEED_MAX, want))


# ------------------------------------------------- Aussprache-Woerterbuch

def parse_aussprache(md_path):
    """Liest aussprache.md und zieht Regeln heraus.

    Erkannt werden Markdown-Tabellenzeilen (| Wort | Aussprache | ...) und
    einfache Zeilen der Form "Wort -> Aussprache" bzw. "Wort: Aussprache".
    Ein Eintrag wird als Phonem-Regel gewertet, wenn die Aussprache in
    Schraegstrichen (/.../) oder eckigen Klammern steht (IPA), sonst als Alias.
    """
    rules = []
    if not os.path.exists(md_path):
        return rules
    for line in open(md_path, encoding="utf-8"):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        g = a = None
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if len(cells) < 2:
                continue
            if re.fullmatch(r"[-: ]+", cells[0]):        # Tabellen-Trennzeile
                continue
            if cells[0].lower() in ("wort", "begriff", "schreibweise", "word"):
                continue
            g, a = cells[0], cells[1]
        else:
            m = re.match(r"^[-*]?\s*(.+?)\s*(?:->|→|:)\s*(.+)$", s)
            if m:
                g, a = m.group(1).strip(), m.group(2).strip()
        if not g or not a:
            continue
        g = g.strip("`*_ ")
        a = a.strip("`*_ ")
        if not g or not a or g == a:
            continue
        ipa = re.fullmatch(r"[/\[](.+)[/\]]", a)
        if ipa:
            rules.append({"type": "phoneme", "grapheme": g, "value": ipa.group(1).strip()})
        else:
            rules.append({"type": "alias", "grapheme": g, "value": a})
    return rules


def build_pls(rules, lang, alphabet="ipa"):
    head = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<lexicon version="1.0"\n'
        '      xmlns="http://www.w3.org/2005/01/pronunciation-lexicon"\n'
        '      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        '      xsi:schemaLocation="http://www.w3.org/2005/01/pronunciation-lexicon\n'
        '        http://www.w3.org/TR/2007/CR-pronunciation-lexicon-20071212/pls.xsd"\n'
        f'      alphabet="{alphabet}" xml:lang="{lang}">\n'
    )
    body = []
    for r in rules:
        tag = "phoneme" if r["type"] == "phoneme" else "alias"
        val = (r["value"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        gra = (r["grapheme"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        body.append(f"  <lexeme>\n    <grapheme>{gra}</grapheme>\n    <{tag}>{val}</{tag}>\n  </lexeme>\n")
    return head + "".join(body) + "</lexicon>\n"


def upload_dictionary(pls_text, name, description=""):
    """Multipart-Upload des .pls; liefert (dictionary_id, version_id)."""
    boundary = "----signal" + str(int(time.time()))
    parts = []

    def field(n, v):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{n}"\r\n\r\n{v}\r\n'.encode())

    field("name", name)
    if description:
        field("description", description)
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="aussprache.pls"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n".encode()
        + pls_text.encode("utf-8") + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)
    d = json.loads(_request(
        "POST", "/v1/pronunciation-dictionaries/add-from-file", body=body, raw=True,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}))
    return d["id"], d.get("version_id"), d.get("version_rules_num")


# ---------------------------------------------------------------- Hauptlauf

def run(cfg):
    text = open(os.path.join(HERE, cfg["text_file"]), encoding="utf-8").read().strip()
    n_words, n_chars = words(text), len(text)
    print(f"Testtext: {n_words} Woerter, {n_chars} Zeichen — Modell {MODEL}")

    sub_before = subscription()
    print(f"Tarif {sub_before['tier']}: {sub_before['character_count']}/{sub_before['character_limit']} Zeichen verbraucht")

    results = []
    api_calls = 0

    for v in cfg["voices"]:
        vid, vname, slug = v["voice_id"], v["name"], v["slug"]
        print(f"\n=== {vname} ({v['gender']}) ===")

        # 1) Kalibrierlauf bei speed = 1.0
        audio, dur = tts(vid, text, 1.0)
        api_calls += 1
        wpm_base = measure(text, dur)
        print(f"  Kalibrierung speed=1.00 -> {dur:.2f}s = {wpm_base:.1f} WPM")

        for target, label in ((WPM_FAST, "219wpm"), (WPM_SLOW, "langsam")):
            if abs(wpm_base - target) <= TOLERANCE_WPM:
                # Kalibrierlauf trifft das Ziel schon — wiederverwenden.
                a, d_, sp = audio, dur, 1.0
            else:
                sp = speed_for(target, wpm_base, 1.0)
                a, d_ = tts(vid, text, sp)
                api_calls += 1
            wpm = measure(text, d_)
            fn = f"{slug}_{label}.mp3"
            with open(os.path.join(HERE, fn), "wb") as f:
                f.write(a)
            print(f"  {label}: speed={sp:.3f} -> {d_:.2f}s = {wpm:.1f} WPM  ({fn})")
            results.append({
                "voice": vname, "voice_id": vid, "gender": v["gender"],
                "target_wpm": target, "speed": round(sp, 3),
                "duration_s": round(d_, 2), "wpm": round(wpm, 1),
                "file": fn, "dictionary": False,
            })

    sub_after = subscription()
    used = sub_after["character_count"] - sub_before["character_count"]
    out = {
        "model": MODEL, "output_format": OUTPUT_FORMAT,
        "text_words": n_words, "text_chars": n_chars,
        "targets": {"fast": WPM_FAST, "slow": WPM_SLOW},
        "api_calls": api_calls,
        "characters_billed": used,
        "characters_per_call_nominal": n_chars,
        "tier": sub_before["tier"],
        "quota_before": sub_before["character_count"],
        "quota_after": sub_after["character_count"],
        "quota_limit": sub_after["character_limit"],
        "samples": results,
    }
    with open(os.path.join(HERE, "messwerte.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"\n{api_calls} Aufrufe, {used} Zeichen abgerechnet -> messwerte.json")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "voices":
        for v in list_voices():
            print(f"{v['voice_id']}  {v['gender']:>6}  {v['name']:<22} {v['accent']} / {v['use_case']}")
    elif cmd == "quota":
        print(json.dumps(subscription(), indent=2))
    elif cmd == "run":
        run(json.load(open(os.path.join(HERE, "config.json"), encoding="utf-8")))
    else:
        sys.exit(f"unbekannt: {cmd}")
