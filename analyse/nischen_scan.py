# -*- coding: utf-8 -*-
"""Nischen-Scanner — setzt NISCHEN-PLAYBOOK.md §3 (2x2-Diagnose) in Code um.

Beantwortet EINE Frage pro Nische: System / Fruehe Welle / Gesaettigt / Keine Nachfrage.

Ablauf:
  1. Discovery  — YouTube-Suche nach dem Nischen-Keyword scrapen, Kanal-IDs sammeln
  2. Erhebung   — pro Kanal: Abos, Beitrittsdatum, exakte Views der letzten ~15 Uploads (RSS)
  3. Diagnose   — Kleinkanal-Gate + 2x2-Feld + Arithmetik-Gate

Nutzt analyse/fetchlib.py (gedrosselt, kein API-Key noetig).

Aufruf:
    python3 nischen_scan.py "deep sea rov exploration"
    python3 nischen_scan.py "maritime disaster investigation" --rpm 4 --kosten 38 --ziel 10000
    python3 nischen_scan.py --handles handles.txt --label "Technik-Katastrophen"

Ausgabe: Markdown auf stdout + JSON nach analyse/nischen/<slug>.json
"""
import argparse, json, os, re, sys, html
from datetime import date, datetime
from statistics import median

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetchlib import fetch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nischen")
os.makedirs(OUT, exist_ok=True)

TODAY = date.today()
MONTHS = {m: i for i, m in enumerate(
    ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

# --- Playbook-Schwellen (§3 / §4). Bewusst hier zentral, damit sie kalibrierbar sind. ---
KLEIN_ABO_MAX = 50_000      # "kleiner Kanal"
KLEIN_HIT_MIN = 100_000     # Video-Views, die als Outlier eines kleinen Kanals gelten
KLEIN_MIN_ANZAHL = 3        # mind. 3 verschiedene kleine Kanaele mit Hit
JUNG_MONATE = 12            # "jung" = Kanalalter <= 12 Monate
GROSS_ABO_MIN = 200_000     # "grosser Kanal" der Nische
GROSS_MEDIAN_MIN = 50_000   # grosse Kanaele "holen Views", wenn Median darueber liegt
SAMPLE_MAX = 15             # Videos pro Kanal (RSS liefert max ~15)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def sxt(pattern, text, grp=1):
    m = re.search(pattern, text)
    return m.group(grp) if m else None


def norm_abbrev(s):
    """'1.2M subscribers' -> 1200000. Gibt None bei Unlesbarem."""
    if not s:
        return None
    s = s.strip().replace(",", ".")
    m = re.match(r"^([\d.]+)\s*([KMB])?$", s, re.I)
    if not m:
        return None
    try:
        v = float(m.group(1))
    except ValueError:
        return None
    mult = {"k": 1e3, "m": 1e6, "b": 1e9}.get((m.group(2) or "").lower(), 1)
    return int(v * mult)


def parse_join(t):
    """'Mar 14, 2024' -> date"""
    if not t:
        return None
    m = re.match(r"([A-Za-z]{3})\w* (\d{1,2}), (\d{4})", t)
    if not m:
        return None
    mo = MONTHS.get(m.group(1), 0)
    return date(int(m.group(3)), mo, int(m.group(2))) if mo else None


def months_since(d):
    if not d:
        return None
    return (TODAY - d).days / 30.44


# ---------------------------------------------------------------- 1. Discovery
# Zwei Modi. "video" ist der richtige: er findet Kanaele, die MIT DEM THEMA Views
# holen. Der Kanal-Filter findet nur Kanaele, die NACH dem Thema BENANNT sind —
# das sind ueberwiegend frische Slop-Kanaele und verzerrt die Diagnose.
SEARCH_FILTER = {
    "video": "&sp=CAMSAhAB",   # Typ: Video, sortiert nach Aufrufen
    "channel": "&sp=EgIQAg%3D%3D",
}


def discover(keyword, limit=30, mode="video"):
    """YouTube-Suche scrapen -> [(channel_id, handle)], Reihenfolge = Trefferrang."""
    url = ("https://www.youtube.com/results?search_query="
           + re.sub(r"\s+", "+", keyword.strip()) + SEARCH_FILTER.get(mode, ""))
    txt, code, note = fetch(url, f"nsearch__{mode}__" + slug(keyword) + ".html")
    if code != 200 or len(txt) < 1000:
        print(f"  ! Suche fehlgeschlagen (code={code}, {note})", file=sys.stderr)
        return []

    found, seen = [], set()

    def add(cid, handle):
        if cid and cid not in seen:
            seen.add(cid)
            found.append((cid, handle))

    if mode == "video":
        # In Video-Treffern haengt der Kanal am videoOwnerRenderer/longBylineText.
        # Handle steht als canonicalBaseUrl in der Naehe der browseId.
        for m in re.finditer(
                r'"browseId":"(UC[\w-]{20,})","canonicalBaseUrl":"/(@[\w.\-]+)"', txt):
            add(m.group(1), m.group(2))
            if len(found) >= limit:
                return found
        # Fallback: Kanaele ohne Handle
        for m in re.finditer(r'"browseId":"(UC[\w-]{20,})"', txt):
            add(m.group(1), None)
            if len(found) >= limit:
                break
    else:
        for m in re.finditer(
                r'"browseId":"(UC[\w-]{20,})"(?:.{0,400}?"canonicalBaseUrl":"/(@[\w.\-]+))?',
                txt):
            add(m.group(1), m.group(2))
            if len(found) >= limit:
                break
    return found


# ---------------------------------------------------------------- 2. Erhebung
def channel_data(cid, handle=None):
    """Abos + Beitrittsdatum (about) und exakte Views der letzten Uploads (RSS)."""
    rec = {"channel_id": cid, "handle": handle, "warn": []}

    about_url = (f"https://www.youtube.com/{handle}/about" if handle
                 else f"https://www.youtube.com/channel/{cid}/about")
    ab, code, note = fetch(about_url, "nabout__" + (handle or cid).lstrip("@") + ".html")
    if code == 200 and len(ab) > 1000:
        rec["title"] = sxt(r'"title":"([^"]{1,120})","description"', ab)
        rec["subs"] = norm_abbrev(sxt(r'"subscriberCountText":"([^"]*?) subscribers?"', ab))
        rec["join_text"] = sxt(r'"joinedDateText":\{"content":"Joined ([^"]+)"', ab)
        tv = sxt(r'"viewCountText":"([\d,]+) views?"', ab)
        rec["total_views"] = int(tv.replace(",", "")) if tv else None
        vc = sxt(r'"videoCountText":"([\d,]+) videos?"', ab)
        rec["video_count"] = int(vc.replace(",", "")) if vc else None
        if not handle:
            h = sxt(r'"canonicalBaseUrl":"/(@[\w.\-]+)"', ab)
            if h:
                rec["handle"] = h
    else:
        rec["warn"].append(f"about:{code}:{note}")

    join = parse_join(rec.get("join_text"))
    rec["join_date"] = join.isoformat() if join else None
    rec["alter_monate"] = round(months_since(join), 1) if join else None

    rt, rc, rn = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}",
                       "nrss__" + cid + ".xml")
    vids = []
    if rc == 200:
        for e in rt.split("<entry>")[1:]:
            v = sxt(r'<media:statistics views="(\d+)"', e)
            t = sxt(r'<title>([^<]*)</title>', e)
            p = sxt(r'<published>([^<]+)</published>', e)
            if v is not None:
                vids.append({"title": html.unescape(t) if t else None,
                             "views": int(v), "published": p})
    else:
        rec["warn"].append(f"rss:{rc}:{rn}")

    vids = vids[:SAMPLE_MAX]
    rec["n_sample"] = len(vids)
    rec["titel"] = [x["title"] for x in vids if x["title"]]
    views = sorted(x["views"] for x in vids)
    rec["median_views"] = int(median(views)) if views else None
    rec["max_views"] = max(views) if views else None
    rec["top_titel"] = max(vids, key=lambda x: x["views"])["title"] if vids else None
    rec["views_pro_abo"] = (round(rec["median_views"] / rec["subs"], 2)
                            if rec.get("median_views") and rec.get("subs") else None)
    return rec


STOP = {"the", "a", "an", "of", "in", "on", "and", "or", "for", "to", "der", "die", "das",
        "und", "von", "im", "documentary", "doku", "video", "youtube"}


def relevanz(rec, keyword):
    """Anteil der Stichproben-Titel, die ein Keyword-Token enthalten.

    Notwendig, weil die YouTube-Suche auch themenfremde Grosskanaele ausspielt —
    ein 32-Mio.-Kanal mit 9,7 Mio. Median wuerde die Diagnose sonst kippen.
    """
    toks = [t for t in re.findall(r"[a-zA-Zäöüß]{4,}", (keyword or "").lower())
            if t not in STOP]
    titel = rec.get("titel") or []
    if not toks or not titel:
        return None
    hits = sum(1 for t in titel if any(tok in t.lower() for tok in toks))
    return round(hits / len(titel), 2)


# ---------------------------------------------------------------- 3. Diagnose
def diagnose(kanaele, rpm, kosten, ziel, uploads_mon, min_relevanz=0.2):
    d = {}
    auswertbar = [k for k in kanaele if k.get("median_views") is not None and k.get("subs")]
    # Themenfremde Treffer aus der Diagnose nehmen (bleiben in der Tabelle sichtbar)
    valid = [k for k in auswertbar
             if k.get("relevanz") is None or k["relevanz"] >= min_relevanz]
    d["n_kanaele"] = len(kanaele)
    d["n_auswertbar"] = len(auswertbar)
    d["n_relevant"] = len(valid)
    d["min_relevanz"] = min_relevanz
    d["ausgeschlossen_themenfremd"] = [
        (k.get("handle") or k["channel_id"]) for k in auswertbar if k not in valid]

    klein_hits = [k for k in valid
                  if k["subs"] <= KLEIN_ABO_MAX and (k["max_views"] or 0) >= KLEIN_HIT_MIN]
    jung = [k for k in klein_hits
            if k.get("alter_monate") is not None and k["alter_monate"] <= JUNG_MONATE]
    d["klein_mit_hit"] = [k.get("handle") or k["channel_id"] for k in klein_hits]
    d["davon_jung"] = [k.get("handle") or k["channel_id"] for k in jung]
    d["kleinkanal_gate"] = len(klein_hits) >= KLEIN_MIN_ANZAHL
    d["altersignal"] = len(jung) >= 1

    gross = [k for k in valid if k["subs"] >= GROSS_ABO_MIN]
    gross_stark = [k for k in gross if k["median_views"] >= GROSS_MEDIAN_MIN]
    d["n_gross"] = len(gross)
    d["n_gross_stark"] = len(gross_stark)

    klein_ja = d["kleinkanal_gate"]
    gross_ja = len(gross_stark) >= 1
    if klein_ja and gross_ja:
        d["feld"] = "SYSTEM-NISCHE"
        d["urteil"] = "gruen — rein"
    elif klein_ja and not gross_ja:
        d["feld"] = "FRUEHE WELLE"
        d["urteil"] = "gelb — schnell rein, klein testen"
    elif not klein_ja and gross_ja:
        d["feld"] = "GESAETTIGT"
        d["urteil"] = "orange — nur mit Format-Twist"
    else:
        d["feld"] = "KEINE NACHFRAGE"
        d["urteil"] = "rot — raus (kein Geheimtipp)"

    # Arithmetik-Gate (§4)
    d["rpm"] = rpm
    d["break_even_views"] = round(kosten / (rpm / 1000))
    d["views_monat_fuer_ziel"] = round((ziel / rpm) * 1000)
    d["noetiger_median"] = round(d["views_monat_fuer_ziel"] / uploads_mon)

    tier = [k for k in valid if 10_000 <= k["subs"] <= 100_000]
    d["n_tier_10k_100k"] = len(tier)
    d["tier_median"] = int(median([k["median_views"] for k in tier])) if tier else None
    if d["tier_median"] is None:
        d["arithmetik_gate"] = None
    else:
        d["arithmetik_gate"] = d["tier_median"] >= d["noetiger_median"]
    return d


def report(label, kanaele, d):
    L = []
    A = L.append
    A(f"# Nischen-Scan: {label}")
    A("")
    A(f"_Erhoben {TODAY.isoformat()} · {d['n_auswertbar']}/{d['n_kanaele']} Kanäle auswertbar, "
      f"davon **{d['n_relevant']} themenrelevant** (Titel-Match ≥{d['min_relevanz']:.0%}) · "
      f"Stichprobe je Kanal ≤{SAMPLE_MAX} Uploads (RSS, exakte Views)_")
    A("")
    A(f"## Urteil: **{d['feld']}** — {d['urteil']}")
    A("")
    A("| Prüfung | Ergebnis |")
    A("|---|---|")
    A(f"| Kleinkanal-Gate (≥{KLEIN_MIN_ANZAHL} Kanäle <{KLEIN_ABO_MAX:,} Abos mit ≥{KLEIN_HIT_MIN:,}-Video) "
      f"| {'✅' if d['kleinkanal_gate'] else '❌'} {len(d['klein_mit_hit'])} gefunden |")
    A(f"| Alters-Signal (≥1 davon ≤{JUNG_MONATE} Mon. alt) | {'✅' if d['altersignal'] else '❌'} "
      f"{len(d['davon_jung'])} |")
    A(f"| Große Kanäle (≥{GROSS_ABO_MIN:,} Abos) mit Median ≥{GROSS_MEDIAN_MIN:,} | "
      f"{d['n_gross_stark']} von {d['n_gross']} |")
    ag = d["arithmetik_gate"]
    A(f"| Arithmetik-Gate (Tier-Median ≥ nötiger Median) | "
      f"{'✅' if ag else ('❌' if ag is False else '— keine Daten')} |")
    A("")
    A("### Arithmetik (§4)")
    A(f"- RPM-Annahme: **${d['rpm']}** (unteres Drittel, konservativ)")
    A(f"- Break-even: **{d['break_even_views']:,} Views/Folge**")
    A(f"- Für das Ziel: **{d['views_monat_fuer_ziel']:,} Views/Monat** → nötiger Median "
      f"**{d['noetiger_median']:,}/Folge**")
    if d["tier_median"] is not None:
        A(f"- Beobachteter Median der 10k–100k-Abo-Tier ({d['n_tier_10k_100k']} Kanäle): "
          f"**{d['tier_median']:,}**")
    A("")
    A("### Kanäle")
    A("")
    A("| Kanal | Abos | Alter (Mon.) | Median | Max | V/Abo | Rel. | Top-Video |")
    A("|---|---:|---:|---:|---:|---:|---:|---|")
    for k in sorted(kanaele, key=lambda x: -(x.get("median_views") or 0)):
        if k.get("median_views") is None:
            continue
        t = (k.get("top_titel") or "")[:52]
        subs = f"{k['subs']:,}" if k.get("subs") is not None else "?"
        alter = k["alter_monate"] if k.get("alter_monate") is not None else "?"
        rel = k.get("relevanz")
        rels = "—" if rel is None else f"{rel:.0%}"
        mark = "" if (rel is None or rel >= d["min_relevanz"]) else " ⚠︎"
        A(f"| {k.get('handle') or k['channel_id']}{mark} | {subs} | {alter} | "
          f"{k['median_views']:,} | {k['max_views']:,} | {k.get('views_pro_abo') or '?'} | "
          f"{rels} | {t} |")
    if d.get("ausgeschlossen_themenfremd"):
        A("")
        A("_⚠︎ = themenfremd, aus der Diagnose ausgeschlossen: "
          + ", ".join(d["ausgeschlossen_themenfremd"]) + "_")
    skipped = [k for k in kanaele if k.get("median_views") is None]
    if skipped:
        A("")
        A(f"_{len(skipped)} Kanäle ohne auswertbare Daten: "
          + ", ".join((k.get('handle') or k['channel_id']) for k in skipped[:10]) + "_")
    A("")
    A("> Schwellen sind Heuristiken (NISCHEN-PLAYBOOK §1, Beweis-Stufe B) — gegen eigene "
      "Daten kalibrieren, nicht als Naturgesetz behandeln. RSS liefert nur die letzten ~15 "
      "Uploads: der Median ist ein **aktueller** Median, kein Lebenszeit-Median.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keyword", nargs="?", help="Nischen-Suchbegriff")
    ap.add_argument("--handles", help="Datei mit @handles oder UC-IDs (statt Discovery)")
    ap.add_argument("--label", help="Anzeigename der Nische")
    ap.add_argument("--limit", type=int, default=25, help="max. Kanäle (Default 25)")
    ap.add_argument("--mode", choices=["video", "channel"], default="video",
                    help="video = Kanäle, die mit dem Thema Views holen (Default). "
                         "channel = Kanäle, die nach dem Thema benannt sind")
    ap.add_argument("--rpm", type=float, default=4.0)
    ap.add_argument("--kosten", type=float, default=38.0, help="$ pro Folge")
    ap.add_argument("--ziel", type=float, default=10000.0, help="$ Monatsziel")
    ap.add_argument("--uploads", type=float, default=8.0, help="Folgen/Monat")
    ap.add_argument("--min-relevanz", type=float, default=0.2, dest="min_relevanz",
                    help="Mindest-Titel-Match, um in die Diagnose zu zählen (Default 0.2)")
    a = ap.parse_args()

    if not a.keyword and not a.handles:
        ap.error("keyword oder --handles nötig")
    label = a.label or a.keyword or os.path.basename(a.handles)

    if a.handles:
        cands = []
        for line in open(a.handles):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("UC"):
                cands.append((s, None))
            else:
                cands.append((None, s if s.startswith("@") else "@" + s))
        print(f"[1/3] {len(cands)} Kanäle aus Datei", file=sys.stderr)
    else:
        print(f"[1/3] Discovery ({a.mode}): '{a.keyword}' …", file=sys.stderr)
        cands = discover(a.keyword, a.limit, a.mode)
        print(f"      {len(cands)} Kanäle gefunden", file=sys.stderr)

    kanaele = []
    for i, (cid, handle) in enumerate(cands[:a.limit], 1):
        if cid is None:
            ab, code, _ = fetch(f"https://www.youtube.com/{handle}/about",
                                "nres__" + handle.lstrip("@") + ".html")
            cid = sxt(r'"externalId":"(UC[\w-]+)"', ab) if code == 200 else None
            if not cid:
                print(f"      [{i}] {handle}: keine channel_id", file=sys.stderr)
                continue
        print(f"[2/3] [{i}/{min(len(cands), a.limit)}] {handle or cid}", file=sys.stderr)
        rec = channel_data(cid, handle)
        rec["relevanz"] = relevanz(rec, a.keyword)
        kanaele.append(rec)

    print("[3/3] Diagnose …", file=sys.stderr)
    d = diagnose(kanaele, a.rpm, a.kosten, a.ziel, a.uploads, a.min_relevanz)
    md = report(label, kanaele, d)
    print(md)

    p = os.path.join(OUT, slug(label) + ".json")
    json.dump({"label": label, "erhoben": TODAY.isoformat(), "parameter": vars(a),
               "diagnose": d, "kanaele": kanaele}, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"\n_JSON: {os.path.relpath(p, HERE)}_")


if __name__ == "__main__":
    main()
