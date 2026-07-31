# -*- coding: utf-8 -*-
"""6-Monats-Ertragsmodell fuer einen neuen Kanal.

WARUM DAS NOETIG IST: Das Arithmetik-Gate in NISCHEN-SYSTEM.md rechnet den
EINGESCHWUNGENEN Zustand ("Nischen-Benchmark erreicht"). Den erreicht ein neuer
Kanal nach 18-36 Monaten, nicht nach 6. Wer die Gate-Zahl als 6-Monats-Prognose
liest, ueberschaetzt um eine Groessenordnung.

ANKER SIND ECHTE DEUTSCHE DOKU-KANAELE aus den eigenen Scans (analyse/nischen/),
nicht Annahmen:
    @EliasRichtersDokus   3,4 Mon   2.820 Abos   Median  3.936
    @DieDunkleAktee       5,5 Mon   2.390 Abos   Median 15.787
    @Erdarchiv           10,8 Mon  16.500 Abos   Median 72.916   <- Ausbrecher
    @WeltderFabeln       13,8 Mon   2.830 Abos   Median  1.723
    @Evolution-X         14,2 Mon   3.740 Abos   Median  2.423
    @f3rlas              36,7 Mon   7.510 Abos   Median 13.799
    @LostReichIndustries 92,6 Mon   1.300 Abos   Median    451

Lesart: Die MEISTEN deutschen Doku-Kanaele bleiben auch nach 12+ Monaten im
niedrigen vierstelligen Median. Einer von sieben bricht aus. Das Modell rechnet
deshalb in Szenarien mit Wahrscheinlichkeiten, nicht mit einem Punktwert.

Aufruf:  python3 ramp_modell.py [--uploads 8] [--rpm 2.0] [--kosten 38] [--monate 6]
"""
import argparse

# Views des DURCHSCHNITTLICHEN Videos im ersten Monat nach Upload,
# beim Kanalalter t (Monate). Aus den Ankern oben interpoliert.
SZENARIEN = {
    "Fehlschlag":  {"p": 0.35, "v6":    400, "v12":   1_000, "v24":   2_000},
    "Unteres Q.":  {"p": 0.30, "v6":  1_500, "v12":   3_000, "v24":   6_000},
    "Median":      {"p": 0.20, "v6":  4_000, "v12":  10_000, "v24":  20_000},
    "Guter Lauf":  {"p": 0.11, "v6": 14_000, "v12":  35_000, "v24":  60_000},
    "Ausbrecher":  {"p": 0.04, "v6": 35_000, "v12":  75_000, "v24": 140_000},
}
KATALOG_TAIL = 0.5   # Backkatalog liefert zusaetzlich ~50 % der Neu-Video-Views
SUBS_PRO_1000 = 2.0  # eigener Playbook-Wert (SPACE-PLAYBOOK §14)
MIN_WATCHZEIT = 4.0  # Minuten durchschnittliche Wiedergabedauer (konservativ)


def monat(v_neu, uploads, rpm, monat_nr, kosten):
    """Ein Monat: Views, YPP-Status, Netto."""
    views = uploads * v_neu * (1 + KATALOG_TAIL)
    watch_h = views * MIN_WATCHZEIT / 60
    subs_kum = views * monat_nr / 2 * SUBS_PRO_1000 / 1000   # grob kumuliert
    ypp = subs_kum >= 1000 and watch_h * 12 >= 4000
    brutto = views * rpm / 1000 if ypp else 0.0
    return {"views": round(views), "watch_h": round(watch_h),
            "subs_kum": round(subs_kum), "ypp": ypp,
            "brutto": round(brutto, 2), "netto": round(brutto - uploads * kosten, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--uploads", type=float, default=8)
    ap.add_argument("--rpm", type=float, default=2.0)
    ap.add_argument("--kosten", type=float, default=38)
    ap.add_argument("--monate", type=int, default=6)
    a = ap.parse_args()
    key = {6: "v6", 12: "v12", 24: "v24"}.get(a.monate, "v6")

    print(f"# Ertragsmodell Monat {a.monate}")
    print(f"\n{a.uploads:.0f} Folgen/Monat · RPM ${a.rpm} · {a.kosten:.0f} $/Folge "
          f"= {a.uploads*a.kosten:.0f} $ Kosten/Monat\n")
    print("| Szenario | P | Views/Mon | Watch-Std | Abos kum. | YPP? | Brutto | Netto |")
    print("|---|---:|---:|---:|---:|:--:|---:|---:|")
    ew_b = ew_n = 0.0
    for name, s in SZENARIEN.items():
        r = monat(s[key], a.uploads, a.rpm, a.monate, a.kosten)
        ew_b += s["p"] * r["brutto"]
        ew_n += s["p"] * r["netto"]
        print(f"| {name} | {s['p']:.0%} | {r['views']:,} | {r['watch_h']:,} | "
              f"{r['subs_kum']:,} | {'✅' if r['ypp'] else '❌'} | "
              f"{r['brutto']:,.0f} $ | {r['netto']:,.0f} $ |")
    print(f"\n**Erwartungswert: {ew_b:,.0f} $ brutto · {ew_n:,.0f} $ netto pro Monat**")
    p_null = sum(s["p"] for name, s in SZENARIEN.items()
                 if not monat(s[key], a.uploads, a.rpm, a.monate, a.kosten)["ypp"])
    print(f"**Wahrscheinlichkeit, dass die Einnahmen 0 $ sind (YPP nicht erreicht): {p_null:.0%}**")


if __name__ == "__main__":
    main()
