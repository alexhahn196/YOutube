# Produktionskosten-Analyse — Budget ≤ 50 €/Video & Modell-Alternativen

Stand: 15.07.2026. Frage: Bleiben wir bei Higgsfield (nano_banana + seedance_2_0) oder wechseln wir auf
direkte APIs (chinesische Modelle: Seedance/ByteDance, Kling/Kuaishou, Hailuo/MiniMax, Wan/Alibaba)?
Randbedingung: Budget **max. 50 €/Video** bis zur Monetarisierung; Steuerbarkeit durch Claude muss
gleichwertig zu Higgsfield sein (API/skriptbar, kein Klick-Tool).

---

## 1. Wichtig zur Einordnung: Wir nutzen BEREITS ein chinesisches Modell
Unser Video-Generator **Seedance 2.0 ist ByteDance** (China) — Higgsfield ist nur der Händler/die
Bedienoberfläche davor. Das Bild-Modell nano_banana ist Google. Die Frage ist also nicht „chinesische
KI ja/nein", sondern: **direkt beim Händler kaufen (API) oder weiter über Higgsfield?**

## 2. Preisvergleich (verifiziert, Juli 2026)

| Weg | Modell | 1080p-Clip (~5 s) | Steuerbar durch Claude? |
|---|---|---|---|
| **Higgsfield (heute)** | seedance_2_0 std | 45 Cr ≈ **1,50–1,95 €** | ✅ nativ (MCP-Tools, heute im Einsatz) |
| Higgsfield 4K | seedance_2_0 4K | 110 Cr ≈ 3,65–4,75 € | ✅ |
| fal.ai API | Seedance 2.0 std | ~0,30 $/s → **~1,40 €**/5 s (Fast: ~0,24 $/s) | ✅ REST-API + Key (wie ElevenLabs via curl) |
| fal.ai API | Seedance 1.0 Pro i2v | ~0,74 $ ≈ 0,68 € | ✅ |
| fal.ai API | **Kling 3.0 Pro** | 0,168 $/s → **~0,78 €**/5 s (inkl. Audio) | ✅ |
| fal.ai API | **Hailuo 02 Std** | 0,045 $/s (768p) → **~0,25 €**/6 s | ✅ |
| Direkt-APIs China (Volcano/Kling/MiniMax) | dito | ähnlich fal | ⚠️ Registrierungs-/Zahlungs-Hürden, z. T. Verifikation — nicht empfohlen |

Quellen: fal.ai-Modellseiten (Seedance 1.0 Pro i2v; Seedance 2.0), BuildMVPfast API-Preisliste 07/2026,
Atlas-Cloud-Preisguides (Seedance 2.0 / Hailuo), Novoads Seedance-Pricing.

**Befund:** Seedance 2.0 über fal.ai kostet **fast dasselbe** wie über Higgsfield (~1,40 € vs. ~1,50 €).
Der echte Preisvorteil läge nur bei **anderen** Modellen: Kling 3.0 Pro (~½ Preis, mit Audio) und
Hailuo (~⅙ Preis, aber 768p = nur Füller-Qualität). Dazu kommt: das Higgsfield-Ultra-Abo läuft
bereits — Credits im Abo sind wirtschaftlich „schon bezahlt"; fal.ai wäre **zusätzliches** Geld.

## 3. Kostenmodell künftige Folge (13–15 Min, neue Regeln §12)

| Posten | Menge | Kosten |
|---|---|---|
| Neue Shots 1080p (seedance std) | ~10 × 45 Cr | 450 Cr |
| davon 2 Hero-Shots in 4K statt 1080p | +2 × 65 Cr Aufpreis | +130 Cr |
| Start-Bilder (nano_banana) | ~12 × 2–4 Cr | ~35 Cr |
| Preflights/Reserve | | ~85 Cr |
| **Higgsfield gesamt** | **~700 Cr** | **≈ 23–30 €** |
| ElevenLabs (VO + Musik, im Creator-Abo) | | ≈ 3–5 € |
| **Gesamt pro Folge** | | **≈ 26–35 €** ✅ |

Dazu wächst die **Wiederverwendungs-Bibliothek** jede Folge (Folge 1: 33 Clips archiviert, per Job-ID
abrufbar) → die Grenzkosten SINKEN pro Episode. Folge 1 war mit ~1.500 Cr (≈ 46–59 €) der teuerste
Fall (v4-Neubau + Voll-4K + Dubletten) — kein Maßstab für den Regelbetrieb.

**→ Das 50-€-Budget ist mit dem HEUTIGEN Setup sicher einhaltbar (Ziel: 35 €, Deckel: 50 €).**

## 4. Entscheidung

**BLEIBEN bei Higgsfield (nano_banana + seedance_2_0) — Konzept bestätigt.** Gründe:
1. Budget passt ohne Wechsel (≈ 26–35 €/Folge bei 1080p + selektivem 4K).
2. Seedance über fal.ai wäre **kaum billiger** — Wechsel brächte Integrationsaufwand + neuen API-Key
   + Neuaufbau von Budget-Tracking/Job-Archiv, ohne relevanten Gewinn.
3. Higgsfield-Abo läuft ohnehin (Credits verfallen sonst); native MCP-Steuerung ist erprobt
   (komplette Folge-1-Pipeline inkl. Ledger).
4. Qualität: seedance_2_0 ist aktuell Referenzklasse für unser Material; kein verifizierter Beleg,
   dass Kling/Hailuo bei Kosmos-Shots gleichziehen.

**Hybrid-Option (vorgemerkt, NICHT jetzt):** Wenn (a) Kadenz auf 2+/Woche steigt und Credits zum
Engpass werden, (b) das Abo gekündigt wird, oder (c) wir billige Füller-B-Rolls brauchen →
**fal.ai-Key anlegen** und Kling 3.0 Pro (~0,78 €/Clip) bzw. Hailuo (~0,25 €, 768p) für Nicht-Hero-
Shots zuschalten. Steuerbarkeit ist gegeben (REST wie ElevenLabs). Direkt-Verträge mit chinesischen
Plattformen (Volcano Engine etc.): verworfen — Anmelde-/Zahlungshürden ohne Preisvorteil ggü. fal.

**Budget-Regel (verbindlich):** Vor jeder Folge Shot-Plan mit Credit-Voranschlag (wie Folge 1),
Ziel ≤ 35 €, harter Deckel 50 €. 4K nur für 2–3 Hero-Shots; Rest 1080p; maximale Wiederverwendung.
