# -*- coding: utf-8 -*-
"""Nischen-Scanner v2 — setzt NISCHEN-SYSTEM.md Stufe 3 in Code um.

v2 nach externem Audit (6 Fachperspektiven, 30.07.2026). Was sich geaendert hat
und WARUM — das ist wichtiger als der Code selbst:

1. SUCHFILTER WAR FALSCH.  "&sp=CAMSAhAB" liefert 0 videoRenderer-Bloecke
   (760 KB Seite, aber unparsebar). Richtig ist "&sp=EgIQAQ%3D%3D". Das hat im
   Deutschland-Lauf 7 von 11 Scans stillschweigend ruiniert und sechs Nischen
   faelschlich als "keine Nachfrage" ins Kill-Log geschrieben.

2. KEIN RELEVANZFILTER MEHR.  Der Filter war doppelt falsch: er sperrte den
   entscheidenden Fachkanal aus (@Erdarchiv, 7 %) und liess einen fachfremden
   Grosskanal als Benchmark durch (@KurzgesagtDE bekam 100 %, weil "Dinge
   Erklaert" das Suchwort "erklaert" enthaelt — und setzte in ZWEI
   unabhaengigen Nischen denselben Benchmark-Median).
   Stattdessen KONSTRUKTIV: Der Kanalpool sind die OWNER der Suchtreffer.
   Wer mit dem Thema in den Suchergebnissen steht, ist per Konstruktion
   themenrelevant. Kein Filter kann dann noch falsch filtern.

3. DAUER WIRD GEMESSEN.  Vorher nie erhoben — deshalb blieb unsichtbar, dass
   der Kronzeuge des Deutschland-Entscheids Sleep-Content produziert. Format
   ist Teil der Nischendefinition (Publikum x Themenraum x FORMAT).

4. LAUT SCHEITERN.  Fehlgeschlagene Messung wirft, statt ein plausibles
   Urteil zu drucken. Exit 2. Stille Fehler waren die gefaehrlichste
   Fehlerklasse des Vorgaengers.

5. MINDEST-N-GUARDS + QUOTEN statt Absolutzahlen.  "5 Treffer ueber 100k" ist
   bei 3 extrahierten Treffern arithmetisch unerreichbar — das Gate misst dann
   die Parse-Ausbeute, nicht den Markt.

6. UNSICHERHEIT WIRD AUSGEWIESEN.  Median mit Konfidenzintervall; ein Gate,
   dessen Schwelle im Intervall liegt, gilt als unentschieden.

7. WINNER'S CURSE.  Der Sieger ist das Maximum aus vielen verrauschten
   Schaetzern und damit systematisch zu hoch. Benchmark = Median der besten
   drei, nicht das Maximum; zusaetzlich wird der abgeschlagene Wert gedruckt.

8. KATALOGFAKTOR.  Einnahmen kommen nicht nur aus Uploads des Monats, sondern
   aus dem Backkatalog. Ohne diesen Faktor lag das Arithmetik-Gate ~2-3x zu
   hoch und haette kuenftig Kandidaten grundlos getoetet.

Aufruf:
    python3 nischen_scan.py "keyword"
    python3 nischen_scan.py "kw1" "kw2" "kw3" --label "Nische"   # 3 Keywords: Pflicht laut System
    python3 nischen_scan.py --handles handles.txt --label "Ground Truth"
"""
import argparse, json, math, os, re, sys, html
from urllib.parse import quote_plus
from datetime import date, datetime
from statistics import median, stdev

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetchlib import fetch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "nischen")
os.makedirs(OUT, exist_ok=True)
TODAY = date.today()
MONTHS = {m: i for i, m in enumerate(
    ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

# ---- Schwellen. Heuristiken (NISCHEN-PLAYBOOK §1, Stufe B) — kalibrierbar. ----
KLEIN_ABO_MAX = 50_000
KLEIN_HIT_MIN = 100_000
KLEIN_MIN_ANZAHL = 3
GROSS_ABO_MIN = 200_000
NACHFRAGE_MEDIAN_MIN = 50_000
NACHFRAGE_MIN_KANAELE = 2
SAMPLE_MAX = 15
AKTIV_TAGE = 120
REIF_MIN = 7                 # untere Grenze der adaptiven Reifeschwelle
REIF_ZIEL = 30               # bevorzugte Reifeschwelle
REIF_MIN_N = 5               # so viele reife Videos braucht ein Median
MIN_TREFFER = 12             # darunter: Themen-Nachfrage ungemessen
MIN_AKTIV_FENSTER = 5        # darunter: Fenster-Frage unentscheidbar
THEMA_QUOTE = 0.25           # Anteil der Treffer >=100k, ab dem das Thema traegt
KATALOG_FAKTOR = 2.0         # Backkatalog-Multiplikator (konservativ)
SIGMA_FALLBACK = 1.3         # log10-Streuung, wenn Stichprobe zu klein


class MessungFehlgeschlagen(Exception):
    """Wird geworfen, wenn die Erhebung nicht belastbar ist. Nie stillschweigend
    ein plausibles Urteil drucken — das war der schlimmste Fehler von v1."""


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


def sxt(pat, txt, grp=1):
    m = re.search(pat, txt)
    return m.group(grp) if m else None


def jdec(raw):
    try:
        return json.loads('"' + raw + '"')
    except Exception:
        return raw


def norm_abbrev(s):
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
    return int(v * {"k": 1e3, "m": 1e6, "b": 1e9}.get((m.group(2) or "").lower(), 1))


def parse_join(t):
    if not t:
        return None
    m = re.match(r"([A-Za-z]{3})\w* (\d{1,2}), (\d{4})", t)
    if not m:
        return None
    mo = MONTHS.get(m.group(1), 0)
    return date(int(m.group(3)), mo, int(m.group(2))) if mo else None


def dauer_sek(txt):
    """'13:12' -> 792 · '1:02:33' -> 3753"""
    if not txt:
        return None
    teile = txt.strip().split(":")
    if not all(t.isdigit() for t in teile):
        return None
    s = 0
    for t in teile:
        s = s * 60 + int(t)
    return s


def ci_median(werte):
    """Median mit 95-%-Intervall unter Log-Normal-Annahme.
    Ein Gate, dessen Schwelle im Intervall liegt, ist unentschieden."""
    if not werte:
        return None, None, None
    m = median(werte)
    n = len(werte)
    logs = [math.log10(max(v, 1)) for v in werte]
    sig = stdev(logs) if n >= 3 else SIGMA_FALLBACK
    if sig <= 0:
        sig = SIGMA_FALLBACK
    spanne = 1.96 * sig / math.sqrt(n)
    return int(m), int(10 ** (math.log10(max(m, 1)) - spanne)), int(10 ** (math.log10(max(m, 1)) + spanne))


# ------------------------------------------------------------- 1. Discovery
# Korrekter Filter (empirisch geprueft): EgIQAQ%3D%3D = Typ Video.
# Der alte Wert CAMSAhAB liefert eine Seite ohne videoRenderer-Bloecke.
SEARCH_VIDEO = "&sp=EgIQAQ%3D%3D"


def suche(keyword):
    """-> (treffer, kanaele). treffer = Video-Ebene (Nachfrage),
    kanaele = Owner der Treffer (Fenster). Kein Relevanzfilter noetig."""
    url = ("https://www.youtube.com/results?search_query="
           + quote_plus(keyword.strip()) + SEARCH_VIDEO)
    txt, code, note = fetch(url, f"nsearch__{slug(keyword)}.html")
    if code != 200 or len(txt) < 5000:
        raise MessungFehlgeschlagen(f"Suche '{keyword}': HTTP {code}, {len(txt)} B ({note})")

    bloecke = txt.split('"videoRenderer":')[1:]
    if len(bloecke) < 5:
        raise MessungFehlgeschlagen(
            f"Suche '{keyword}': nur {len(bloecke)} videoRenderer-Blöcke — "
            "Filter oder Parser defekt, KEIN leerer Markt")

    treffer, owner = [], {}
    for blk in bloecke:
        w = blk[:6000]
        mt = re.search(r'"title":\{"runs":\[\{"text":"((?:[^"\\]|\\.){3,200})"\}\]', w)
        mv = re.search(r'"viewCountText":\{"simpleText":"([\d.,  ]+)\s*(?:views|Aufrufe)"', w)
        if not (mt and mv):
            continue
        ziffern = re.sub(r"[^\d]", "", mv.group(1))
        if not ziffern:
            continue
        md = re.search(r'"lengthText":\{.{0,220}?"simpleText":"([\d:]+)"', w)
        mo = re.search(r'"browseId":"(UC[\w-]{20,})","canonicalBaseUrl":"/(@[\w.\-]+)"', w)
        t = {"titel": jdec(mt.group(1)), "views": int(ziffern),
             "dauer_sek": dauer_sek(md.group(1)) if md else None,
             "kanal": mo.group(2) if mo else None}
        treffer.append(t)
        if mo:
            owner.setdefault(mo.group(1), mo.group(2))
    if len(treffer) < 5:
        raise MessungFehlgeschlagen(
            f"Suche '{keyword}': {len(bloecke)} Blöcke, aber nur {len(treffer)} "
            "mit Titel+Views parsebar — Parser defekt")
    return treffer, list(owner.items())


# ------------------------------------------------------------- 2. Erhebung
def kanal_daten(cid, handle=None):
    rec = {"channel_id": cid, "handle": handle, "warn": []}
    url = (f"https://www.youtube.com/{handle}/about" if handle
           else f"https://www.youtube.com/channel/{cid}/about")
    ab, code, note = fetch(url, "nabout__" + (handle or cid).lstrip("@") + ".html")
    if code == 200 and len(ab) > 1000:
        rec["title"] = sxt(r'"title":"([^"]{1,120})","description"', ab)
        rec["subs"] = norm_abbrev(sxt(r'"subscriberCountText":"([^"]*?) subscribers?"', ab))
        rec["join_text"] = sxt(r'"joinedDateText":\{"content":"Joined ([^"]+)"', ab)
        vc = sxt(r'"videoCountText":"([\d,]+) videos?"', ab)
        rec["video_count"] = int(vc.replace(",", "")) if vc else None
        # Identitaetspruefung: loest der Handle auf den erwarteten Kanal auf?
        echte_id = sxt(r'"externalId":"(UC[\w-]+)"', ab)
        if echte_id and echte_id != cid:
            rec["warn"].append(f"handle_kollision:{echte_id}")
    else:
        rec["warn"].append(f"about:{code}:{note}")

    j = parse_join(rec.get("join_text"))
    rec["join_date"] = j.isoformat() if j else None
    rec["alter_monate"] = round((TODAY - j).days / 30.44, 1) if j else None

    rt, rc, rn = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}",
                       "nrss__" + cid + ".xml")
    vids = []
    if rc == 200:
        for e in rt.split("<entry>")[1:]:
            v = sxt(r'<media:statistics views="(\d+)"', e)
            if v is None:
                continue
            p = sxt(r'<published>([^<]+)</published>', e)
            try:
                pd = datetime.fromisoformat(p.replace("Z", "+00:00")).date()
            except Exception:
                pd = None
            vids.append({"titel": html.unescape(sxt(r'<title>([^<]*)</title>', e) or ""),
                         "views": int(v),
                         "alter_tage": (TODAY - pd).days if pd else None})
    else:
        rec["warn"].append(f"rss:{rc}:{rn}")

    vids = vids[:SAMPLE_MAX]
    rec["n_sample"] = len(vids)
    alter = [v["alter_tage"] for v in vids if v["alter_tage"] is not None]
    rec["letzter_upload_tage"] = min(alter) if alter else None
    rec["aktiv"] = rec["letzter_upload_tage"] is not None and rec["letzter_upload_tage"] <= AKTIV_TAGE

    # Kadenz: wie viel ZEIT deckt die Stichprobe ab? Ohne das ist der Median
    # ueber "letzte 15 Uploads" zwischen Kanaelen nicht vergleichbar.
    if len(alter) >= 2:
        rec["kadenz_pro_monat"] = round(len(alter) / max((max(alter) - min(alter)) / 30.44, 0.1), 1)
    else:
        rec["kadenz_pro_monat"] = None

    # Adaptive Reifegrenze: die hoechste Schwelle <=30 T., die >=5 Videos laesst.
    schwelle, reif = None, []
    for s in (REIF_ZIEL, 21, 14, REIF_MIN):
        kand = [v for v in vids if (v["alter_tage"] or 0) >= s]
        if len(kand) >= REIF_MIN_N:
            schwelle, reif = s, kand
            break
    if not reif:
        reif = [v for v in vids if (v["alter_tage"] or 0) >= REIF_MIN]
        schwelle = REIF_MIN
        if len(reif) < REIF_MIN_N:
            rec["warn"].append(f"zu_wenig_reife_videos:{len(reif)}")
    rec["reif_schwelle_tage"] = schwelle
    rec["n_reif"] = len(reif)

    rv = [v["views"] for v in reif]
    m, lo, hi = ci_median(rv)
    rec["median_views"], rec["median_ci_lo"], rec["median_ci_hi"] = m, lo, hi
    rec["max_views"] = max(rv) if rv else None
    rec["views_pro_abo"] = (round(m / rec["subs"], 2)
                            if m and rec.get("subs") else None)
    rec["top_titel"] = max(reif, key=lambda x: x["views"])["titel"] if reif else None
    return rec


# ------------------------------------------------------------- 3. Diagnose
def diagnose(kanaele, treffer, rpm, kosten, ziel, uploads, katalog=KATALOG_FAKTOR):
    d = {"schwellen": {"nachfrage_median": NACHFRAGE_MEDIAN_MIN,
                       "klein_abo_max": KLEIN_ABO_MAX, "klein_hit": KLEIN_HIT_MIN,
                       "thema_quote": THEMA_QUOTE, "katalog_faktor": katalog}}

    # --- Themen-Nachfrage (Video-Ebene) ---
    tv = sorted((t["views"] for t in treffer), reverse=True)
    d["n_treffer"] = len(tv)
    d["treffer_top"] = sorted(treffer, key=lambda t: -t["views"])[:10]
    d["treffer_median"] = int(median(tv)) if tv else None
    d["treffer_ueber_100k"] = sum(1 for v in tv if v >= 100_000)
    d["treffer_quote_100k"] = round(d["treffer_ueber_100k"] / len(tv), 2) if tv else None
    dauern = [t["dauer_sek"] for t in treffer if t.get("dauer_sek")]
    d["treffer_dauer_median_min"] = round(median(dauern) / 60, 1) if dauern else None
    d["treffer_anteil_ueber_40min"] = (round(sum(1 for x in dauern if x > 2400) / len(dauern), 2)
                                       if dauern else None)

    if d["n_treffer"] < MIN_TREFFER:
        d["thema_traegt"] = None
        d["thema_hinweis"] = f"UNGEMESSEN — nur {d['n_treffer']} Treffer (< {MIN_TREFFER})"
    else:
        d["thema_traegt"] = d["treffer_quote_100k"] >= THEMA_QUOTE
        d["thema_hinweis"] = None

    # --- Kanal-Ebene ---
    auswertbar = [k for k in kanaele if k.get("median_views") and k.get("subs")]
    aktiv = [k for k in auswertbar if k.get("aktiv")]
    d["n_kanaele"], d["n_auswertbar"], d["n_aktiv"] = len(kanaele), len(auswertbar), len(aktiv)

    traeger = [k for k in aktiv if k["median_views"] >= NACHFRAGE_MEDIAN_MIN]
    # Unentschieden, wenn die Schwelle im Konfidenzintervall liegt
    grenzfall = [k for k in aktiv
                 if k.get("median_ci_lo") and k.get("median_ci_hi")
                 and k["median_ci_lo"] < NACHFRAGE_MEDIAN_MIN < k["median_ci_hi"]]
    d["traeger"] = [{"kanal": k.get("handle") or k["channel_id"], "subs": k["subs"],
                     "median": k["median_views"], "ci": [k["median_ci_lo"], k["median_ci_hi"]],
                     "kadenz": k.get("kadenz_pro_monat")} for k in traeger]
    d["n_grenzfall"] = len(grenzfall)
    d["nachfrage"] = len(traeger) >= NACHFRAGE_MIN_KANAELE

    klein = [k for k in aktiv if k["subs"] <= KLEIN_ABO_MAX and (k["max_views"] or 0) >= KLEIN_HIT_MIN]
    jung = [k for k in aktiv if (k.get("alter_monate") or 999) <= 18
            and k["median_views"] >= NACHFRAGE_MEDIAN_MIN]
    d["klein_mit_hit"] = [k.get("handle") or k["channel_id"] for k in klein]
    d["jung_und_stark"] = [k.get("handle") or k["channel_id"] for k in jung]
    vpa = [k["views_pro_abo"] for k in aktiv if k.get("views_pro_abo")]
    d["views_pro_abo_median"] = round(median(vpa), 2) if vpa else None

    if d["n_aktiv"] < MIN_AKTIV_FENSTER:
        d["fenster"] = None
        d["fenster_hinweis"] = (f"UNENTSCHEIDBAR — nur {d['n_aktiv']} aktive Kanäle "
                                f"(< {MIN_AKTIV_FENSTER}). Kein Marktbefund.")
    else:
        d["fenster"] = len(klein) >= KLEIN_MIN_ANZAHL or len(jung) >= 1
        d["fenster_hinweis"] = None

    # --- Urteil ---
    if d["thema_traegt"] is None:
        d["feld"], d["urteil"] = "UNGEMESSEN", "grau — Messung reicht nicht. Nicht ins Kill-Log."
    elif not d["thema_traegt"]:
        d["feld"], d["urteil"] = "KEINE NACHFRAGE", "rot — Videos zum Thema tragen keine Reichweite."
    elif d["nachfrage"] and d["fenster"] is True:
        d["feld"], d["urteil"] = "SYSTEM-NISCHE", "grün — rein."
    elif d["nachfrage"] and d["fenster"] is False:
        d["feld"], d["urteil"] = "TRAGFÄHIG, FENSTER ENG", "orange — nur mit echtem Format-Unterschied."
    elif d["nachfrage"] and d["fenster"] is None:
        d["feld"], d["urteil"] = "TRAGFÄHIG, FENSTER UNGEMESSEN", "gelb — Nachfrage belegt, Eintritt offen."
    else:
        d["feld"] = "UNBESETZT MIT NACHFRAGE"
        d["urteil"] = ("grün-gelb — Thema trägt, kaum dedizierte Kanäle. "
                       "Interessanteste Lage; per Pilot bestätigen.")

    # --- Arithmetik ---
    med_sorted = sorted((k["median_views"] for k in aktiv), reverse=True)
    # Benchmark = Median der besten drei statt Maximum (Winner's Curse, s. Kopf)
    d["benchmark_top3"] = int(median(med_sorted[:3])) if med_sorted else None
    d["benchmark_max"] = med_sorted[0] if med_sorted else None
    d["benchmark_abgeschlagen"] = int(d["benchmark_top3"] / 2) if d["benchmark_top3"] else None

    d["rpm"], d["katalog_faktor"] = rpm, katalog
    d["break_even_views"] = round(kosten / (rpm / 1000))
    d["views_monat_fuer_ziel"] = round((ziel / rpm) * 1000)
    d["noetiger_median"] = round(d["views_monat_fuer_ziel"] / (uploads * katalog))
    d["noetiger_median_ohne_katalog"] = round(d["views_monat_fuer_ziel"] / uploads)
    if d["benchmark_top3"] is None:
        d["arithmetik"] = None
    else:
        d["arithmetik"] = d["benchmark_abgeschlagen"] >= d["noetiger_median"]
    return d


# ------------------------------------------------------------- 4. Report
def report(label, keywords, kanaele, d):
    L, A = [], lambda s: L.append(s)
    A(f"# Nischen-Scan: {label}")
    A("")
    A(f"_Erhoben {TODAY.isoformat()} · Keywords: {', '.join(keywords) if keywords else 'Handle-Liste'}_")
    A(f"_{d['n_treffer']} Video-Treffer · {d['n_auswertbar']}/{d['n_kanaele']} Kanäle auswertbar, "
      f"davon {d['n_aktiv']} aktiv · Reifeschwelle adaptiv, Median mit 95-%-Intervall_")
    A("")
    A(f"## Urteil: **{d['feld']}**")
    A(d["urteil"])
    A("")
    A("| Frage | Ergebnis |")
    A("|---|---|")
    if d.get("thema_hinweis"):
        A(f"| **THEMA** (Video-Ebene) | ⚠️ {d['thema_hinweis']} |")
    else:
        A(f"| **THEMA** — ≥{THEMA_QUOTE:.0%} der Treffer ≥100k | "
          f"{'✅ ja' if d['thema_traegt'] else '❌ nein'} — {d['treffer_ueber_100k']}/{d['n_treffer']} "
          f"= {d['treffer_quote_100k']:.0%}, Median {d['treffer_median']:,} |")
    A(f"| **NACHFRAGE** — ≥{NACHFRAGE_MIN_KANAELE} aktive Kanäle Median ≥{NACHFRAGE_MEDIAN_MIN:,} | "
      f"{'✅ ja' if d['nachfrage'] else '❌ nein'} ({len(d['traeger'])} Träger"
      + (f", {d['n_grenzfall']} Grenzfälle im Intervall" if d['n_grenzfall'] else "") + ") |")
    if d.get("fenster_hinweis"):
        A(f"| **FENSTER** | ⚠️ {d['fenster_hinweis']} |")
    else:
        A(f"| **FENSTER** — kleine/junge Kanäle kommen durch | "
          f"{'✅ offen' if d['fenster'] else '❌ eng'} "
          f"({len(d['klein_mit_hit'])} klein / {len(d['jung_und_stark'])} jung"
          + (f", Views/Abo-Median {d['views_pro_abo_median']}" if d.get('views_pro_abo_median') else "")
          + ") |")
    ar = d["arithmetik"]
    A(f"| **ARITHMETIK** — abgeschlagener Benchmark ≥ nötiger Median | "
      f"{'✅' if ar else ('❌' if ar is False else '— keine Daten')} |")
    A("")
    if d.get("treffer_dauer_median_min") is not None:
        A(f"**Format der Nachfrage:** Median-Länge der Treffer **{d['treffer_dauer_median_min']} Min**"
          + (f", {d['treffer_anteil_ueber_40min']:.0%} über 40 Min"
             if d.get('treffer_anteil_ueber_40min') else "")
          + ". *Liegt der Anteil über 40 Min hoch, ist die Nachfrage Sleep-/Longplay-Content — "
            "ein anderes Format als eine 13–15-Min-Doku.*")
        A("")
    if d["traeger"]:
        A("**Träger:** " + " · ".join(
            f"{t['kanal']} ({t['subs']:,} Abos, Median {t['median']:,} "
            f"[{t['ci'][0]:,}–{t['ci'][1]:,}]"
            + (f", {t['kadenz']}/Mon" if t.get("kadenz") else "") + ")" for t in d["traeger"][:6]))
        A("")
    A("### Arithmetik")
    A(f"- RPM **${d['rpm']}** · Katalogfaktor **{d['katalog_faktor']}×** · "
      f"Break-even **{d['break_even_views']:,} Views/Folge**")
    A(f"- Ziel braucht **{d['views_monat_fuer_ziel']:,} Views/Monat** → nötiger Median "
      f"**{d['noetiger_median']:,}/Folge** *(ohne Katalogfaktor wären es "
      f"{d['noetiger_median_ohne_katalog']:,})*")
    if d["benchmark_top3"]:
        A(f"- Benchmark = Median der besten 3 aktiven Kanäle: **{d['benchmark_top3']:,}** "
          f"(Maximum wäre {d['benchmark_max']:,})")
        A(f"- **Nach Winner's-Curse-Abschlag (÷2): {d['benchmark_abgeschlagen']:,}** ← damit wird gerechnet")
    A("")
    if d.get("treffer_top"):
        A("### Top-Videos zum Thema")
        A("")
        A("| Views | Länge | Kanal | Titel |")
        A("|---:|---:|---|---|")
        for t in d["treffer_top"]:
            dm = f"{t['dauer_sek']//60}:{t['dauer_sek']%60:02d}" if t.get("dauer_sek") else "?"
            A(f"| {t['views']:,} | {dm} | {t.get('kanal') or '?'} | {t['titel'][:60]} |")
        A("")
    A("### Kanäle")
    A("")
    A("| Kanal | Abos | Alter M. | Median [95-%-Intervall] | n reif | Kadenz/Mon | V/Abo | Letzter Upload |")
    A("|---|---:|---:|---:|---:|---:|---:|---:|")
    for k in sorted(kanaele, key=lambda x: -(x.get("median_views") or 0)):
        if not k.get("median_views"):
            continue
        flag = " 💤" if not k.get("aktiv") else ""
        if k.get("warn"):
            flag += " ⚠︎"
        subs = f"{k['subs']:,}" if k.get("subs") is not None else "?"
        alt_m = k["alter_monate"] if k.get("alter_monate") is not None else "?"
        lu = k.get("letzter_upload_tage")
        A(f"| {k.get('handle') or k['channel_id']}{flag} | {subs} | {alt_m} "
          f"| {k['median_views']:,} [{k['median_ci_lo']:,}–{k['median_ci_hi']:,}] "
          f"| {k['n_reif']} | {k.get('kadenz_pro_monat') or '?'} "
          f"| {k.get('views_pro_abo') or '?'} "
          f"| {str(lu) + ' T.' if lu is not None else '?'} |")
    A("")
    warn = [f"{k.get('handle') or k['channel_id']}: {', '.join(k['warn'])}"
            for k in kanaele if k.get("warn")]
    if warn:
        A("_⚠︎ Warnungen: " + " · ".join(warn[:8]) + "_")
        A("")
    A("> **Grenzen:** RSS liefert nur die letzten ~15 Uploads → aktueller, kein Lebenszeit-Median. "
      "Die Kadenz-Spalte zeigt, wie viel Zeit die Stichprobe abdeckt — bei hoher Kadenz ist das "
      "wenig. Schwellen sind Heuristiken (Stufe B), an eigenen Daten kalibrierbar. "
      "Ein Median, dessen Intervall die Schwelle einschließt, ist **unentschieden**, nicht bestanden.")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords", nargs="*", help="1–3 Suchbegriffe (System verlangt 3)")
    ap.add_argument("--handles", help="Datei mit @handles/UC-IDs statt Suche")
    ap.add_argument("--label")
    ap.add_argument("--limit", type=int, default=25)
    ap.add_argument("--rpm", type=float, default=2.31)
    ap.add_argument("--kosten", type=float, default=38.0)
    ap.add_argument("--ziel", type=float, default=10000.0)
    ap.add_argument("--uploads", type=float, default=8.0)
    ap.add_argument("--katalog", type=float, default=KATALOG_FAKTOR)
    a = ap.parse_args()
    if not a.keywords and not a.handles:
        ap.error("keywords oder --handles nötig")
    label = a.label or " / ".join(a.keywords) or os.path.basename(a.handles)

    treffer, kand = [], {}
    try:
        if a.handles:
            for line in open(a.handles):
                s = line.strip()
                if s and not s.startswith("#"):
                    kand[s] = s if s.startswith("UC") else None
            kand = {None: h for h in []} or {k: (k if k.startswith("UC") else None)
                                             for k in kand}
            print(f"[1/3] {len(kand)} Kanäle aus Datei", file=sys.stderr)
            paare = [(v, k if not k.startswith("UC") else None) for k, v in kand.items()]
        else:
            if len(a.keywords) < 3:
                print(f"  ! WARNUNG: nur {len(a.keywords)} Keyword(s). Das System verlangt 3 — "
                      "die Streuung zwischen Formulierungen erreichte im Test Faktor 56.",
                      file=sys.stderr)
            gesehen = {}
            for kw in a.keywords:
                print(f"[1/3] Suche: {kw}", file=sys.stderr)
                tr, own = suche(kw)
                treffer += tr
                for cid, h in own:
                    gesehen.setdefault(cid, h)
            paare = list(gesehen.items())[:a.limit]
            print(f"      {len(treffer)} Treffer, {len(paare)} Kanäle", file=sys.stderr)

        kanaele = []
        for i, (cid, h) in enumerate(paare, 1):
            if cid is None or not str(cid).startswith("UC"):
                ab, code, _ = fetch(f"https://www.youtube.com/{h}/about",
                                    "nres__" + str(h).lstrip("@") + ".html")
                cid = sxt(r'"externalId":"(UC[\w-]+)"', ab) if code == 200 else None
                if not cid:
                    print(f"      [{i}] {h}: keine channel_id", file=sys.stderr)
                    continue
            print(f"[2/3] [{i}/{len(paare)}] {h or cid}", file=sys.stderr)
            kanaele.append(kanal_daten(cid, h))

        print("[3/3] Diagnose …", file=sys.stderr)
        d = diagnose(kanaele, treffer, a.rpm, a.kosten, a.ziel, a.uploads, a.katalog)
    except MessungFehlgeschlagen as e:
        print(f"\n## MESSUNG FEHLGESCHLAGEN\n\n{e}\n\n"
              "**Kein Urteil.** Dieser Kandidat darf NICHT als 'keine Nachfrage' "
              "ins Kill-Log — er wurde nicht gemessen.", file=sys.stdout)
        print(f"MESSUNG FEHLGESCHLAGEN: {e}", file=sys.stderr)
        sys.exit(2)

    print(report(label, a.keywords, kanaele, d))
    p = os.path.join(OUT, slug(label) + ".json")
    json.dump({"label": label, "keywords": a.keywords, "erhoben": TODAY.isoformat(),
               "parameter": vars(a), "diagnose": d, "kanaele": kanaele},
              open(p, "w"), ensure_ascii=False, indent=1)
    print(f"\n_JSON: {os.path.relpath(p, HERE)}_")


if __name__ == "__main__":
    main()
