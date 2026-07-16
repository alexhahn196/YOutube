# Budget-Ledger — Folge 4 (Wow!-Signal)

**Deckel (User-Vorgabe):** max. 50 € ≈ 1.052 Cr (Kurs 2.000 Cr = 95 € → 1 Cr ≈ 0,0475 €)

| Posten | Credits |
|---|---|
| Start-Balance (vor F4) | 967,5 |
| End-Balance (nach allen Generierungen) | 332,5 |
| **Verbrauch F4 gesamt (inkl. F3-Thumb-Plate)** | **635 Cr ≈ 30,16 €** |

## Aufschlüsselung
- **Bilder (13 Generierungen, 0 Re-Rolls!):** 1× 2k Hero NY01 @4 + 11× 1k @2 = 26 Cr, plus F3-Thumbnail-Plate 2k @4 = **30 Cr**
- **Videos (12 Generierungen):** 1× 4k Hero NY01 @110 + 11× 1080p std @45 = **605 Cr** (zwei 429-Rate-Limit-Fehlversuche = 0 Cr)
- Musik: Reuse F1/F2-Beds = **0 Cr** · TTS: ElevenLabs (12.512 + 1.728 Zeichen Re-TTS seg03) · Schnitt/4K-Render: lokal ffmpeg = **0 Cr**
- **Reuse-Quote:** 13 von 25 Clips aus dem F1–F3-Pool (52 %) — der Wow!-Stoff passte perfekt auf vorhandene Radioteleskop-/Forensik-Shots.

## Lessons
1. **„No text"-Suffix konsequent von Anfang an** → diesmal 0 Bild-Re-Rolls (F3: 5).
2. **Regieanweisungen im VO-Skript müssen `[BEAT]`-Format haben** — „[BEAT — 3 sec, …]" rutschte durch den TTS-Filter und wurde mitgesprochen → seg03 musste neu vertont werden (nur ElevenLabs-Zeichen, 0 Cr). Filter-Regex in allen Skripten auf `^\[BEAT\b[^\]]*\]$` erweitert.
3. Rate-Limit ~8 parallele seedance-Jobs bestätigt — Batch 2 einfach nach Queue-Drain neu feuern.

**Fazit: 30,16 € von 50 € — 40 % unter Deckel.** Verbleibende Balance 332,5 Cr (reicht für F5-Thumb-Plates + einzelne Shots; für F5-Vollproduktion (~600 Cr) wird ein Credit-Nachkauf nötig).
