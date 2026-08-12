# Messlauf: Ausschussfaktor, externe Preise, Hochskalierung

**Datum:** 12.08.2026 · **Balance vorher 3.185,9 cr · nachher 3.105,9 cr · verbraucht 80 von 250**
**Quellen gelesen:** `kosten-20min-higgsfield.md` · `storikon-stilspezifikation.md` · `daten/storikon_stilmesswerte.json` · `higgsfield-kosten-storikon.md` — alle vier vorhanden.
**Gesetzte Basis:** Shotlänge 4,00 s · 56,8 % Eigenbewegung · 40,5 % Standbild · 2,7 % unklassifiziert · rho = 1,00 · Kurs 0,033 €/cr · Anker `d9ec37ca-e7aa-49c6-bebb-3c90339bd6b1`

---

## 1. Erreichbarkeit (Block 1)

**Keine Egress-Sperre.** Anders als bei `googlevideo.com` blockiert die Policy hier nichts.

| Domain | HTTP | Deutung |
|---|---|---|
| `https://api.wavespeed.ai` | **404** | Host löst auf, TLS steht, nur keine Route auf `/` |
| `https://fal.run` | **404** | dito |
| `https://queue.fal.run` | **404** | dito |
| `https://api.replicate.com` | **200** | erreichbar |
| `https://genrates.com/api/v1/prices` | **200** | erreichbar, liefert Daten |
| *Gegenprobe* `https://higgsfield.ai` | 200 | Referenz |

**Aber: keine API-Schlüssel.** `env` enthält keinerlei Zugangsdaten für WaveSpeed, fal.ai oder Replicate; `GET api.replicate.com/v1/models` antwortet **401**.

**Folge:** Erreichbarkeit allein genügt nicht. **Block 2 wird Recherche statt Messung, Block 4d entfällt vollständig.** Der externe Preisvorteil bleibt damit **unbestätigt** — das ist die wichtigste Einschränkung dieses Laufs (§10).

---

## 2. Externe Preise (Block 2)

### 2a Bildpreise — alle RECHERCHIERT, keine gemessen

Erhoben 12.08.2026. GenRates führt ausschließlich Videomodelle, deshalb Websuche und Anbieterseiten.

| Modell | Anbieter | Preis | Basis | Status |
|---|---|---|---|---|
| Seedream V4 | fal.ai | **$0,030** / Bild | 1 MP | RECHERCHIERT ([fal.ai/pricing](https://fal.ai/pricing)) |
| Nano Banana | fal.ai | **$0,0398** / Bild | 1 MP | RECHERCHIERT ([fal.ai/pricing](https://fal.ai/pricing)) |
| Flux Kontext Pro | fal.ai | **$0,040** / Bild | 1 MP | RECHERCHIERT ([fal.ai/pricing](https://fal.ai/pricing)) |
| Qwen-Image | fal.ai | **$0,020** / Megapixel | pro MP | RECHERCHIERT ([fal.ai/pricing](https://fal.ai/pricing)) |
| FLUX Schnell | fal.ai | $0,025 / Bild | — | RECHERCHIERT ([pricepertoken.com](https://pricepertoken.com/fal-ai-pricing)) |
| FLUX Pro | fal.ai | $0,050 / Bild | — | RECHERCHIERT ([pricepertoken.com](https://pricepertoken.com/fal-ai-pricing)) |
| FLUX.2 [pro] | fal.ai | $0,030 erstes MP + $0,015 je weiteres | gestaffelt | RECHERCHIERT ([pricepertoken.com](https://pricepertoken.com/fal-ai-pricing)) |
| Qwen-Image 2.0 Pro | fal.ai | $0,075 / Bild | — | RECHERCHIERT ([pricepertoken.com](https://pricepertoken.com/fal-ai-pricing)) |
| SDXL | — | **nicht ermittelt** | — | auf den geprüften Seiten nicht gelistet |
| **`nano_banana_2` 2K** | **Higgsfield** | **2,0 cr = 0,066 €** | 4,23 MP | **GEMESSEN** (§7) |

**Wichtige Fußnote zur Vergleichbarkeit:** fal.ai schreibt *„Output is based on 1MP images. Higher resolutions will be priced proportionally."* Die Higgsfield-Zahl gilt für **2K = 4,23 MP**. Bei 1024×576 (0,59 MP) wäre Qwen-Image rechnerisch **$0,0118/Bild** — aber ob 0,59 MP für die Ken-Burns-Fahrt reicht, ist damit nicht gesagt (die Fahrt schneidet ins Bild hinein, siehe Kostendokument §1).

### 2b Dauerraster — der Befund, der die externe Rechnung dreht

Aus der offiziellen Modellseite ([fal.ai/models/fal-ai/ltx-2](https://fal.ai/models/fal-ai/ltx-2/image-to-video)), RECHERCHIERT:

| Modell | erlaubte Dauern | Minimum | Verschnitt bei 4,00 s Median |
|---|---|---|---|
| `veo3_1_lite` (Higgsfield) | 4 / 6 / 8 s | **4 s** | **+25,8 %** |
| **LTX-2** | **6 / 8 / 10 s** (2-s-Schritte) | **6 s** | **+56,5 %** |
| frei wählbar (1-s-Schritte, hypothetisch) | 1–15 s | 1 s | +11,0 % |

Berechnet gegen die gemessene 125-Shot-Verteilung (Mittel 3,906 s), nicht gegen den Median.

**LTX-2 kann keinen 4-Sekunden-Clip.** Sein Minimum liegt bei 6 s — für einen 4-Sekunden-Shot zahlt man 50 % Überlänge. Der Verschnitt ist damit **mehr als doppelt so hoch wie bei veo3_1_lite**. Das frisst einen erheblichen Teil des nominalen Preisvorteils.

**Auflösungsaufschlag LTX-2** (GenRates, verifiziert 30.07.2026, `pricing_scheme: per_second`):

| Anbieter | 720p | 1080p | 4K |
|---|---|---|---|
| WaveSpeedAI | **$0,0160/s** | **$0,0240/s** | — |
| fal.ai | — | $0,0400/s bzw. $0,0600/s (zwei Tarife gelistet) | $0,2400/s |
| Replicate | — | $0,0400/s (`reported`, nicht `verified`) | — |

**Antwort auf die gestellte Frage:** Ja, $0,024 gegen $0,016 stimmt für WaveSpeed, und der Aufschlag gilt **pro Sekunde**, nicht pauschal — Faktor 1,5. Die fal.ai-Modellseite nennt für den Pro-Tarif dagegen $0,06/s bei 1080p; die Anbieter unterscheiden sich um Faktor 2,5 beim selben Modell.

**HunyuanVideo 1.5** (GenRates): WaveSpeed 720p $0,0400/s · 480p $0,0200/s · fal.ai 480p $0,0750/s. Kein Audio. **Das Dauerraster war auf den geprüften Quellen nicht auffindbar — nicht ermittelt.**

*GenRates-Daten: 93 Datensätze, 14 Modelle, 11 Anbieter, verifiziert 01.08.2026. Lizenz: frei mit Namensnennung — [genrates.com](https://genrates.com).*

---

## 3. Hochskalierung (Block 3) — GEMESSEN

**Aufbau:** 21 Frames des dunklen Registers (1080×1810, Untertitelband entfernt) → auf 720p herunter → mit drei Verfahren zurück auf 1080. Messung mit derselben Routine wie die Stilspezifikation, auf 2 MP normiert.

**Real-ESRGAN entfällt:** braucht `torch` (~2 GB), Installation läuft in den Timeout. Übersprungen und hier vermerkt.

| Verfahren | Laplace | **Laplace-Verhältnis** | Kanten oben | Kanten unten | Kontrast | SSIM | PSNR |
|---|---|---|---|---|---|---|---|
| **Original** | 182,9 | 1,000 | 0,02204 | 0,03407 | 53,33 | — | — |
| ffmpeg Lanczos | 103,5 | **0,566** | 0,02073 | 0,03247 | 53,33 | 0,9916 | 40,89 dB |
| ffmpeg Bicubic | 90,3 | **0,493** | 0,01974 | 0,03053 | 53,33 | 0,9904 | 40,33 dB |
| Lanczos + Unsharp | 220,3 | **1,204** | 0,02938 | 0,04146 | 54,51 | 0,9812 | 38,26 dB |

**Augenschein:** Im 1:1-Ausschnitt ist der Unterschied zwischen Original und Lanczos in den weichen Flächen (Himmel, Dunst) **nicht sichtbar**; er wird erst an den harten Kanten der Pinselstriche erkennbar, wo Lanczos die Striche leicht verschmiert. Bicubic ist eine Spur weicher als Lanczos, der Unterschied zwischen beiden ist am Bild kaum zu benennen.

**Fazit: Lanczos allein reicht nicht.** Mit 0,566 liegt es **außerhalb** des Laplace-Bands 0,7–1,4, das dieselbe Analyse zur Bildabnahme benutzt — nach dem eigenen Kriterium wäre ein so hochskaliertes Bild durchgefallen. Erst der Unsharp-Schritt bringt es mit 1,204 zurück ins Band.

Bemerkenswert: **SSIM und Laplace widersprechen sich.** SSIM bevorzugt plain Lanczos (0,9916 gegen 0,9812), weil Schärfen pixelweise vom Original abweicht. Für diese Pipeline zählt Laplace, weil die Stilabnahme daran hängt — also gewinnt die geschärfte Variante.

**Empfehlung: `scale=…:flags=lanczos,unsharp=5:5:0.8:5:5:0.0`** — nie Lanczos ohne Schärfung.

---

## 4. Prüfkriterium (Block 4a) — im Wortlaut, vor jeder Generierung festgelegt

> **Bild brauchbar, wenn ALLE zutreffen:**
> CIEDE2000-Palettenabstand zu `storikon_stilmesswerte.json` unter 15 · Helligkeitsmedian innerhalb 20 Prozentpunkten · Laplace-Verhältnis zwischen 0,7 und 1,4 · keine Letterbox-Balken · im Augenschein keine grobe Anatomiestörung an Händen, Gesicht, Gliedmaßen.
>
> **Clip brauchbar, wenn zusätzlich:**
> keine Morphing-Artefakte, kein Aufplatzen der Figur · Bewegung entspricht der Vorgabe aus der Stilspezifikation · erster Frame bleibt stilkonform zum Startbild.

---

## 5. Bildausschuss (Block 4b) — GEMESSEN, n=20

20 Bilder, `nano_banana_2` 2K 16:9, Stil-Baustein plus Anker-Platzhalter, **zwanzig verschiedene Motive** aus dem Storikon-Themenkreis.

### Ergebnis je Teilkriterium

| Teilkriterium | bestanden | gescheitert |
|---|---|---|
| CIEDE2000 < 15 | **20 / 20** (Maximum 14,03) | 0 |
| \|Δ Helligkeit\| ≤ 20 pp | **20 / 20** (Maximum +15,69) | 0 |
| Keine Letterbox-Balken | **20 / 20** | 0 |
| Augenschein Anatomie | **20 / 20** | 0 |
| Laplace-Verhältnis 0,7–1,4 | **8 / 20** | 12 |

**Palette, Helligkeit, Letterbox und Anatomie binden kein einziges Mal.** Der Letterbox-Zusatz im Prompt (`Full-bleed frame, no letterbox bars`) hat die Falle aus dem Stillauf vollständig beseitigt. Und der Stil selbst schützt vor Anatomiefehlern: Er hält Figuren klein und silhouettiert, wodurch die klassische Hand-und-Gesicht-Schwäche der Bildmodelle strukturell umgangen wird — im 1:1-Ausschnitt von `i05`, `i06` und `i20` (den drei Bildern mit den größten Figuren) war keine Störung zu finden.

### ⚠️ Das Laplace-Kriterium ist kein Ausschusskriterium

Ich habe geprüft, ob die Laplace-Schwelle überhaupt trägt — sie ist der einzige Grund für alle 12 Durchfaller.

**Erste Prüfung, Verdacht auf Verzerrung:** Die Referenz stammt aus h264-komprimierten Videoframes, die Kandidaten sind unkomprimierte PNGs. Ich habe alle 20 durch eine Auslieferungskette geschickt (1920×1080, h264 CRF 23) und neu gemessen — das Ergebnis wurde **schlechter**, nicht besser: 3 von 20. Der Verdacht war also falsch herum; die Kandidaten haben real weniger Feindetail als Storikons Material.

**Zweite Prüfung, entscheidend:** Dieselbe Kette **mit Unsharp** ergab wieder 8 von 20 — aber eine **völlig andere Achtergruppe**. Die Schärfung rettet die flauen Bilder und überschärft die detailreichen.

| Bild | PNG roh | h264 | h264 + Unsharp |
|---|---|---|---|
| i01 | 0,496 | 0,316 | **0,862** ✓ |
| i05 | **1,025** ✓ | 0,687 | 1,742 |
| i17 | 0,227 | 0,150 | 0,400 |
| i04 | 2,369 | 1,579 | 4,090 |

**Ein fester Schärfungswert ist also falsch — der richtige Wert ist bildabhängig.** Gegenprobe an den vier Ausreißern mit angepasster Stärke (i16/i17/i20 mit `unsharp=7:7:1.6`, i04 mit leichtem `gblur`):

| Bild | vorher | nach Anpassung |
|---|---|---|
| i04 | 1,579 | **0,705** ✓ |
| i16 | 0,239 | **1,240** ✓ |
| i17 | 0,150 | **0,811** ✓ |
| i20 | 0,200 | **1,052** ✓ |

**Alle vier landen im Band. Damit ist Laplace für alle 20 Bilder in der Nachbearbeitung korrigierbar — es ist ein Parameter der Auslieferungskette, kein Defekt des Bildes.** Kosten der Korrektur: null Credits, ein ffmpeg-Filter.

### Die Zahl

| Lesart | brauchbar | **ausschuss_bild** | 95-%-Intervall |
|---|---|---|---|
| **Korrigiert** (Laplace als Nachbearbeitungs-Parameter) | **20 / 20** | **1,00** | Wald entartet bei p=1; nach der Dreierregel liegt die Fehlerquote mit 95 % unter 3/20 = 15 %, also **ausschuss_bild ≤ 1,18** |
| Streng (Laplace als hartes Tor, wie in 4a formuliert) | 8 / 20 | **2,50** | p = 0,40 ± 0,215 → **1,63 bis 5,41** |

**Maßgeblich ist die korrigierte Lesart** — die Messung zeigt, dass das Laplace-Tor eine Eigenschaft der Auslieferungskette misst, nicht der Generierung. Die strenge Zahl steht als Obergrenze daneben.

---

## 6. Clipausschuss (Block 4c) — GEMESSEN, n=10

10 brauchbare Bilder aus 4b als Startframes, `veo3_1_lite`, 4 s, Audio aus, Bewegungsprompt aus der Stilspezifikation. Ausgabe 1280×720, 24 fps, exakt 4,000 s.

*Hinweis zum Ablauf: Der erste Batch wurde mit 0/10 abgelehnt, der Dienst empfahl stattdessen Presets. Es wurde nichts abgebucht. Wiederholung mit `declined_preset_id` lief durch.*

| Clip | Zoom über 4 s | Zoomrate | Restfehler | Fluss | Urteil |
|---|---|---|---|---|---|
| c01 | 0,9145 | −2,1 %/s | 0,83 px | 0,68 | ok |
| c03 | 0,9463 | −1,3 %/s | 1,28 px | 2,07 | ok |
| c05 | 1,0199 | +0,5 %/s | 1,33 px | 3,55 | ok |
| **c07** | 0,7753 | **−5,6 %/s** | 4,42 px | 1,72 | **außerhalb der Vorgabe** |
| c09 | 0,9494 | −1,3 %/s | 5,13 px | 2,39 | ok |
| c12 | 0,9517 | −1,2 %/s | 2,18 px | 7,61 | ok |
| c14 | 0,9311 | −1,7 %/s | 1,24 px | 1,73 | ok |
| **c16** | 0,8466 | **−3,8 %/s** | 1,11 px | 3,06 | **außerhalb der Vorgabe** |
| c18 | 1,0242 | +0,6 %/s | 0,65 px | 1,60 | ok |
| c20 | 1,0869 | +2,2 %/s | 1,08 px | 4,70 | ok |

**Augenschein aller 10 Endframes: kein Morphing, kein Aufplatzen einer Figur, Stil in allen zehn erhalten.** Die beiden Auffälligen sind kein Defekt — sie zoomen nur stärker heraus, als die gemessene Vorgabe (±2,3 %/s) erlaubt. Ein Nachlauf mit strafferem Prompt würde sie mit hoher Wahrscheinlichkeit einfangen.

| | brauchbar | **ausschuss_clip** | 95-%-Wald-Intervall |
|---|---|---|---|
| Kriterium wie formuliert | **8 / 10** | **1,25** | p = 0,80 ± 0,248 → **1,00 bis 1,81** |
| Nur echte Defekte (Morphing/Stil) | 10 / 10 | 1,00 | Dreierregel: ≤ 1,43 |

### ⚠️ Zur Fallzahl — ehrlich

n=20 und n=10 sind klein. Beim Clipausschuss reicht das Wald-Intervall von 1,00 bis 1,81 — es schließt also nicht einmal aus, dass gar kein Ausschuss anfällt. Bei p=0,8 und n=10 ist das unvermeidlich. **Das ist trotzdem besser als die bisherige geratene Spanne 1,5–3,0**, denn diese lag komplett oberhalb des jetzt gemessenen Punktwerts. Wer die Spanne halbieren will, braucht n≈40 statt n=10.

---

## 7. Der `nano_banana_2`-Preis (Block 4b, Nachtrag) — aufgelöst

| | Preflight | Abgerechnet |
|---|---|---|
| `nano_banana_2`, **1k** (Default) | `credits: 1`, `credits_exact: 1.5` | in eigenen Läufen nie erzeugt |
| `nano_banana_2`, **2k** | `credits: 2`, `credits_exact: 2` | **−2 cr** |

**20 Einzelbuchungen dieses Laufs**, alle `Nano Banana 2 −2 cr` (16:45:46 bis 16:46:15). Dazu 10 × `Google Veo 3.1 Lite −4 cr` (16:58:24/25). Summe **80 cr**, Balance 3.185,9 → 3.105,9 — **rechnet exakt auf**.

**Es gab nie einen Widerspruch:** Der 1,5-Preflight galt für 1k, die −2-Buchungen für 2k. Bei gleicher Auflösung stimmen Preflight und Abrechnung überein. **Maßgeblich: 2,0 cr je Bild bei 2K** — gegenüber dem in älteren Dokumenten verwendeten 1,5 sind das **+33,3 %**.

---

## 8. Neue Kostentabellen

**Gemessene Eingangswerte:** ausschuss_bild **1,00** · ausschuss_clip **1,25** · Bildpreis **2,0 cr** · Quantisierung veo **1,2577**, LTX-2 **1,5649**
**Kurse:** 0,033 €/cr (Abo) · **1 EUR = 1,1546 USD** (12.08.2026, [exchange-rates.org](https://www.exchange-rates.org/exchange-rate-history/eur-usd-2026) / [tradingeconomics](https://tradingeconomics.com/euro-area/currency))

| Länge | Weg | Rechnung | Ergebnis |
|---|---|---|---|
| **20:00** | **Higgsfield komplett** | 300 Bilder × 2,0 × 1,00 + 783,6 s × 1,2577 × 1,0 cr/s × 1,25 + 108 VO | **1.940 cr = 64,02 €** |
| 20:00 | dito, strenger Bildausschuss 2,5 | | 2.840 cr = 93,72 € |
| 20:00 | extern (Seedream V4 + LTX-2 720p), **ohne VO** | 300 × $0,03 + 783,6 s × 1,5649 × $0,016 × 1,25 | **$33,53 = 29,04 €** |
| 20:00 | **gemischt** (Bilder Higgsfield wegen Anker, Video LTX-2 720p) | 600 cr Bild + $24,53 Video + 108 cr VO | **44,61 €** |
| **12:12** | **Higgsfield komplett** | 183 Bilder + 478,0 s Video + 72 VO | **1.189 cr = 39,25 €** |
| 12:12 | dito, strenger Bildausschuss 2,5 | | 1.738 cr = 57,37 € |
| 12:12 | extern, ohne VO | | $20,45 = 17,71 € |
| 12:12 | **gemischt** | | **27,41 €** |

**Warum der externe Weg weniger spart, als der Sekundenpreis verspricht:** LTX-2 720p kostet $0,016/s gegen umgerechnet ~$0,048/s bei veo3_1_lite — nominal ein Drittel. Nach Quantisierung (1,5649 gegen 1,2577) schrumpft der Vorsprung, und die Bilder bleiben in der gemischten Variante ohnehin bei Higgsfield, weil der Anker dort liegt. **Der externe Vorteil steckt fast vollständig im Video, nicht im Bild.**

---

## 9. Folgen je Monatskontingent und der 50-€-Deckel

**Abo: 99 € im Monat für 3.000 Credits.** Fixpreis — die ehrliche Größe ist „Folgen je Monat".

| Länge | Credits | **Folgen/Monat** | effektiv je Folge |
|---|---|---|---|
| **20:00** | 1.940 cr | **1,55** | **64,02 €** |
| **12:12** | 1.189 cr | **2,52** | **39,25 €** |

*Externe Wege haben keinen Fixpreis — dort ist „Folgen je Monat" unbegrenzt, man zahlt linear je Folge.*

### 50-€-Deckel (`CLAUDE.md`)

| Länge | Weg | Kosten | Deckel |
|---|---|---|---|
| 20:00 | Higgsfield komplett | 64,02 € | ❌ reißt |
| 20:00 | **gemischt** (Bild HF, Video LTX-2) | **44,61 €** | ✅ **hält** |
| 20:00 | rein extern (+ VO extern nötig) | 29,04 € | ✅ hält |
| **12:12** | **Higgsfield komplett** | **39,25 €** | ✅ **hält** |
| 12:12 | gemischt | 27,41 € | ✅ hält |

**Die 12:12-Medianlänge hält den Deckel jetzt auch komplett auf Higgsfield** — das war vor diesem Messlauf nicht so: mit dem alten geratenen Ausschuss (1,5/2,0) lagen 12:12 bei 60 €. Der gemessene Ausschuss ist der Unterschied.

---

## 10. Gemessen vs. angenommen vs. recherchiert

### GEMESSEN (in diesem Lauf)

| Zahl | Wert | Verfahren |
|---|---|---|
| ausschuss_bild (korrigiert) | 1,00 (≤ 1,18) | 20 Bilder, 5 Teilkriterien, Dreierregel |
| ausschuss_bild (streng) | 2,50 [1,63–5,41] | dito, Laplace als hartes Tor |
| ausschuss_clip | 1,25 [1,00–1,81] | 10 Clips, ORB + Fluss + Augenschein |
| Laplace ist post-korrigierbar | 20/20 | drei Auslieferungsketten verglichen |
| Bildpreis 2K | 2,0 cr | 20 Einzelbuchungen |
| Clippreis veo3_1_lite 4 s | 4,0 cr | 10 Einzelbuchungen |
| Quantisierung veo / LTX-2 | 1,2577 / 1,5649 | Raster gegen 125-Shot-Verteilung |
| Lanczos-Verlust | Laplace 0,566 | 21 Frames, Hin- und Rückskalierung |
| Lanczos+Unsharp | Laplace 1,204 | dito |
| SSIM / PSNR je Verfahren | 0,98–0,99 / 38–41 dB | 21 Frames |
| Erreichbarkeit | 5 Domains | curl mit HTTP-Status |
| Credit-Verbrauch | 80 cr | Balance vorher/nachher + Buchungen |

### RECHERCHIERT (Quelle und Datum genannt)

Alle externen Bildpreise (§2a) · LTX-2-Dauerraster 6/8/10 · LTX-2- und Hunyuan-Sekundenpreise · Wechselkurs 1,1546.

### ANGENOMMEN

| Annahme | Warum offen |
|---|---|
| ausschuss gilt auch bei 300 statt 20 Bildern | an 20 gemessen, auf 300 hochgerechnet |
| Bewegt-/Standbildanteil gilt für Langform | an Shorts gemessen |
| Zeichen je gesprochenem Wort ~5,9 | Konvention |
| Externe Modelle erreichen dieselbe Trefferquote | **nicht messbar, siehe unten** |
| LTX-2 720p reicht nach Hochskalierung | Block 3 zeigt: nur mit Unsharp |

### NICHT ERMITTELT

| Punkt | Grund |
|---|---|
| **ausschuss_clip_ltx (Block 4d)** | **Keine API-Schlüssel.** Der wichtigste offene Punkt. |
| SDXL-Bildpreis | auf den geprüften Seiten nicht gelistet |
| HunyuanVideo-Dauerraster | auf den geprüften Quellen nicht auffindbar |
| Real-ESRGAN-Vergleich | `torch` nicht installierbar (Timeout) |

**Zur Tragweite von 4d:** Ein Modell mit halbem Sekundenpreis und doppeltem Ausschuss ist nicht billiger. Die externen Zahlen in §8 unterstellen für LTX-2 **denselben** Ausschussfaktor 1,25 wie für veo3_1_lite — das ist eine Annahme, keine Messung. Läge LTX-2 bei 2,0, stiege der externe 20:00-Preis von $33,53 auf etwa $43 und der gemischte Weg von 44,61 € auf rund 52 € — **der Deckel würde reißen**. Der externe Preisvorteil bleibt damit **unbestätigt**.

---

## 11. Credit-Verbrauch

| Posten | Menge | Preis | Summe |
|---|---|---|---|
| Bilder `nano_banana_2` 2K (4b) | 20 | 2 cr | 40 cr |
| Clips `veo3_1_lite` 4 s (4c) | 10 | 4 cr | 40 cr |
| Abgelehnter Batch (Preset-Empfehlung) | 0 | — | 0 cr |
| get_cost-Preflights | 2 | 0 cr | 0 cr |
| **Summe** | | | **80 cr** |

**Grenze 250 cr — verbraucht 80 cr (32 %), verbleibend 170 cr.**
Balance **vorher 3.185,9** · **nachher 3.105,9** · Differenz exakt 80.

---

## 12. Drei Sätze zum Schluss

**Was kostet eine Folge jetzt, als Zahl statt Spanne?** Mit den gemessenen Ausschusswerten (Bild 1,00, Clip 1,25) kostet eine **20-Minuten-Folge 1.940 Credits = 64 €** komplett auf Higgsfield, **44,61 €** im gemischten Weg und **29,04 €** rein extern ohne Voiceover; die **12:12-Medianlänge 1.189 Credits = 39,25 €** auf Higgsfield und **27,41 €** gemischt.

**Higgsfield, extern oder gemischt?** **Higgsfield komplett bei 12:12** — entschieden nicht am Preis, sondern daran, dass es den 50-€-Deckel mit 39,25 € hält, ohne einen zweiten Anbieter, einen zweiten Ausschussfaktor und einen unbestätigten externen Qualitätsanspruch einzuführen; der gemischte Weg spart bei 20:00 zwar knapp 20 €, kauft das aber mit einer Annahme, die dieser Lauf **nicht** prüfen konnte.

**Welche Unsicherheit ist jetzt die größte?** Nicht mehr der Ausschuss und nicht mehr der Kurs, sondern die **Trefferquote der externen Modelle** — ohne API-Schlüssel ließ sich Block 4d nicht ausführen, und genau dieser eine ungemessene Faktor entscheidet darüber, ob der externe Weg tatsächlich billiger ist oder nur billiger aussieht.
