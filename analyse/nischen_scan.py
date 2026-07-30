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
from urllib.parse import quote_plus
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
REIF_TAGE = 30              # Videos unter 30 Tagen zaehlen NICHT in den Median (s. u.)
AKTIV_TAGE = 120            # Kanal gilt als aktiv, wenn Upload innerhalb 120 Tagen
NACHFRAGE_MEDIAN_MIN = 50_000   # ab hier "die Nische traegt Reichweite"
NACHFRAGE_MIN_KANAELE = 2       # so viele aktive Kanaele muessen das schaffen


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
    # quote_plus: ohne Kodierung liefert YouTube bei Umlauten eine 1,5-KB-Fehlerseite
    url = ("https://www.youtube.com/results?search_query="
           + quote_plus(keyword.strip()) + SEARCH_FILTER.get(mode, ""))
    txt, code, note = fetch(url, f"nsearch__{mode}__" + slug(keyword) + ".html")
    if code != 200 or len(txt) < 1000:
        print(f"  ! Suche fehlgeschlagen (code={code}, {note}, {len(txt)} B)", file=sys.stderr)
        return [], []

    # Video-Ebene: Nachfrage zeigt sich an den Videos, nicht an dedizierten Kanaelen.
    # In einem unbesetzten Markt gibt es per Definition keine Nischen-Kanaele -
    # aber sehr wohl Videos mit Reichweite. Ohne diese Messung liest der Scanner
    # "unbesetzt" faelschlich als "keine Nachfrage".
    #
    # WICHTIG: Titel und Views MUESSEN aus demselben videoRenderer-Block kommen.
    # Zwei getrennte findall-Listen per zip zu paaren geht schief - die Titel-Regex
    # trifft auch Kapitelmarken ("Einleitung"), und die Zuordnung verrutscht.
    treffer = []
    for blk in txt.split('"videoRenderer":')[1:]:
        w = blk[:4000]
        mt = re.search(r'"title":\{"runs":\[\{"text":"((?:[^"\\]|\\.){3,200})"\}\]', w)
        mv = re.search(r'"viewCountText":\{"simpleText":"([\d.,\u00a0 ]+)\s*(?:views|Aufrufe)"', w)
        if not (mt and mv):
            continue
        try:
            titel = json.loads('"' + mt.group(1) + '"')
        except Exception:
            titel = mt.group(1)
        ziffern = re.sub(r"[^\d]", "", mv.group(1))
        if not ziffern:
            continue
        treffer.append({"titel": titel, "views": int(ziffern)})

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
                return found, treffer
        # Fallback: Kanaele ohne Handle
        for m in re.finditer(r'"browseId":"(UC[\w-]{20,})"', txt):
            add(m.group(1), None)
            if len(found) >= limit:
                break
        return found, treffer
    else:
        for m in re.finditer(
                r'"browseId":"(UC[\w-]{20,})"(?:.{0,400}?"canonicalBaseUrl":"/(@[\w.\-]+))?',
                txt):
            add(m.group(1), m.group(2))
            if len(found) >= limit:
                break
    return found, treffer


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
    for v in vids:
        try:
            pub = datetime.fromisoformat(v["published"].replace("Z", "+00:00")).date()
        except Exception:
            pub = None
        v["alter_tage"] = (TODAY - pub).days if pub else None
        v["views_pro_tag"] = (round(v["views"] / max(v["alter_tage"], 1), 1)
                              if v["alter_tage"] is not None else None)

    rec["n_sample"] = len(vids)
    rec["titel"] = [x["title"] for x in vids if x["title"]]

    # Aktivitaet: juengster Upload. Ruhende Archivkanaele verzerren jede Nischen-Diagnose.
    alter = [v["alter_tage"] for v in vids if v["alter_tage"] is not None]
    rec["letzter_upload_tage"] = min(alter) if alter else None
    rec["aktiv"] = (rec["letzter_upload_tage"] is not None
                    and rec["letzter_upload_tage"] <= AKTIV_TAGE)

    # KERNKORREKTUR: Nur Videos zaehlen, die Zeit hatten, Views zu sammeln.
    # Sonst bestraft der Median langsame Qualitaetskanaele (frische Uploads = 0 Views)
    # und bevorzugt Spam-Kanaele mit hoher Kadenz.
    reif = [v for v in vids if v["alter_tage"] is not None and v["alter_tage"] >= REIF_TAGE]
    rec["n_reif"] = len(reif)
    rv = sorted(v["views"] for v in reif)
    rec["median_views"] = int(median(rv)) if rv else None
    rec["max_views"] = max(rv) if rv else None
    rec["median_views_pro_tag"] = (round(median([v["views_pro_tag"] for v in reif]), 1)
                                   if reif else None)
    rec["top_titel"] = max(reif, key=lambda x: x["views"])["title"] if reif else None
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
    if not toks:
        return None
    # Kanalname zaehlt voll: ein Kanal namens "Erdarchiv" ist thematisch, auch wenn
    # seine Videotitel die Suchwoerter nicht wiederholen.
    kname = ((rec.get("title") or "") + " " + (rec.get("handle") or "")).lower()
    if any(tok in kname for tok in toks):
        return 1.0
    if not titel:
        return None
    hits = sum(1 for t in titel if any(tok in t.lower() for tok in toks))
    return round(hits / len(titel), 2)


# ---------------------------------------------------------------- 3. Diagnose
def diagnose(kanaele, rpm, kosten, ziel, uploads_mon, min_relevanz=0.1, treffer=None):
    """Zwei UNABHAENGIGE Fragen, nicht eine.

    NACHFRAGE: Traegt die Nische ueberhaupt Reichweite? (Sonst egal, wie offen sie ist.)
    FENSTER:   Kommen NEUE/kleine Kanaele noch durch? (Sonst nur Verdraengung.)

    Diese Trennung ist die Korrektur eines Fehlers der ersten Fassung: Space-Doku
    hat hohe Nachfrage, aber alle Betreiber sind ueber 50k Abos gewachsen. Ein
    einzelnes 2x2 hat das als "gesaettigt" gelesen und die Nische verworfen,
    obwohl sie nachweislich traegt.
    """
    d = {}
    auswertbar = [k for k in kanaele if k.get("median_views") is not None and k.get("subs")]
    relevant = [k for k in auswertbar
                if k.get("relevanz") is None or k["relevanz"] >= min_relevanz]
    aktiv = [k for k in relevant if k.get("aktiv")]

    d["n_kanaele"] = len(kanaele)
    d["n_auswertbar"] = len(auswertbar)
    d["n_relevant"] = len(relevant)
    d["n_aktiv"] = len(aktiv)
    d["min_relevanz"] = min_relevanz
    d["ausgeschlossen_themenfremd"] = [(k.get("handle") or k["channel_id"])
                                       for k in auswertbar if k not in relevant]
    d["ausgeschlossen_ruhend"] = [(k.get("handle") or k["channel_id"])
                                  for k in relevant if not k.get("aktiv")]

    # --- Frage 0: THEMEN-NACHFRAGE auf Video-Ebene ---
    tv = sorted((t["views"] for t in (treffer or [])), reverse=True)
    d["n_treffer"] = len(tv)
    d["treffer_top"] = (treffer or [])[:8]
    d["treffer_median"] = int(median(tv)) if tv else None
    d["treffer_ueber_100k"] = sum(1 for v in tv if v >= 100_000)
    d["treffer_ueber_500k"] = sum(1 for v in tv if v >= 500_000)
    # Thema traegt, wenn mehrere Treffer sechsstellig sind - unabhaengig davon,
    # ob dedizierte Kanaele existieren.
    d["thema_traegt"] = d["treffer_ueber_100k"] >= 5

    # --- Frage 1: NACHFRAGE ---
    traeger = [k for k in aktiv if k["median_views"] >= NACHFRAGE_MEDIAN_MIN]
    d["traeger"] = [{"kanal": k.get("handle") or k["channel_id"], "subs": k["subs"],
                     "median": k["median_views"]} for k in traeger]
    d["nachfrage"] = len(traeger) >= NACHFRAGE_MIN_KANAELE
    med_all = sorted(k["median_views"] for k in aktiv)
    d["nischen_median"] = int(median(med_all)) if med_all else None
    d["nischen_bestes_median"] = max(med_all) if med_all else None

    # --- Frage 2: FENSTER ---
    klein_hits = [k for k in aktiv
                  if k["subs"] <= KLEIN_ABO_MAX and (k["max_views"] or 0) >= KLEIN_HIT_MIN]
    jung_stark = [k for k in aktiv
                  if k.get("alter_monate") is not None and k["alter_monate"] <= 18
                  and k["median_views"] >= NACHFRAGE_MEDIAN_MIN]
    d["klein_mit_hit"] = [k.get("handle") or k["channel_id"] for k in klein_hits]
    d["jung_und_stark"] = [k.get("handle") or k["channel_id"] for k in jung_stark]
    d["fenster"] = (len(klein_hits) >= KLEIN_MIN_ANZAHL) or (len(jung_stark) >= 1)

    # --- Kombiniertes Urteil ---
    if not d["nachfrage"] and d["thema_traegt"]:
        d["feld"] = "UNBESETZT MIT NACHFRAGE"
        d["urteil"] = ("gruen-gelb — Thema traegt nachweislich Reichweite, aber es gibt "
                       "kaum dedizierte Kanaele. Das ist die interessanteste Lage: "
                       "Nachfrage ohne Angebot. Vor dem Bau per Pilot bestaetigen.")
    elif d["nachfrage"] and d["fenster"]:
        d["feld"], d["urteil"] = "SYSTEM-NISCHE", "gruen — rein"
    elif d["nachfrage"] and not d["fenster"]:
        d["feld"] = "TRAGFAEHIG, FENSTER ENG"
        d["urteil"] = "orange — nur mit echtem Format-Unterschied (Verdraengung, kein Selbstlaeufer)"
    elif not d["nachfrage"] and d["fenster"]:
        d["feld"] = "FRUEHE WELLE ODER ZU KLEIN"
        d["urteil"] = "gelb — nur klein testen; unklar, ob die Nische Reichweite traegt"
    else:
        d["feld"] = "KEINE NACHFRAGE"
        d["urteil"] = ("rot — raus. Weder tragen die Videos zum Thema Reichweite, "
                       "noch gibt es Kanaele, die davon leben.")

    # --- Arithmetik-Gate (Playbook 4) ---
    d["rpm"] = rpm
    d["break_even_views"] = round(kosten / (rpm / 1000))
    d["views_monat_fuer_ziel"] = round((ziel / rpm) * 1000)
    d["noetiger_median"] = round(d["views_monat_fuer_ziel"] / uploads_mon)
    d["arithmetik_gate"] = (None if d["nischen_bestes_median"] is None
                            else d["nischen_bestes_median"] >= d["noetiger_median"])
    d["arithmetik_basis"] = "bestes aktives Kanal-Median der Nische"
    return d


def report(label, kanaele, d):
    L = []
    A = L.append
    A(f"# Nischen-Scan: {label}")
    A("")
    A(f"_Erhoben {TODAY.isoformat()} · {d['n_auswertbar']}/{d['n_kanaele']} auswertbar → "
      f"{d['n_relevant']} themenrelevant → **{d['n_aktiv']} aktiv** (Upload ≤{AKTIV_TAGE} T.) · "
      f"Median nur über Videos ≥{REIF_TAGE} Tage alt_")
    A("")
    A(f"## Urteil: **{d['feld']}**")
    A(f"{d['urteil']}")
    A("")
    A("| Frage | Ergebnis |")
    A("|---|---|")
    if d.get("n_treffer"):
        A(f"| **THEMA** — tragen Videos zum Thema Reichweite? (Video-Ebene) "
          f"| {'✅ ja' if d['thema_traegt'] else '❌ nein'} — "
          f"{d['treffer_ueber_100k']}/{d['n_treffer']} Treffer ≥100k, "
          f"{d['treffer_ueber_500k']} ≥500k, Median {d['treffer_median']:,} |")
    A(f"| **NACHFRAGE** — ≥{NACHFRAGE_MIN_KANAELE} aktive Kanäle mit Median ≥{NACHFRAGE_MEDIAN_MIN:,} "
      f"| {'✅ ja' if d['nachfrage'] else '❌ nein'} ({len(d['traeger'])} gefunden) |")
    A(f"| **FENSTER** — ≥{KLEIN_MIN_ANZAHL} Kanäle <{KLEIN_ABO_MAX:,} Abos mit ≥{KLEIN_HIT_MIN:,}-Video "
      f"**oder** ≥1 Kanal ≤18 Mon. mit starkem Median "
      f"| {'✅ offen' if d['fenster'] else '❌ eng'} "
      f"({len(d['klein_mit_hit'])} klein / {len(d['jung_und_stark'])} jung) |")
    ag = d["arithmetik_gate"]
    A(f"| **ARITHMETIK** — bestes Nischen-Median ≥ nötiger Median "
      f"| {'✅' if ag else ('❌' if ag is False else '— keine Daten')} |")
    A("")
    if d["traeger"]:
        A("**Träger der Nachfrage:** "
          + " · ".join(f"{t['kanal']} ({t['subs']:,} Abos, Median {t['median']:,})"
                       for t in d["traeger"][:6]))
        A("")
    if d.get("treffer_top"):
        A("### Top-Videos zum Thema (Video-Ebene, unabhängig vom Kanal)")
        A("")
        A("| Views | Titel |")
        A("|---:|---|")
        for t in d["treffer_top"]:
            A(f"| {t['views']:,} | {t['titel'][:78]} |")
        A("")
    A("### Arithmetik (Playbook §4)")
    A(f"- RPM-Annahme **${d['rpm']}** · Break-even **{d['break_even_views']:,} Views/Folge**")
    A(f"- Ziel braucht **{d['views_monat_fuer_ziel']:,} Views/Monat** → nötiger Median "
      f"**{d['noetiger_median']:,}/Folge**")
    if d["nischen_median"] is not None:
        A(f"- Nischen-Median (aktive Kanäle): **{d['nischen_median']:,}** · "
          f"bestes Kanal-Median: **{d['nischen_bestes_median']:,}**")
    A("")
    A("### Kanäle")
    A("")
    A("| Kanal | Abos | Alter M. | Median (reif) | n reif | V/Tag | Max | Rel. | Letzter Upload |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for k in sorted(kanaele, key=lambda x: -(x.get("median_views") or 0)):
        if k.get("median_views") is None:
            continue
        rel = k.get("relevanz")
        flags = ""
        if rel is not None and rel < d["min_relevanz"]:
            flags += " ⚠︎"
        if not k.get("aktiv"):
            flags += " 💤"
        lu = k.get("letzter_upload_tage")
        subs = f"{k['subs']:,}" if k.get("subs") is not None else "?"
        alter = k["alter_monate"] if k.get("alter_monate") is not None else "?"
        relstr = "—" if rel is None else f"{rel:.0%}"
        lustr = f"{lu} T." if lu is not None else "?"
        A(f"| {k.get('handle') or k['channel_id']}{flags} | {subs} | {alter} "
          f"| {k['median_views']:,} | {k.get('n_reif') or 0} "
          f"| {k.get('median_views_pro_tag') or '?'} | {k['max_views']:,} "
          f"| {relstr} | {lustr} |")
    A("")
    legend = []
    if d.get("ausgeschlossen_themenfremd"):
        legend.append("⚠︎ themenfremd: " + ", ".join(d["ausgeschlossen_themenfremd"]))
    if d.get("ausgeschlossen_ruhend"):
        legend.append("💤 ruhend (aus Diagnose ausgeschlossen): "
                      + ", ".join(d["ausgeschlossen_ruhend"]))
    for x in legend:
        A(f"_{x}_")
        A("")
    skipped = [k for k in kanaele if k.get("median_views") is None]
    if skipped:
        A(f"_{len(skipped)} ohne auswertbare Daten: "
          + ", ".join((k.get('handle') or k['channel_id']) for k in skipped[:10]) + "_")
        A("")
    A("> **Grenzen des Instruments (ehrlich):** RSS liefert nur die letzten ~15 Uploads → "
      "der Median ist ein *aktueller* Median, kein Lebenszeit-Median. Videos <"
      f"{REIF_TAGE} Tage sind ausgeschlossen, weil sie noch keine Views gesammelt haben. "
      "Handle-Auflösung kann fehlgehen (gleichnamige Kanäle) — Abo-Zahl und Top-Titel "
      "gegenprüfen. Schwellen sind Heuristiken (NISCHEN-PLAYBOOK §1, Stufe B).")
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
    ap.add_argument("--min-relevanz", type=float, default=0.1, dest="min_relevanz",
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
        treffer = []
        print(f"[1/3] {len(cands)} Kanäle aus Datei", file=sys.stderr)
    else:
        print(f"[1/3] Discovery ({a.mode}): '{a.keyword}' …", file=sys.stderr)
        cands, treffer = discover(a.keyword, a.limit, a.mode)
        print(f"      {len(cands)} Kanäle, {len(treffer)} Video-Treffer", file=sys.stderr)

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
    d = diagnose(kanaele, a.rpm, a.kosten, a.ziel, a.uploads, a.min_relevanz, treffer)
    md = report(label, kanaele, d)
    print(md)

    p = os.path.join(OUT, slug(label) + ".json")
    json.dump({"label": label, "erhoben": TODAY.isoformat(), "parameter": vars(a),
               "diagnose": d, "kanaele": kanaele}, open(p, "w"), ensure_ascii=False, indent=1)
    print(f"\n_JSON: {os.path.relpath(p, HERE)}_")


if __name__ == "__main__":
    main()
