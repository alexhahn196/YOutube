# -*- coding: utf-8 -*-
"""Higgsfield-Kostenrechner fuer eine Folge.

WARUM: Die Frage "was kostet so ein Video" wird regelmaessig falsch gerechnet,
weil man in CLIPS denkt. Higgsfield rechnet aber in SEKUNDEN Ausgabe-Video.
Ob 245 Clips a 5 s oder 153 Clips a 8 s - beides sind 1.221 s und kostet
dasselbe. Die einzige Groesse, die die Rechnung wirklich bewegt, ist die
KI-VIDEO-DECKUNG: welcher Anteil der Laufzeit ist generiertes Bewegtbild
(teuer) statt Standbild-mit-Kamerafahrt, Archivmaterial oder Reuse (0 Cr).

STUECKKOSTEN sind eigene Messwerte, nicht Listenpreise
(produktion/folge-01-v4/budget-ledger.md, "get_cost verifiziert"):
    Seedance 720p/fast/5s  =  17,5 Cr  ->  3,5 Cr/s
    Seedance 1080p/std/5s  =  45   Cr  ->  9,0 Cr/s
    Seedance 4k/high/5s    = 110   Cr  -> 22,0 Cr/s
    Nano Banana Pro 1k = 2 Cr · 2k = 4 Cr   (start_image je Shot)
    Kurs: 2.000 Cr = 95 EUR  ->  0,0475 EUR/Cr

BELEG, dass die Rechnung stimmt: F3 663,5 Cr / F4 681,5 Cr Ist-Verbrauch bei
13 Video-Generierungen a 5 s 1080p + 4K-Hero. Nachrechnen mit --dauer 780
--deckung 0.08 trifft diese Groessenordnung.

Aufruf:
    python3 kosten_kalk.py --dauer 1221            # ein Video, alle Stufen
    python3 kosten_kalk.py --dauer 780 --deckung 0.08 --stufe 1080p
"""
import argparse

CR_EUR = 95 / 2000            # 0,0475 EUR pro Credit
STUFEN = {                     # Cr pro Sekunde Ausgabe-Video
    "720p":  {"cr_s":  3.5, "label": "720p / fast"},
    "1080p": {"cr_s":  9.0, "label": "1080p / std"},
    "4k":    {"cr_s": 22.0, "label": "4K / high"},
}
BILD_CR = 2.0                  # start_image 1k je Shot
SHOT_SEK_STD = 5.0             # ein Shot = 5 s (Modell-Default)
DECKUNGEN = [0.08, 0.25, 0.50, 0.75, 1.00]
REROLL = {"gut": 1.3, "real": 1.8}   # F3/F4 lagen bei 1,08-1,42; Story-Content hoeher


def rechne(dauer_s, deckung, cr_s, reroll, shot_s=SHOT_SEK_STD):
    """-> dict. Bilder skalieren mit der SHOT-ZAHL, Video mit den SEKUNDEN."""
    ki_sek = dauer_s * deckung
    shots = ki_sek / shot_s
    video_cr = ki_sek * cr_s
    bild_cr = shots * BILD_CR
    cr = (video_cr + bild_cr) * reroll
    return {"ki_sek": ki_sek, "shots": shots, "cr": cr, "eur": cr * CR_EUR}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dauer", type=float, required=True, help="Laufzeit in Sekunden")
    ap.add_argument("--deckung", type=float, help="KI-Video-Anteil 0..1 (ohne = Tabelle)")
    ap.add_argument("--stufe", choices=list(STUFEN), help="ohne = alle Stufen")
    ap.add_argument("--shot", type=float, default=SHOT_SEK_STD, help="Shotlaenge in s")
    a = ap.parse_args()

    m, s = divmod(int(a.dauer), 60)
    print(f"# Higgsfield-Kosten fuer {m}:{s:02d} ({a.dauer:.0f} s) · Shot {a.shot:.0f} s\n")
    print(f"Kurs {CR_EUR:.4f} EUR/Cr · Bild {BILD_CR:.0f} Cr/Shot · "
          f"Reroll gut {REROLL['gut']}x / real {REROLL['real']}x\n")

    stufen = [a.stufe] if a.stufe else list(STUFEN)
    deck = [a.deckung] if a.deckung is not None else DECKUNGEN

    for st in stufen:
        cr_s = STUFEN[st]["cr_s"]
        print(f"## {STUFEN[st]['label']} ({cr_s:.1f} Cr/s = "
              f"{cr_s*60*CR_EUR:,.2f} EUR pro Minute KI-Video)\n")
        print("| KI-Deckung | KI-Sek | Shots | Cr (gut) | EUR (gut) | Cr (real) | EUR (real) |")
        print("|---:|---:|---:|---:|---:|---:|---:|")
        for d in deck:
            g = rechne(a.dauer, d, cr_s, REROLL["gut"], a.shot)
            r = rechne(a.dauer, d, cr_s, REROLL["real"], a.shot)
            print(f"| {d:.0%} | {g['ki_sek']:,.0f} | {g['shots']:,.0f} | "
                  f"{g['cr']:,.0f} | {g['eur']:,.0f} EUR | "
                  f"{r['cr']:,.0f} | {r['eur']:,.0f} EUR |")
        print()


if __name__ == "__main__":
    main()
