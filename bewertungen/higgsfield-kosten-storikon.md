# Higgsfield-Kosten für 10 Minuten fertiges Video im Stil von „Сторикон"

**Kanal:** Сторикон (`UCR4Ech9MtQ1R-MidNIc9Y6g`, @storikon, 35.5K Abos, 9 Langform-Videos)
**Erhebungsdatum:** 12.08.2026
**Methode:** Alle Credit-Werte per `get_cost: true` abgefragt. **Kein einziger Job wurde abgesendet.**
**Währung:** Primär in **Credits**. Euro nur als abgeleitete Zweitspalte (§3) — der Kurs ist nicht eindeutig.

> ⚠️ **Die größte Unsicherheit in diesem Dokument ist der Ausschussfaktor.** Er ist **geraten, nicht gemessen** (§4.1). Er bestimmt die Endsumme stärker als jede Modellwahl innerhalb einer Preisklasse.

---

## 1. Shotprofil — nachgemessen

### 1.1 Das vorgegebene Profil hat sich nicht bestätigt

Vorgabe im Auftrag (n=1): *27 Einstellungen in 90 s, Ø 3,3 s.*
Nachmessung desselben Fensters ergab **30 Einstellungen, Ø 3,00 s** — die Ausgangszahl war bereits um 11 % daneben.

### 1.2 Messfenster (Tool: `NexLev:watch_youtube_video_and_ask`)

| # | Video | Fenster | Fallzahl (Fensterlänge) | Shots | Ø Shotlänge | bewegte KI-Clips | Titelkarten/Grafik | Standbilder |
|---|---|---|---|---|---|---|---|---|
| 0 | `VzgCw_pgut8` „Alexander the Great" | 01:00–02:30 | 90 s (Nachmessung der Vorgabe) | **30** | **3,00 s** | 27 (90,0 %) | 3 | 0 |
| 1 | `aTWyNHNLoYc` „East India Company" | 01:00–02:00 | 60 s | **16** | **3,75 s** | 15 (93,8 %) | 1 | 0 |
| 2 | `DNctig8Wr04` „Война за независимость США" | 02:00–03:00 | 60 s | **13** | **4,62 s** | 13 (100 %) | 0 | 0 |
| 3 | `CYnbskuk8pM` „Hitler's 10 Mistakes" | 05:00–06:00 | 60 s | **14** | **4,29 s** | 13 (92,9 %) | 1 | 0 |

**Gesamt-Fallzahl:** 4 Fenster, 270 s Videomaterial, 73 gezählte Shots, aus 4 verschiedenen Videos.

### 1.3 Median und Abweichung

| Größe | Wert |
|---|---|
| Median Shotlänge, 3 Pflicht-Fenster (1–3) | **4,29 s** |
| Abweichung zur Vorgabe 3,3 s | **+29,9 %** → über der 20-%-Schwelle |
| Median über alle 4 Fenster inkl. Nachmessung | 4,02 s |
| Median Anteil echt bewegter KI-Clips | **93,75 %** (Vorgabe war ~95 % — bestätigt) |
| Standbilder in allen 4 Fenstern | **0** — der Kanal animiert praktisch alles |

**→ Gerechnet wird laut Auftragsregel mit dem eigenen Median: `median_shotlaenge = 4,29 s`.**
Die Abweichung ist damit ausdrücklich dokumentiert. Das vorgegebene Fenster (3,00 s nachgemessen) ist der **schnittdichteste** der vier — es war nicht repräsentativ, sondern das Extrem. Rechnen mit 3,3 s hätte die Shotzahl und damit die Kosten um rund 30 % überschätzt.

### 1.4 Reale Videolänge des Kanals

Alle 9 Langform-Videos (`NexLev:youtube_channel_videos`), Länge in Sekunden:
472 (7:52) · 537 (8:57) · 605 (10:05) · 645 (10:45) · **732 (12:12)** · 787 (13:07) · 855 (14:15) · 1217 (20:17) · 1232 (20:32)

**Median = 732 s = 12:12** (Spannweite 7:52–20:32, deckt sich mit der Auftragsangabe).

### 1.5 Abgeleitete Mengengerüste

```
median_shotlaenge   = 4,29 s          (gemessen, §1.3)
shots_pro_10min     = 600 / 4,29      = 140 Shots
shots_pro_12:12     = 732 / 4,29      = 171 Shots
bilder              = shots            (1 Startframe je Shot)
clips               = shots
```

---

## 2. Preistabelle je Modell (Credits, per `get_cost`)

Alle Abfragen: `aspect_ratio: "16:9"`, `get_cost: true`, Audio aus wo der Parameter existiert.
Alle Parameter vorher mit `models_explore(action:'get')` auf Gültigkeit geprüft.

### 2.1 Videomodelle — kürzestmögliche Dauer (wie beauftragt)

| Modell | Abfrageparameter | Credits |
|---|---|---|
| `veo3_1_lite` | `duration 4`, `generate_audio false` | **4,0** |
| `kling3_0_turbo` | `duration 3`, `resolution 720p` | **4,5** |
| `kling3_0` | `duration 3`, `mode std`, `sound off` | **4,5** |
| `seedance1_5` | `duration 4`, `resolution 720p`, `generate_audio false` | **4,8** |
| `wan3_0` | `duration 3`, `resolution 720p`, `generate_audio false` | **7,5** |
| `happy_horse_video` | `duration 3`, `resolution 720p` | **7,5** |
| `seedance_2_0_mini` | `duration 4`, `resolution 720p`, `generate_audio false` | **10,0** |
| `seedance_2_0` | `duration 4`, `resolution 720p`, `mode fast`, `generate_audio false` | **14,0** |
| `seedance_2_0` | `duration 4`, `resolution 1080p`, `mode std`, `generate_audio false` | **36,0** |

*Hinweis zu `kling3_0_turbo`: Das Modell deklariert laut `models_explore` **keinen** Audio-Parameter — „Audio aus" ist dort nicht abfragbar und auch nicht nötig.*
*`seedance_2_0_mini` deklariert **keinen** `mode`-Parameter (nur `seedance_2_0` hat ihn). Die Mindestdauer beider Seedance-2.0-Varianten ist 4 s, nicht 3 s.*

### 2.2 ⚠️ Korrekturbedarf: kürzeste Dauer deckt den Medianshot nicht ab

Der gemessene Medianshot ist **4,29 s**. Ein 3-s- oder 4-s-Clip ist **kürzer als der Shot, den er füllen soll**. Wer mit den Preisen aus §2.1 rechnet, rechnet eine Untergrenze, die in der Produktion nicht herstellbar ist (man bräuchte Zeitlupe oder Standbild-Freeze am Clipende).

Deshalb zusätzlich abgefragt: **dauer-angepasste Preise**, jeweils die kürzeste vom Modell erlaubte Dauer **≥ 4,29 s**.

| Modell | Dauer-angepasste Abfrage | Credits | Credits/Sekunde |
|---|---|---|---|
| `veo3_1_lite` | `duration 6` (erlaubt: 4/6/8), `generate_audio false` | **6,0** | 1,0 |
| `kling3_0_turbo` | `duration 5`, `720p` | **7,5** | 1,5 |
| `kling3_0` | `duration 5`, `mode std`, `sound off` | **7,5** | 1,5 |
| `seedance1_5` | `duration 8` (erlaubt: 4/8/12), `720p`, Audio aus | **9,6** | 1,2 |
| `seedance_2_0_mini` | `duration 5`, `720p`, Audio aus | **12,5** | 2,5 |
| `wan3_0` | `duration 5`, `720p`, Audio aus | **12,5** | 2,5 |
| `happy_horse_video` | `duration 5`, `720p` | **12,5** | 2,5 |
| `seedance_2_0` | `duration 5`, `720p`, `mode fast`, Audio aus | **17,5** | 3,5 |
| `seedance_2_0` | `duration 5`, `1080p`, `mode std`, Audio aus | **45,0** | 9,0 |

Die Credits/Sekunde sind aus je zwei Messpunkten berechnet und über alle Modelle exakt linear — es gibt keinen Mengenrabatt bei längeren Clips.

**`seedance1_5` ist die Ausnahme:** mit 1,2 cr/s eigentlich zweitgünstigstes Modell, aber die erlaubten Dauern springen von 4 s direkt auf 8 s. Für einen 4,29-s-Shot zahlt man 8 s — 46 % der Clipzeit wird weggeschnitten. Effektiv 2,24 cr je genutzter Sekunde und damit teurer als Kling.

### 2.3 Bildmodelle (Startframes), 16:9

| Modell | Abfrageparameter | Credits |
|---|---|---|
| `seedream_v4_5` | `aspect_ratio 16:9`, `quality basic` (Default) | **1,0** |
| `seedream_v5_lite` | `aspect_ratio 16:9`, `quality basic` (Default) | **1,0** |
| `nano_banana_2` | `aspect_ratio 16:9`, `resolution 1k` (Default) | **1,0** gerundet / `credits_exact: 1.5` |
| `cinematic_studio_2_5` | `aspect_ratio 16:9`, `resolution 1k` (Default) | **2,0** |
| `nano_banana_flash` | — | **existiert nicht**, siehe §6 |

**⚠️ Widerspruch bei `nano_banana_2`:** `get_cost` liefert `{"credits": 1, "credits_exact": 1.5}`. Die tatsächliche Abrechnungshistorie (`transactions`) zeigt für „Nano Banana 2" jedoch durchgängig **−2 Credits** pro Bild (35 Buchungen zwischen 06.08. und 08.08.2026). Preflight und Ist-Abrechnung stimmen hier nicht überein. **In der Rechnung unten ist konservativ mit 1,5 gerechnet**; wenn real 2,0 abgerechnet wird, steigt Kombination B um ca. 10 %.

---

## 3. Credit-zu-Euro-Kurs

**Quelle:** `higgsfield:show_plans_and_credits(intent:'topup')`, abgerufen **12.08.2026**. Feld `topups[]`, `currency: "eur"`.

| Paket | Preis | Kurs | Credits je € |
|---|---|---|---|
| 500 Credits | 26,00 € | 0,0520 €/cr | 19,2 |
| 1.000 Credits | 49,00 € | 0,0490 €/cr | 20,4 |
| 2.000 Credits | 95,00 € | **0,0475 €/cr** | 21,1 |
| 4.000 Credits | 190,00 € | **0,0475 €/cr** | 21,1 |

**Verwendeter Kurs für alle €-Angaben in diesem Dokument: 0,0475 €/Credit** (Grenzkurs der beiden großen Pakete).

### ⚠️ Der Kurs ist nicht eindeutig — deshalb sind Credits die Leitwährung

Über den **Abo-Weg** ergibt sich ein völlig anderer Kurs: Der Plan ULTRA liefert 3.000 Credits/Monat, `annual_final_price_cents: 9900` (99 €). Ob sich das auf Jahr oder Monat bezieht, ist aus der Tool-Antwort **nicht eindeutig ableitbar** (`monthly_final_price_cents` steht auf `0`). Je nach Lesart ergäbe das 0,00275 €/cr (jährlich) oder 0,033 €/cr (monatlich) — Faktor 17 zwischen den Lesarten und bis zu Faktor 19 gegenüber dem Top-up-Kurs.

**Konsequenz:** Alle Kernaussagen dieses Dokuments stehen in Credits. Die €-Spalten gelten **ausschließlich für den Top-up-Weg** und sind als Obergrenze zu lesen. Wer die Abo-Credits verbraucht, zahlt effektiv deutlich weniger. Hinweis am Rand: Top-up-Credits verfallen nach 90 Tagen (`topup_expire_days: 90`).

### 3.1 Euro auf einen Blick — realistisches Szenario inkl. Voiceover

Zum Top-up-Kurs **0,0475 €/cr**. Anders als die €-Spalten in §4.3/§4.4 sind hier die Voiceover-Kosten aus §6.2 **enthalten** (60 cr bei 10:00, 72 cr bei 12:12).

| Kombination | 10:00 | 12:12 (Median) |
|---|---|---|
| **A Günstigst** | 1.950 cr = **93 €** | 2.380 cr = **113 €** |
| **B Kanal-realistisch** | 2.475 cr = **118 €** | 3.022 cr = **144 €** |
| **C Referenz/Konsistenz** | 5.170 cr = **246 €** | 6.314 cr = **300 €** |
| **D Premium 1080p** | 13.080 cr = **621 €** | 15.975 cr = **759 €** |

**Was dieselbe Produktion in den drei möglichen Kursen kostet** (Beispiel Kombination B):

| Kurs | Herkunft | B / 10:00 | B / 12:12 |
|---|---|---|---|
| 0,0475 €/cr | Top-up-Paket 2.000/4.000 — **belegt** | 118 € | 144 € |
| 0,033 €/cr | Abo ULTRA, falls 99 € je **Monat** — unklar | 82 € | 100 € |
| 0,00275 €/cr | Abo ULTRA, falls 99 € je **Jahr** — unklar | 7 € | 8 € |

**Praktische Lesart:** Die vorhandenen 3.219,9 Credits sind bereits bezahlt. Ein Durchlauf in Kombination B verursacht daraus **keine zusätzlichen Ausgaben** — er verbraucht rund zwei Drittel bis das gesamte Monatskontingent. Die 118–144 € fallen erst beim **Nachkauf** an.

### 3.2 Einordnung gegen das Projektbudget

Der Kostendeckel dieses Projekts liegt laut `CLAUDE.md` bei **50 €/Folge** (Ist-Stand 32–40 €). Eine Produktion im Storikon-Stil liegt beim Nachkauf-Kurs selbst in der günstigen realistischen Variante bei **118–144 €** — das **2,4- bis 2,9-Fache des Deckels**, ohne Score, Foley und Schnitt (§6).

Der Treiber ist nicht der Preis je Clip, sondern die **Menge**: Storikon animiert praktisch alles (0 Standbilder in 270 s Messmaterial, §1.2), also 140–171 generierte Clips je Folge. Das eigene Format zieht gemeinfreie NASA-/ESA-Footage bei und ersetzt damit einen Teil dieser Clips. **Der Kostenhebel liegt im Anteil generierter Shots, nicht in der Modellwahl** — zwischen den Kombinationen A und B liegen 26 €, zwischen 100 % und 50 % generierten Shots liegt die Hälfte der Summe.

---

## 4. Kostenmodell

### 4.1 Variablen — offen benannt

```
median_shotlaenge     = 4,29 s                      GEMESSEN (§1.3, n=4 Fenster)
shots_pro_10min       = 600 / 4,29 = 140            abgeleitet
shots_pro_medianlaenge= 732 / 4,29 = 171            abgeleitet
bilder                = shots
clips                 = shots
ausschussfaktor_bild  = [1,0 | 1,5 | 2,0]           ⚠️ GERATEN, NICHT GEMESSEN
ausschussfaktor_clip  = [1,5 | 2,0 | 3,0]           ⚠️ GERATEN, NICHT GEMESSEN
figuren_einmalkosten  = NICHT ERMITTELT (§6)        → in den Summen als 0 geführt

kosten = bilder * bildpreis * ausschussfaktor_bild
       + clips  * clippreis * ausschussfaktor_clip
       + figuren_einmalkosten
```

**Zum Ausschussfaktor:** Es gibt in diesem Dokument **keine Messung dazu** — weder aus dem Kanal noch aus eigener Produktion. Er ist reine Annahme. Zwischen optimistisch und pessimistisch liegt bei den Clips **Faktor 2,0** — das ist mehr Streuung, als zwischen den drei günstigsten Videomodellen liegt. Wer diese Zahl belastbar will, muss sie in der eigenen Produktion messen (Anzahl verworfener Generierungen je brauchbarem Clip) und hier ersetzen.

### 4.2 Die vier Modellkombinationen

| Kombi | Bildmodell | Videomodell (dauer-angepasst) | Warum diese Paarung |
|---|---|---|---|
| **A Günstigst** | `seedream_v5_lite` (1,0) | `veo3_1_lite` 6 s (6,0) | Preisuntergrenze mit lauffähigen Parametern |
| **B Kanal-realistisch** | `nano_banana_2` (1,5) | `kling3_0_turbo` 5 s (7,5) | Kling trifft die Clipdauer exakt; NB2 liefert 16:9-Startframes |
| **C Referenz/Konsistenz** | `seedream_v4_5` (1,0) | `seedance_2_0 fast` 5 s (17,5) | Einziger Weg mit `image_references` → Figurenkonsistenz über Shots (§5) |
| **D Premium 1080p** | `cinematic_studio_2_5` (2,0) | `seedance_2_0 std 1080p` 5 s (45,0) | Obergrenze, volle 1080p-Qualität |

### 4.3 Szenarien für **10:00** (140 Shots) — dauer-angepasste Preise

| Kombination | optimistisch (1,0/1,5) | realistisch (1,5/2,0) | pessimistisch (2,0/3,0) |
|---|---|---|---|
| **A Günstigst** | **1.400 cr** (66 €) | **1.890 cr** (90 €) | **2.800 cr** (133 €) |
| **B Kanal-realistisch** | **1.785 cr** (85 €) | **2.415 cr** (115 €) | **3.570 cr** (170 €) |
| **C Referenz/Konsistenz** | **3.815 cr** (181 €) | **5.110 cr** (243 €) | **7.630 cr** (362 €) |
| **D Premium 1080p** | **9.730 cr** (462 €) | **13.020 cr** (618 €) | **19.460 cr** (924 €) |

### 4.4 Szenarien für die **Medianlänge 12:12** (171 Shots) — dauer-angepasste Preise

| Kombination | optimistisch (1,0/1,5) | realistisch (1,5/2,0) | pessimistisch (2,0/3,0) |
|---|---|---|---|
| **A Günstigst** | **1.710 cr** (81 €) | **2.308 cr** (110 €) | **3.420 cr** (162 €) |
| **B Kanal-realistisch** | **2.180 cr** (104 €) | **2.950 cr** (140 €) | **4.360 cr** (207 €) |
| **C Referenz/Konsistenz** | **4.660 cr** (221 €) | **6.242 cr** (296 €) | **9.320 cr** (443 €) |
| **D Premium 1080p** | **11.884 cr** (565 €) | **15.903 cr** (755 €) | **23.769 cr** (1.129 €) |

### 4.5 Untergrenze mit den Kurzdauer-Preisen aus §2.1

Nur zur Einordnung — diese Clips sind **kürzer als der Medianshot** und in der Schnittfassung nicht 1:1 verwendbar.

| Kombination | 10:00 realistisch | 12:12 realistisch |
|---|---|---|
| A Günstigst | 1.330 cr (63 €) | 1.624 cr (77 €) |
| B Kanal-realistisch | 1.575 cr (75 €) | 1.924 cr (91 €) |
| C Referenz/Konsistenz | 4.130 cr (196 €) | 5.044 cr (240 €) |
| D Premium 1080p | 10.500 cr (499 €) | 12.825 cr (609 €) |

### 4.6 Sensitivität: gemessene 93,75 % bewegte Clips

Die Auftragsformel setzt `clips = shots`. Gemessen sind aber nur **93,75 %** der Shots bewegte Clips; der Rest sind Titelkarten/Grafiken, die kein Videomodell brauchen. Wer das einpreist, spart bei Kombination B / 10:00 / realistisch rund **131 Credits** (2.415 → 2.284 cr). Der Effekt ist klein gegenüber dem Ausschussfaktor und in den Haupttabellen bewusst **nicht** berücksichtigt.

---

## 5. Figurenkonsistenz — Einpreisung

Der Kanal hält Gesichter über viele Shots stabil. Beide Wege wurden geprüft:

| Weg | Tool | Kosten je wiederkehrender Figur | Status |
|---|---|---|---|
| **Reference Element** | `show_reference_elements(action:'create')` | **nicht ermittelt** | Das Tool-Schema hat **keinen `get_cost`-Parameter**. Eine Preisabfrage ohne Anlage ist nicht möglich; eine Anlage wäre ein absendender Aufruf und damit nach Regel 1 verboten. |
| **Soul-Training** | `show_characters(action:'train')` | **nicht ermittelt** | Ebenfalls **kein `get_cost`-Parameter**. Zusätzlich sind 5–20 Referenzfotos Pflicht, die hier nicht vorliegen. |

**Indikativer Anhaltspunkt (kein `get_cost`, daher nicht in den Summen):** Der Plan-Tooltip aus `show_plans_and_credits` beziffert 3.000 Credits als „~12000 images or ~500 videos or **~100 character generations**" → rechnerisch **≈ 30 Credits je „character generation"**. Bei **3 Figuren pro Video** wären das **≈ 90 Credits einmalig**. Was Higgsfield unter „character generation" genau versteht (Soul-Training? eine Generierung mit Soul?), geht aus dem Tooltip nicht hervor — die Zahl ist deshalb **nicht belastbar** und bewusst **nicht** in §4.3/§4.4 eingerechnet.

**Einordnung der Größenordnung:** Selbst wenn die Einmalkosten bei 30 cr/Figur lägen, wären 90 cr gegenüber 1.890–13.020 cr laufenden Kosten **unter 5 %**. Die Figurenkonsistenz ist im Higgsfield-Budget kein relevanter Hebel — der Hebel ist die **Modellwahl** (Faktor 7 zwischen A und D) und der **Ausschuss** (Faktor 2).

**Praktische Einschränkung, die die Modellwahl vorgibt:**
- **Soul** funktioniert nur mit `text2image_soul_v2` und `soul_cinema_studio` und nur für **eine** Person pro Generierung. Für Mehrpersonen-Shots (bei einem Geschichtskanal die Regel) ist Soul unbrauchbar.
- **Reference Elements** erlauben mehrere Figuren pro Shot und funktionieren u. a. mit `seedream_v4_5`, `seedream_v5_lite`, `nano_banana_2`, `cinematic_studio_2_5`, `seedance_2_0`, `kling3_0`.
- **→ Für diesen Kanalstil ist der Reference-Element-Weg der einzig praktikable.** Das schließt `veo3_1_lite` (Kombi A) als Konsistenz-Träger aus — es deklariert nur `start_image`/`end_image`, keine `image_references`. Konsistenz müsste dort komplett über den Startframe laufen.

**⚠️ Messlücke:** Alle `get_cost`-Werte in §2 wurden **ohne angehängte Referenzmedien** abgefragt. Ob eine referenzgetriebene Generierung denselben Preis hat, ist damit nicht belegt.

---

## 6. Nicht abgedeckt — was in der Rechnung fehlt

Ohne diesen Abschnitt ist jede Zahl oben irreführend niedrig. Die Higgsfield-Summe deckt **nur Startframes und Clips** ab.

### 6.1 Orchester-Score und Foley — nicht über Higgsfield lösbar
Laut Toolbeschreibung von `generate_audio` existieren `sonilo_music` (Musik) und `mirelo_text_to_audio` (Soundeffekte) **ausschließlich für die Game-Generation-Pipeline** und dürfen nicht für eigenständige Audioproduktion verwendet werden. Wörtlich: *„there is no standalone music/SFX model here — decline general music or sound-effect requests"*.
**→ Score und Foley müssen extern eingekauft werden.** Kosten: **nicht ermittelt** (außerhalb des Higgsfield-Scopes). Für einen Kanal mit durchgehendem Orchester-Score ist das ein realer Posten, kein Rundungsfehler.

### 6.2 Voiceover — über Higgsfield möglich, aber gedeckelt
`seed_audio` (Seed Audio 1.0, ByteDance), per `get_cost` gemessen:

| Prompt-Länge | Credits | Credits je 1.000 Zeichen |
|---|---|---|
| 100 Zeichen | 0,7 | 7,0 |
| 1.000 Zeichen | 6,7 | **6,7** |
| 2.000 Zeichen | 12,0 | 6,0 |

Der Preis pro 1.000 Zeichen sinkt leicht mit der Länge (7,0 → 6,0) — **nicht exakt linear**.

**⚠️ Hartes Limit gefunden:** Ein Test mit 8.000 Zeichen wurde abgewiesen:
`422 — "String should have at most 2048 characters"` (Request ID `ff465b4d-2f9c-424a-96fd-fc06e504bbef`).
**Ein 10-Minuten-Voiceover ist also nicht in einem Aufruf erzeugbar** und muss in Blöcke ≤ 2.048 Zeichen zerlegt werden — mit dem bekannten Risiko von Tonhöhen-/Tempo-Sprüngen an den Nahtstellen.

Hochrechnung (1.400 Wörter ≈ 8.260 Zeichen bei ~5,9 Zeichen/Wort):

| Länge | Zeichen | Aufrufe à 2.000 Z. | Credits | € |
|---|---|---|---|---|
| 10:00 | ~8.260 | 5 | **60 cr** | 2,85 € |
| 12:12 (Median) | ~10.080 | 6 | **72 cr** | 3,42 € |

Basis: gemessene 12,0 cr je 2.000-Zeichen-Aufruf. Die Zeichenzahl selbst ist aus der Auftragsangabe „1.400 Wörter" abgeleitet, nicht am Kanal gemessen.

### 6.3 Gar nicht abgedeckt — Kosten nicht ermittelt
| Posten | Warum es fehlt |
|---|---|
| **Schnitt / Assembly** | 140–171 Clips müssen geschnitten, getimt und gegradet werden. Kein Higgsfield-Posten. Bei 140 Shots je 10 min ist das der größte **Zeit**posten der Produktion. |
| **Titelkarten** | In 3 von 4 Messfenstern vorhanden (5 Stück in 270 s). Grafikarbeit, nicht generierbar. |
| **Kartenanimation** | Im Auftrag als Merkmal benannt; in den Messfenstern als Grafik-Shots gezählt. Braucht ein Motion-Graphics-Tool. |
| **Skript und Recherche** | Kompletter Vorlauf. Kein Higgsfield-Posten. |
| **Musiklizenz / Score** | Siehe §6.1. |
| **Upscaling auf 4K** | Alle Clip-Preise oben sind 720p (bzw. 1080p bei Kombi D). `upscale_video` existiert, wurde **nicht abgefragt** — nicht im Auftragsumfang. |

**Faustregel zur Einordnung:** Die Higgsfield-Zahl in §4 ist der **Materialpreis**, nicht der Produktionspreis.

---

## 7. Blockiert / nicht ermittelt

| # | Aufruf | Modell / Tool | Fehler bzw. Grund |
|---|---|---|---|
| 1 | `models_explore(action:'get', model_id:'nano_banana_flash')` | `nano_banana_flash` | `Unknown error` |
| 2 | `generate_image(model:'nano_banana_flash', get_cost:true)` | `nano_banana_flash` | `Invalid request: unknown model "nano_banana_flash". Use models_explore(action:'list') to see available models.` → **Das Modell existiert in diesem Workspace nicht.** Nächstliegendes real existierendes Modell laut `models_explore(action:'search')`: **`nano_banana_2_lite`** („Nano Banana 2 Lite", Google), per `get_cost` mit `16:9` gemessen: **1,0 Credit**. Ersatzwert, ausdrücklich **nicht** als `nano_banana_flash` ausgewiesen. |
| 3 | Preisabfrage Reference Element | `show_reference_elements(action:'create')` | **Kein `get_cost`-Parameter im Tool-Schema.** Preflight unmöglich; Anlage wäre ein absendender Aufruf → nach Regel 1 nicht durchgeführt. **Nicht ermittelt.** |
| 4 | Preisabfrage Soul-Training | `show_characters(action:'train')` | **Kein `get_cost`-Parameter im Tool-Schema**, zusätzlich 5–20 Referenzfotos erforderlich, die nicht vorliegen. **Nicht ermittelt.** |
| 5 | `generate_audio(model:'seed_audio')` mit 8.000 Zeichen | `seed_audio` | `422 — cost params failed validation: "String should have at most 2048 characters"` (Request ID `ff465b4d-2f9c-424a-96fd-fc06e504bbef`). Ersatzweise bei 2.000 Zeichen gemessen und hochgerechnet (§6.2). |
| 6 | Kosten Score / Foley | `sonilo_music`, `mirelo_text_to_audio` | Laut Toolbeschreibung **nur für die Game-Pipeline freigegeben**, nicht für eigenständige Audioproduktion. Bewusst **nicht abgefragt**. **Nicht ermittelt.** |
| 7 | Kosten referenzgetriebener Generierungen | alle Videomodelle | Alle `get_cost`-Werte ohne angehängte Referenzmedien abgefragt (kein `media_id` vorhanden, Upload wäre ein absendender Aufruf). Preisgleichheit mit Referenz **nicht belegt**. |
| 8 | Ausschussfaktor | — | **Nicht messbar** aus öffentlich sichtbaren Kanaldaten. Bleibt geraten (§4.1). |

**Keine Freigabe wurde verweigert** — es gab keine blockierten Berechtigungsabfragen. Alle Ausfälle sind Tool-/Schema-Grenzen, keine Genehmigungsprobleme.

---

## 8. Reicht der aktuelle Credit-Stand?

**Kontostand am 12.08.2026 (`higgsfield:balance`): 3.219,9 Credits, Plan ULTRA.**

| Kombination | 10:00 realistisch (+VO 60 cr) | reicht? | 12:12 realistisch (+VO 72 cr) | reicht? |
|---|---|---|---|---|
| A Günstigst | 1.950 cr | **ja** | 2.380 cr | **ja** |
| B Kanal-realistisch | 2.475 cr | **ja** | 3.022 cr | **ja**, mit 198 cr Puffer |
| C Referenz/Konsistenz | 5.170 cr | **nein** | 6.314 cr | **nein** |
| D Premium 1080p | 13.080 cr | **nein** | 15.975 cr | **nein** |

> **Antwort in einem Satz: Ja — der Stand von 3.219,9 Credits reicht für einen vollständigen Durchlauf in den Kombinationen A und B (10:00 wie auch 12:12 Medianlänge, Voiceover eingerechnet), aber nicht für die referenzgetriebene Kombination C oder die 1080p-Kombination D, die das Guthaben um Faktor 2 bzw. 5 übersteigen.**

Einschränkungen zu diesem Ja: Es gilt beim **realistischen** Ausschussfaktor. Im pessimistischen Szenario (2,0/3,0) reicht der Stand bei 12:12 nur noch für Kombination A (3.420 cr + 72 cr VO = 3.492 cr) **nicht mehr** — dort fehlen 272 Credits. Und der Ausschussfaktor ist die eine Zahl in diesem Dokument, die **nicht gemessen** ist.

---

## Quellenverzeichnis

| Datum | Quelle | Was daraus stammt |
|---|---|---|
| 12.08.2026 | `NexLev:watch_youtube_video_and_ask`, 4 Fenster | Shotzahlen, Shotlängen, Anteil bewegter Clips (§1.2) |
| 12.08.2026 | `NexLev:youtube_channel_videos` (`UCR4Ech9MtQ1R-MidNIc9Y6g`) | 9 Langform-Längen, Median 12:12 (§1.4) |
| 12.08.2026 | `higgsfield:models_explore(action:'get')`, 13 Modelle | Parametervalidierung, erlaubte Dauern/Auflösungen (§2) |
| 12.08.2026 | `higgsfield:generate_video(get_cost:true)`, 13 Abfragen | Alle Clip-Preise (§2.1, §2.2) |
| 12.08.2026 | `higgsfield:generate_image(get_cost:true)`, 6 Abfragen | Alle Bildpreise (§2.3) |
| 12.08.2026 | `higgsfield:generate_audio(get_cost:true)`, 4 Abfragen | VO-Preise + 2048-Zeichen-Limit (§6.2) |
| 12.08.2026 | `higgsfield:show_plans_and_credits(intent:'topup')` | Credit→Euro-Kurs, „character generations"-Tooltip (§3, §5) |
| 12.08.2026 | `higgsfield:balance` | Kontostand 3.219,9 cr (§8) |
| 12.08.2026 | `higgsfield:transactions` (40 Einträge) | Ist-Abrechnung Nano Banana 2 = 2 cr (§2.3) |
| 12.08.2026 | `higgsfield:show_reference_elements(action:'list')` / `show_characters(action:'list')` | Beide leer — keine historischen Kostenbelege für Figurenkonsistenz (§5) |
