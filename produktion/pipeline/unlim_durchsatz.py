# -*- coding: utf-8 -*-
"""Wie viel Material laesst sich in einem Unlimited-Fenster erzeugen?

WARUM EIN EIGENES WERKZEUG: Bei Unlimited ist der Preis nicht mehr die
Grenze - der DURCHSATZ ist es. Die Bindung ist die Zahl paralleler Jobs
(Ultra: 8 Video + 8 Bild gleichzeitig) mal Fenster-Stunden geteilt durch
die Generierungsdauer. Wer in "unbegrenzt" denkt, plant falsch; wer in
"8 Slots" denkt, plant richtig.

GEMESSEN vs. ANGENOMMEN:
    Parallel-Slots 8/8      -> aus dem Ultra-Plan (Beleg, show_plans_and_credits)
    Stueckkosten Cr         -> eigene Messung, produktion/folge-01-v4/budget-ledger.md
    Generierungsdauer       -> ANGENOMMEN (2/3/5 Min), nicht gemessen
    Effizienzfaktor 0,6     -> ANGENOMMEN (Queue, Fehlschlaege, Re-Rolls)

Aufruf:
    python3 unlim_durchsatz.py                          # Standard: 7 Tage
    python3 unlim_durchsatz.py --tage 1 --stunden 12
"""
import argparse

SLOTS_VIDEO = 8
SLOTS_BILD = 8
EFFIZIENZ = 0.6
GEN_MIN = [2, 3, 5]          # Minuten je Video-Generierung (Annahme)
GEN_MIN_BILD = 0.5           # Minuten je Bild-Generierung (Annahme)
SHOT_SEK = 5.0
CR_EUR = 95 / 2000
CR_S_720 = 3.5               # Cr pro Sekunde 720p (gemessen)
BILD_CR_2K = 4.0             # Nano Banana Pro 2k (gemessen)

FORMATE = {
    "SIGNAL 13 Min (8 % Deckung)":      {"dauer": 792,  "deckung": 0.08},
    "Story 20 Min (100 % Deckung)":     {"dauer": 1221, "deckung": 1.00},
    "Sleep-Doku 2 h (50 % Deckung)":    {"dauer": 7200, "deckung": 0.50},
    "Sleep-Doku 2 h (Standbild-Weg)":   {"dauer": 7200, "deckung": 0.00},
}
STILL_SEK = 8.0              # ein Standbild traegt 8 s Kamerafahrt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tage", type=float, default=7)
    ap.add_argument("--stunden", type=float, default=24,
                    help="betriebene Stunden pro Tag (Skript laeuft unbeaufsichtigt: 24)")
    a = ap.parse_args()
    fenster_h = a.tage * a.stunden

    print(f"# Unlimited-Durchsatz · {a.tage:g} Tage x {a.stunden:g} h = {fenster_h:g} Betriebsstunden")
    print(f"\n{SLOTS_VIDEO} parallele Video-Slots · Effizienz {EFFIZIENZ:.0%} "
          f"(Queue/Fehlschlaege/Re-Rolls)\n")

    print("## Rohdurchsatz Video (5-s-Clips)\n")
    print("| Dauer je Gen. | Clips/Std | **Clips im Fenster** | Sekunden Material | Std. Material |")
    print("|---:|---:|---:|---:|---:|")
    clips = {}
    for g in GEN_MIN:
        pro_h = SLOTS_VIDEO * (60 / g) * EFFIZIENZ
        n = pro_h * fenster_h
        clips[g] = n
        print(f"| {g} Min | {pro_h:,.0f} | **{n:,.0f}** | {n*SHOT_SEK:,.0f} | {n*SHOT_SEK/3600:,.1f} h |")

    pro_h_b = SLOTS_BILD * (60 / GEN_MIN_BILD) * EFFIZIENZ
    bilder = pro_h_b * fenster_h
    print(f"\n**Bilder:** {pro_h_b:,.0f}/Std -> **{bilder:,.0f} Bilder im Fenster** "
          f"(je {GEN_MIN_BILD*60:.0f} s Generierung)\n")

    print("## Wie viele Videos ergibt das?\n")
    print("| Format | Clips/Video | Bilder/Video | Videos @2Min | @3Min | @5Min | "
          "Kredit-Gegenwert je Video |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for name, f in FORMATE.items():
        ki_sek = f["dauer"] * f["deckung"]
        n_clips = ki_sek / SHOT_SEK
        if f["deckung"] == 0:                    # reiner Standbild-Weg
            n_bilder = f["dauer"] / STILL_SEK
            wert = n_bilder * BILD_CR_2K
            zeile = [f"{bilder/n_bilder:,.0f}" for _ in GEN_MIN]  # bildgebunden
        else:
            n_bilder = n_clips
            wert = ki_sek * CR_S_720 + n_bilder * 2
            zeile = [f"{clips[g]/n_clips:,.0f}" for g in GEN_MIN]
        print(f"| {name} | {n_clips:,.0f} | {n_bilder:,.0f} | "
              + " | ".join(zeile)
              + f" | {wert:,.0f} Cr = **{wert*CR_EUR:,.0f} EUR** |")

    print(f"\n> Kredit-Gegenwert = was dasselbe Material bei 720p/fast "
          f"({CR_S_720} Cr/s) bzw. Nano Banana Pro 2k ({BILD_CR_2K:.0f} Cr) "
          f"regulaer kosten wuerde. Kurs {CR_EUR:.4f} EUR/Cr.")
    print("> Der Standbild-Weg ist BILD-gebunden, nicht video-gebunden - "
          "deshalb dort dieselbe Zahl in allen drei Spalten.")


if __name__ == "__main__":
    main()
