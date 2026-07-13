# Budget-Ledger — Folge 1 v4 Produktion

**Deckel:** ≤ €50 Higgsfield (Worst-Case €0,043/Cr → harte Grenze ~1.150 Credits). ElevenLabs ≤ €5.
**Start-Guthaben:** 1.813 Credits (13.07.2026).
**Stopp-Regel:** keine neuen Video-Jobs, wenn Guthaben ≤ 660 (= 1.150 verbraucht).

## Stückkosten (get_cost verifiziert)
- Seedance 1080p/std/5s = **45 Cr**  ← gewählt (beste Qualität)
- Seedance 720p/fast/5s = 17,5 Cr
- Nano Banana Pro 2k = 4 Cr · 1k = 2 Cr

## Qualitäts-Entscheidung
Neue Shots nativ **1080p/std**, 2k-Bild als start_image. 18 Folge-1-Clips (720p) werden
wiederverwendet (kostenlos, via Job-IDs) und im Master auf 1080p normalisiert.

## Ledger
| Zeit | Aktion | Cr | Guthaben |
|---|---|---|---|
| start | — | — | 1813 |
| 18:15 | 15 Bilder (nano_banana_2, 2 Cr) | -30 | 1783 |
| 18:20 | NV01-04 Videos 1080p/std (45 Cr) | -180 | 1603 |
| 18:25 | NV02,03,05,06,07,08,09,11 Videos 4K/high (110 Cr) | -880 | ~753 |
| | (NV02/NV03 1080p-Dubletten verworfen, ~90 Cr Verlust) | | |
| **IST 18:28** | **balance-check** | | **753** |

## Rest-Plan (Budget-diszipliniert)
- Noch 4K feuern: NV10 (GBT Nacht), NV13 (Komet-Bahn), NV14 (Würfel), NV15 (Headlines) = 4×110 = 440 Cr
- NV12 (Earth-noise) GESTRICHEN (ersetzbar via reused C17/andere)
- Endstand-Prognose: ~1.500 Cr Higgsfield ≈ €45 (annual) / €65 (monthly)
