#!/usr/bin/env python3
"""Skript-Linter — macht die schon beschlossenen Regeln maschinell pruefbar (ab F5).

Warum ueberhaupt Code? Weil eine Regel, die nur als Prosa im Playbook steht, still
uebersprungen wird. Beleg aus unserer eigenen Historie: die QC-Regel fuer eingebrannten
Text war Prosa — erst als sie ein Skript wurde (qc_textscan.py), fand sie 3 Slop-Clips
in bereits FERTIGEN Mastern. Dasselbe Prinzip hier fuer das VO-Skript.

Geprueft werden nur Regeln, die bereits verbindlich sind:
  §5c  max. 2 Eigennamen · keine Fachzahlen im VO · Satzlaenge · Fremdwort-Test
  ⚠️   ship-blocking: keine unaufgeloeste Markierung darf in die Vertonung
  R6   Laenge 13-15 Min (bei 152 wpm, unsere real gemessene Sprechrate)
  Schaufenster-Regel (optional, --packaging): kein Verdict/keine Verneinung im Schaufenster

Nutzung:
  python3 skript_lint.py ../../skript/signal-04-VO.md
  python3 skript_lint.py ../../skript/signal-05-VO.md --packaging ../folge-05/UPLOAD-PAKET-F5.md
Exit-Code 1 = ship-blocking (FAIL). WARN blockiert nicht, will aber eine Entscheidung.
"""
import argparse, re, sys, unicodedata
from collections import Counter

WPM = 152                     # real gemessen an F2 (nicht geschaetzt)
TARGET_MIN, TARGET_MAX = 13 * 60, 15 * 60

# Zeilen, die keine gesprochene Sprache sind
SKIP_LINE = re.compile(r"^\s*(═|#|>|\||\[|Stimme:|Live-Check)")

# Satzanfang / Funktionswoerter, die gross geschrieben auftauchen, aber keine Namen sind
NOT_A_NAME = set("""
A An And As At But By For From He How I If In It Its Just No Not Now Of On One Or So Somewhere
That The Their Then There They This To We What When Where Which While Who Why Yes You Your
Because Before After Every Each Here His Her Him Our Us Do Does Did Is Are Was Were Be Been
Earth Sun Moon Space Signal Noise Tonight Yesterday Today Monday Tuesday Wednesday Thursday
Friday Saturday Sunday January February March April May June July August September October
November December Ohio
I'm I'll I've I'd We're We'll We've It's That's There's Here's Don't Let's
""".split())

# Fachzahlen/Einheiten, die laut §5c NICHT ins VO gehoeren (Zahl + Fachnotation)
NUMBER_JARGON = [
    (r"\b\d+(?:[.,]\d+)?\s*(?:σ|sigma)\b", "Sigma-Wert"),
    (r"\b\d+(?:[.,]\d+)?\s*(?:ppm|ppb)\b", "ppm/ppb"),
    (r"\b\d+(?:[.,]\d+)?\s*AU\b", "Astronomische Einheit"),
    (r"\b\d+(?:[.,]\d+)?\s*(?:MHz|GHz|kHz|Hz)\b", "Frequenz-Einheit"),
    (r"\b\d+(?:[.,]\d+)?\s*(?:Jy|jansky)\b", "Jansky"),
    (r"\b\d+(?:[.,]\d+)?\s*km/s\b", "km/s"),
    (r"\b\d+(?:[.,]\d+)?\s*(?:ly|light-?years?)\b", "Lichtjahr-Zahl"),
    (r"\b\d+(?:[.,]\d+)?\s*%", "Prozentzahl"),
    (r"\b\d+[.,]\d+\b", "Dezimalzahl"),
    (r"\b\d\s*[×x]\s*10", "Zehnerpotenz"),
]

# Fremdwoerter: Fachbegriff -> Alltagsformulierung, die wir stattdessen wollen
JARGON = {
    "spectroscopy": "das Licht in seine Farben zerlegen",
    "spectrum": "Farbmuster",
    "anisotropy": "die eine Richtung, die anders ist",
    "isotropic": "in alle Richtungen gleich",
    "interferometry": "mehrere Teleskope als eines",
    "biosignature": "ein Zeichen von Leben",
    "technosignature": "ein Zeichen von Technik",
    "narrowband": "auf einer einzigen Frequenz",
    "statistical significance": "wie leicht Zufall das erklaert",
    "confidence interval": "die Spanne, in der es liegt",
    "false positive": "Fehlalarm",
    "photometric": "Helligkeits-",
    "radial velocity": "das Wackeln des Sterns",
    "occultation": "wenn etwas davorzieht",
    "albedo": "wie hell etwas zurueckwirft",
    "outgassing": "ausgasen",
    "perihelion": "der sonnennaechste Punkt",
    "hypothesis": "Vermutung",
    "empirical": "gemessen",
    "extrapolate": "hochrechnen",
    "corroborate": "bestaetigen",
    "unprecedented": "so noch nie",
    "paradigm": "Denkmuster",
}

SHOWCASE_FORBIDDEN = [
    r"\bnot\s+(?:life|alien|aliens|a\s+signal)\b", r"\bwasn'?t\b", r"\bisn'?t\b",
    r"\bno\s+(?:aliens|life|signal)\b", r"\bdebunk\w*\b", r"\bjust\s+noise\b",
    r"\bnothing\s+but\b", r"\bhoax\b",
]


def read_vo(path):
    """Nur gesprochenen Text zurueckgeben (Regie-Marker und Header raus)."""
    lines = []
    for ln in open(path, encoding="utf-8"):
        if SKIP_LINE.match(ln):
            continue
        ln = re.sub(r"\[[^\]]*\]", " ", ln)          # [BEAT] [SFX: ...] entfernen
        if ln.strip():
            lines.append(ln.strip())
    return "\n".join(lines)


def sentences(text):
    flat = re.sub(r"\s+", " ", text.replace("…", "."))
    parts = re.split(r"(?<=[.!?])\s+", flat)
    return [p.strip() for p in parts if len(p.split()) >= 2]


def find_names(text):
    """Kandidaten fuer Eigennamen: Grossschreibung NICHT am Satzanfang.

    Aufeinanderfolgende Grosswoerter werden zu EINEM Namen zusammengezogen —
    sonst zaehlt „Big Ear" als zwei und „Puerto Rico" als zwei.
    """
    hits = Counter()
    for s in sentences(text):
        body = s.split(" ", 1)[1] if " " in s else ""      # Satzanfang ueberspringen
        for grp in re.findall(r"(?:[A-Z][\w'’-]*(?:\s+(?=[A-Z]))?)+", body):
            name = grp.strip()
            if not name or all(t in NOT_A_NAME for t in name.split()):
                continue
            name = re.sub(r"['’]s\b", "", name.rstrip(".,!?;:"))   # „Earth's" = „Earth"
            hits[name] += 1
    # Ein einmaliges Grossschreiben ist meist Satzanfang nach Gedankenstrich o.ae.
    return {k: v for k, v in hits.items() if v >= 2}


def report(label, level, items, hint=""):
    if not items:
        print(f"  ✅ {label}")
        return 0
    icon = "⛔" if level == "FAIL" else "⚠️ "
    print(f"  {icon} {level}: {label}")
    for it in items[:12]:
        print(f"       · {it}")
    if len(items) > 12:
        print(f"       · … und {len(items) - 12} weitere")
    if hint:
        print(f"       → {hint}")
    return 1 if level == "FAIL" else 0


def lint(path, packaging=None):
    raw = open(path, encoding="utf-8").read()
    text = read_vo(path)
    words = len(text.split())
    secs = words / WPM * 60
    sents = sentences(text)
    lens = sorted(len(s.split()) for s in sents)
    median = lens[len(lens) // 2] if lens else 0
    longs = [s for s in sents if len(s.split()) > 25]

    print(f"\n📄 {path}")
    print(f"   {words} Woerter · {len(sents)} Saetze · geschaetzte Laufzeit "
          f"{int(secs)//60}:{int(secs)%60:02d} @ {WPM} wpm")
    fails = 0

    # 1. ⚠️-Regel — ship-blocking, wird auf dem ROHTEXT geprueft (auch Header/Marker)
    warns = [ln.strip()[:110] for ln in raw.splitlines() if "⚠️" in ln]
    fails += report("⚠️-Regel: keine unaufgeloeste Markierung im Skript", "FAIL", warns,
                    'Vor der Vertonung belegen oder streichen — kein „spaeter pruefen“.')

    # 2. Laenge (Regel 6)
    bad_len = [] if TARGET_MIN <= secs <= TARGET_MAX else [
        f"{int(secs)//60}:{int(secs)%60:02d} liegt ausserhalb 13:00–15:00 "
        f"(Ziel {int(TARGET_MIN/60*WPM)}–{int(TARGET_MAX/60*WPM)} Woerter, aktuell {words})"]
    fails += report("Regel 6: Laufzeit 13–15 Min", "WARN", bad_len)

    # 3. §5c Eigennamen
    names = find_names(text)
    over = [f"{k} ({v}×)" for k, v in sorted(names.items(), key=lambda x: -x[1])]
    lvl_items = over if len(names) > 2 else []
    fails += report(f"§5c: max. 2 Eigennamen (gefunden: {len(names)})", "WARN", lvl_items,
                    'Rest in Rollen aufloesen: „ein Team in Chicago“, „der Chefastronom“.')

    # 4. §5c Fachzahlen
    numhits = []
    for pat, name in NUMBER_JARGON:
        for m in re.finditer(pat, text, re.I):
            ctx = text[max(0, m.start() - 30):m.end() + 25].replace("\n", " ")
            numhits.append(f"{name}: …{ctx.strip()}…")
    fails += report("§5c: keine Fachzahlen im VO", "FAIL", numhits,
                    "Exakte Werte gehoeren in Beschreibung + Quellen-Chip, nicht ins Voiceover.")

    # 5. §5c Satzlaenge
    lenprob = []
    if median > 15:
        lenprob.append(f"Median {median} Woerter/Satz (Ziel 10–13)")
    if len(longs) > len(sents) * 0.10:
        lenprob.append(f"{len(longs)} Saetze ueber 25 Woerter ({len(longs)/len(sents)*100:.0f} %, Ziel ≤10 %)")
    if lenprob:                                   # Beispiele nur zeigen, wenn es klemmt
        for s in longs[:5]:
            lenprob.append(f"{len(s.split())} W: {s[:95]}…")
    fails += report(f"§5c: Satzlaenge (Median {median} W)", "WARN", lenprob)

    # 6. §5c Fremdwort-Test
    jarg = [f"{w} → besser: {alt}" for w, alt in JARGON.items()
            if re.search(rf"\b{re.escape(w)}\b", text, re.I)]
    fails += report("§5c: Fremdwort-Test", "WARN", jarg)

    # 7. Schaufenster-Regel (optional)
    if packaging:
        ptext = open(packaging, encoding="utf-8").read()
        head = "\n".join(ptext.splitlines()[:70])          # Titel + Beschreibungskopf
        sc = []
        for pat in SHOWCASE_FORBIDDEN:
            for m in re.finditer(pat, head, re.I):
                sc.append(f"…{head[max(0, m.start()-45):m.end()+35].strip()}…")
        print(f"\n🪟 Schaufenster: {packaging}")
        fails += report("Schaufenster-Regel: kein Verdict/keine Verneinung", "FAIL", sc,
                        "Das Schaufenster verkauft die FRAGE. Das Urteil faellt IM Video.")

    return fails


def main():
    p = argparse.ArgumentParser()
    p.add_argument("vo", nargs="+", help="VO-Skript(e), z. B. skript/signal-05-VO.md")
    p.add_argument("--packaging", help="Upload-Paket fuer den Schaufenster-Check")
    a = p.parse_args()
    fails = sum(lint(v, a.packaging) for v in a.vo)
    print(f"\n{'⛔ SHIP-BLOCKING: ' + str(fails) + ' Regel(n) verletzt' if fails else '✅ keine ship-blocking Verletzung'}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
