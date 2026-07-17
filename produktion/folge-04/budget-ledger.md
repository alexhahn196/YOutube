# Budget-Ledger — Folge 4 (Wow!-Signal)

**Deckel (User-Vorgabe):** max. 50 € ≈ 1.052 Cr (Kurs 2.000 Cr = 95 € → 1 Cr ≈ 0,0475 €)

| Posten | Credits |
|---|---|
| Start-Balance (vor F4) | 967,5 |
| End-Balance (nach allen Generierungen inkl. QC-Fix) | 286 |
| **Verbrauch F4 gesamt (inkl. F3-Thumb-Plate + NZ01-Fix)** | **681,5 Cr ≈ 32,37 €** |

## Aufschlüsselung
- **Bilder (14 Generierungen, 0 Re-Rolls!):** 1× 2k Hero NY01 @4 + 11× 1k @2 = 26 Cr, plus F3-Thumbnail-Plate 2k @4, plus NZ01-Fix-Bild 1k @~1,5 = **~31,5 Cr**
- **Videos (13 Generierungen):** 1× 4k Hero NY01 @110 + 11× 1080p std @45 + 1× NZ01-Fix 1080p @45 = **650 Cr** (zwei 429-Rate-Limit-Fehlversuche = 0 Cr)
- Musik: Reuse F1/F2-Beds = **0 Cr** · TTS: ElevenLabs (12.512 + 1.728 Zeichen Re-TTS seg03) · Schnitt/4K-Render/2× Re-Render: lokal ffmpeg = **0 Cr**
- **Reuse-Quote:** 12 von 25 Clips aus dem F1–F3-Pool (48 %) — der Wow!-Stoff passte perfekt auf vorhandene Radioteleskop-/Forensik-Shots.

## Lessons
1. **„No text"-Suffix konsequent von Anfang an** → diesmal 0 Bild-Re-Rolls (F3: 5).
2. **Regieanweisungen im VO-Skript müssen `[BEAT]`-Format haben** — „[BEAT — 3 sec, …]" rutschte durch den TTS-Filter und wurde mitgesprochen → seg03 musste neu vertont werden (nur ElevenLabs-Zeichen, 0 Cr). Filter-Regex in allen Skripten auf `^\[BEAT\b[^\]]*\]$` erweitert.
3. Rate-Limit ~8 parallele seedance-Jobs bestätigt — Batch 2 einfach nach Queue-Drain neu feuern.
4. **QC am fertigen Master ist Pflicht — Reuse-Clips auf eingebrannten Text scannen:** 3 alte Pool-Clips trugen Fake-/Slop-Text (NX09 „DATA STREAM CORRUPTED/BJERAM", NV05 „ERR 404", C20 „NASA JWST DEEP TIME RELIC"). Fix: NX09→sauberer NZ01-Neurender (+47 Cr), NV05→NY01-Hero, C20-Crop (0 Cr). **Konsequenz:** vor Wiederverwendung eines Pool-Clips immer Text-Scan.
5. **ENOSPC beim 4K-Render:** drei 2,6-GB-Dateien (silent/FINAL/MASTER) sprengen den Platz → Build-Kette löscht Slots nach assemble, Silent nach mix, FINAL nach composite. Alte hochgeladene Master lokal löschen (liegen auf CloudFront).

**Fazit: 32,37 € von 50 € — 35 % unter Deckel.** Verbleibende Balance 286 Cr (reicht für F5-Thumb-Plates + einzelne Shots; für F5-Vollproduktion (~600 Cr) wird ein Credit-Nachkauf nötig).
