#!/usr/bin/env python3
"""Gemeinfreies NASA-Material holen statt KI-Credits verbrennen (ab F5, User-Entscheid 28.07.2026).

Quelle: images.nasa.gov (NASA Image and Video Library, offizielle API, kein Key noetig).
NASA-Material ist ueberwiegend GEMEINFREI — echte Missionsaufnahmen kosten 0 Credits und
senken zugleich den KI-Anteil sichtbar (Playbook §12.8 / W6: staerkt Glaubwuerdigkeit).

ACHTUNG Lizenz: NASA-eigenes Material ist public domain, ABER einzelne Assets enthalten
Fremdmaterial (Hubble/ESA = CC BY, Partneragenturen, Musik). Das Skript schreibt zu jedem
Download die Metadaten in credits.json — vor Verwendung pruefen und in die Videobeschreibung
uebernehmen.

Nutzung:
  python3 fetch_nasa.py "voyager launch" --type video --list
  python3 fetch_nasa.py "hubble deep field" --type image -n 5 --out ../folge-05/nasa
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request

API = "https://images-api.nasa.gov"
# Schlichte UA-Strings beantwortet der Asset-CDN teils mit 503 — Browser-Kennung noetig.
UA = {"User-Agent": "Mozilla/5.0 (compatible; SIGNAL-doku/1.0)"}


def api_get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def search(query, media_type="video", n=10, year_start=None):
    params = {"q": query, "media_type": media_type, "page_size": min(n, 100)}
    if year_start:
        params["year_start"] = year_start
    data = api_get(f"{API}/search?" + urllib.parse.urlencode(params))
    col = data["collection"]
    out = []
    for item in col.get("items", [])[:n]:
        d = item["data"][0]
        out.append({
            "nasa_id": d["nasa_id"],
            "title": d.get("title", ""),
            "date": (d.get("date_created") or "")[:10],
            "center": d.get("center", ""),
            "keywords": d.get("keywords", []),
            "description": (d.get("description") or "")[:400],
            "preview": (item.get("links") or [{}])[0].get("href", ""),
        })
    return col["metadata"]["total_hits"], out


def best_asset(nasa_id, media_type):
    """Groesste verfuegbare Datei waehlen (orig > large > medium)."""
    data = api_get(f"{API}/asset/{urllib.parse.quote(nasa_id)}")
    hrefs = [i["href"] for i in data["collection"]["items"]]
    exts = (".mp4",) if media_type == "video" else (".jpg", ".png", ".tif")
    cands = [h for h in hrefs if h.lower().endswith(exts)]
    for tag in ("~orig", "~large", "~medium", ""):
        for h in cands:
            if tag in h:
                return h
    return cands[0] if cands else None


def download(url, dest, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=300) as r, open(dest, "wb") as f:
                while chunk := r.read(1 << 20):
                    f.write(chunk)
            return os.path.getsize(dest)
        except Exception as e:                       # CDN antwortet sporadisch mit 503
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("query")
    p.add_argument("--type", default="video", choices=["video", "image", "audio"])
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--year-start")
    p.add_argument("--list", action="store_true", help="nur suchen, nichts laden")
    p.add_argument("--out", default="nasa_assets")
    p.add_argument("--pick", type=int, nargs="*", help="Indizes zum Laden (Default: alle)")
    a = p.parse_args()

    total, items = search(a.query, a.type, a.n, a.year_start)
    print(f"{total} Treffer fuer '{a.query}' ({a.type}) — zeige {len(items)}:\n")
    for i, it in enumerate(items):
        print(f"[{i}] {it['title'][:72]}")
        print(f"    {it['date']} · {it['center']} · {', '.join(it['keywords'][:5])}")
        if it["description"]:
            print(f"    {it['description'][:150]}...")
    if a.list:
        print("\n(--list: nichts geladen. Ohne --list bzw. mit --pick 0 2 laden.)")
        return

    os.makedirs(a.out, exist_ok=True)
    picks = a.pick if a.pick else range(len(items))
    credits = []
    for i in picks:
        it = items[i]
        url = best_asset(it["nasa_id"], a.type)
        if not url:
            print(f"[{i}] keine Datei gefunden — uebersprungen")
            continue
        ext = os.path.splitext(url)[1]
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in it["nasa_id"])[:60]
        dest = os.path.join(a.out, safe + ext)
        size = download(url, dest)
        credits.append({**it, "file": os.path.basename(dest), "source_url": url})
        print(f"[{i}] -> {dest} ({size/1048576:.1f} MB)")

    cf = os.path.join(a.out, "credits.json")
    old = json.load(open(cf)) if os.path.exists(cf) else []
    json.dump(old + credits, open(cf, "w"), indent=1, ensure_ascii=False)
    print(f"\nMetadaten/Quellenangaben -> {cf}")
    print("⚠️  Lizenz je Asset pruefen (NASA public domain, aber ESA/Hubble = CC BY, Musik ggf. lizenzpflichtig)")


if __name__ == "__main__":
    main()
