# -*- coding: utf-8 -*-
"""Wie viel Material laesst sich in einem Unlimited-Fenster erzeugen?

WARUM EIN EIGENES WERKZEUG: Bei Unlimited ist der Preis nicht mehr die
Grenze. Es gibt dann DREI Grenzen, und man muss die kleinste finden:

    1. MASCHINE   parallele Slots x Fensterstunden / Generierungsdauer
    2. VORLAGE    wie viele Skripte + Shotlisten liegen fertig vor?
    3. NACHBEARBEITUNG  Schnitt, VO, QC - Menschenstunden

Wer nur (1) rechnet, plant an der Realitaet vorbei. Fuer Story-Content ist
fast immer (2) die Bindung, weil jeder Shot GENAU EINEN Story-Beat bedient
und nicht wie Weltraum-Footage generisch nachnutzbar ist.

GEMESSEN vs. ANGENOMMEN:
    Parallel-Slots 8/8      -> aus dem Ultra-Plan (show_plans_and_credits)
    Stueckkosten Cr         -> eigene Messung, produktion/folge-01-v4/budget-ledger.md
    Generierungsdauer       -> ANGENOMMEN, nicht gemessen (skaliert linear!)
    Effizienzfaktor 0,6     -> ANGENOMMEN (Queue, Fehlschlaege, Re-Rolls)

Aufruf:
    python3 unlim_durchsatz.py --tage 14 --preis 999 --stufe 4k --gen 4 6 10
    python3 unlim_durchsatz.py --tage 14 --preis 999 --stufe 4k --skripte 12
"""
import argparse

SLOTS_VIDEO = 8
SLOTS_BILD = 8
EFFIZIENZ = 0.6
GEN_MIN_BILD = 0.5
SHOT_SEK = 5.0
CR_EUR = 95 / 2000
CR_S = {"720p": 3.5, "1080p": 9.0, "4k": 22.0}   # gemessen
BILD_CR = {"1k": 2.0, "2k": 4.0}                  # gemessen
STILL_SEK = 8.0

FORMATE = {
    "Fantasy-Story 20 Min":  {"dauer": 1221, "deckung": 1.00},
    "Fantasy-Story 12 Min":  {"dauer":  742, "deckung": 1.00},
    "Sleep-Doku 2 h (50 %)": {"dauer": 7200, "deckung": 0.50},
    "SIGNAL 13 Min (8 %)":   {"dauer":  792, "deckung": 0.08},
}
# Menschenstunden je Video, aus unserem eigenen Prozess hochgerechnet
H_SKRIPT = 5.0      # §15 Skript-Werkstatt, 6 Durchgaenge
H_SHOTLISTE = 3.5   # 244 Shot-Prompts erzeugen + durchsehen
H_QC = 1.0          # qc_textscan.py + Stichproben
H_SCHNITT_JE_100 = 4.0   # Assemble + VO-Sync je 100 Clips
H_PACKAGING = 2.0   # Thumbnail, Titel, Beschreibung, Upload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tage", type=float, default=14)
    ap.add_argument("--stunden", type=float, default=24)
    ap.add_argument("--preis", type=float, default=999, help="Paketpreis in EUR")
    ap.add_argument("--stufe", choices=list(CR_S), default="4k")
    ap.add_argument("--gen", type=float, nargs="+", default=[4, 6, 10],
                    help="Minuten je Video-Generierung (Annahmen)")
    ap.add_argument("--slots", type=int, default=SLOTS_VIDEO)
    ap.add_argument("--skripte", type=int, default=None,
                    help="Zahl fertiger Skripte -> Vorlagen-Grenze")
    ap.add_argument("--menschstd", type=float, default=10.0,
                    help="verfuegbare Arbeitsstunden pro Tag fuer Nachbearbeitung")
    a = ap.parse_args()

    fenster_h = a.tage * a.stunden
    cr_s = CR_S[a.stufe]

    print(f"# Unlimited-Paket · {a.tage:g} Tage · {a.preis:,.0f} EUR · Stufe {a.stufe}")
    print(f"\n{a.slots} parallele Slots · {a.stunden:g} h/Tag = {fenster_h:g} Betriebsstunden "
          f"· Effizienz {EFFIZIENZ:.0%}\n")

    # ---------- Grenze 1: Maschine
    print("## Grenze 1 — Maschine\n")
    print("| Dauer je Gen. | Clips/Std | **Clips im Fenster** | Sekunden | Std. Material |")
    print("|---:|---:|---:|---:|---:|")
    kap = {}
    for g in a.gen:
        pro_h = a.slots * (60 / g) * EFFIZIENZ
        n = pro_h * fenster_h
        kap[g] = n
        print(f"| {g:g} Min | {pro_h:,.0f} | **{n:,.0f}** | {n*SHOT_SEK:,.0f} | "
              f"{n*SHOT_SEK/3600:,.1f} h |")

    print(f"\n**Bilder** (start_image): {SLOTS_BILD*(60/GEN_MIN_BILD)*EFFIZIENZ:,.0f}/Std "
          f"-> {SLOTS_BILD*(60/GEN_MIN_BILD)*EFFIZIENZ*fenster_h:,.0f} im Fenster\n")

    # ---------- Videos je Format
    print("## Videos je Format (nur Maschinen-Grenze)\n")
    kopf = " | ".join(f"@{g:g}Min" for g in a.gen)
    print(f"| Format | Clips/Video | {kopf} | Regulaerer Preis je Video |")
    print("|---|---:|" + "---:|" * len(a.gen) + "---:|")
    for name, f in FORMATE.items():
        ki = f["dauer"] * f["deckung"]
        n_clips = ki / SHOT_SEK
        wert = ki * cr_s + n_clips * BILD_CR["1k"]
        zellen = " | ".join(f"{kap[g]/n_clips:,.0f}" for g in a.gen)
        print(f"| {name} | {n_clips:,.0f} | {zellen} | "
              f"{wert:,.0f} Cr = **{wert*CR_EUR:,.0f} EUR** |")

    # ---------- Break-even des Pakets
    ref = FORMATE["Fantasy-Story 20 Min"]
    ki = ref["dauer"] * ref["deckung"]
    wert_ref = (ki * cr_s + ki / SHOT_SEK * BILD_CR["1k"]) * CR_EUR
    print(f"\n> **Break-even des Pakets: {a.preis/wert_ref:.2f} Videos.** "
          f"Ein einziges 20-Min-Video in {a.stufe} kostet regulaer {wert_ref:,.0f} EUR — "
          f"das Paket kostet {a.preis:,.0f} EUR.")

    # ---------- Grenze 2+3
    if a.skripte:
        n_clips = ref["dauer"] * ref["deckung"] / SHOT_SEK
        h_je = (H_SKRIPT + H_SHOTLISTE + H_QC + H_PACKAGING
                + H_SCHNITT_JE_100 * n_clips / 100)
        print(f"\n## Grenze 2 — Vorlage: **{a.skripte} fertige Skripte**")
        print(f"\n## Grenze 3 — Nachbearbeitung\n")
        print(f"Menschenstunden je 20-Min-Story-Video: Skript {H_SKRIPT:.0f} + "
              f"Shotliste {H_SHOTLISTE:.1f} + QC {H_QC:.0f} + Schnitt "
              f"{H_SCHNITT_JE_100*n_clips/100:.1f} ({n_clips:.0f} Clips) + "
              f"Packaging {H_PACKAGING:.0f} = **{h_je:.1f} h**")
        im_fenster = a.tage * a.menschstd / h_je
        print(f"\nIm Fenster fertig editierbar bei {a.menschstd:g} h/Tag: "
              f"**{im_fenster:.1f} Videos**")
        eng = min(min(kap.values()) / n_clips, a.skripte)
        print(f"\n### Bindende Grenze")
        print(f"\n| Grenze | Videos |\n|---|---:|")
        print(f"| 1 Maschine (schlechtester Fall) | {min(kap.values())/n_clips:,.0f} |")
        print(f"| 2 Vorlage | {a.skripte} |")
        print(f"| 3 Nachbearbeitung im Fenster | {im_fenster:.0f} |")
        print(f"\n**Generieren kann man {eng:.0f} Videos** (Grenze 1+2). "
              f"Schneiden dauert danach {eng*h_je/a.menschstd:.0f} Arbeitstage — "
              f"das laeuft NACH dem Fenster weiter und ist kein Problem, "
              f"solange die Kadenz stimmt.")
        gesamt = eng * wert_ref
        print(f"\n**Gegenwert: {eng:.0f} x {wert_ref:,.0f} EUR = {gesamt:,.0f} EUR "
              f"fuer {a.preis:,.0f} EUR = Faktor {gesamt/a.preis:.0f}.**")
        print(f"\n**Grenzkosten je Video danach: {a.preis/eng:,.0f} EUR** "
              f"(nur Paketanteil; Bilder/VO extra).")


if __name__ == "__main__":
    main()
