# Was kostet eine 20-Minuten-Folge in Storikon-Machart bei Higgsfield?

**Stand:** 12.08.2026 · **Kontostand vor der Aufgabe: 3.185,9 Credits** (Plan ULTRA)
**Kreditverbrauch dieser Aufgabe: 0 von 30** — es wurden ausschließlich `get_cost`-Preflights gemacht, die nichts abbuchen. Keine Generierung.

**Quellen (gelesen, nicht neu gemessen):**
`bewertungen/higgsfield-kosten-storikon.md` · `bewertungen/storikon-shotanalyse.md` · `bewertungen/storikon-stilspezifikation.md` · `bewertungen/daten/storikon_stilmesswerte.json` — alle vier vorhanden.

---

## 1. Der Bildpreis ist aufgelöst — und der „Widerspruch" war keiner

Die Kostenanalyse notierte: Preflight meldet `credits_exact: 1.5`, die Abrechnung zeigt −2 cr. Die Einzelbuchungen aus `transactions` klären das.

### Die Buchungen des Stillaufs

| Zeitstempel | Posten | Buchung | Anzahl |
|---|---|---|---|
| 15:18:17 | Nano Banana 2 | −2 cr | 4 (C1) |
| 15:18:18 | Seedream 4.5 | −1 cr | 4 (C1) |
| 15:22:14 | Nano Banana 2 | −2 cr | 4 (C3) |
| **Summe** | | **20 cr** | 12 Bilder |

Das deckt sich exakt mit dem gemeldeten Verbrauch 3.211,9 → 3.191,9.

### Auflösung

**Der Preflight war nie falsch — er wurde nur bei einer anderen Auflösung abgefragt.**

| Abfrage | Preflight | Abgerechnet | Deckung |
|---|---|---|---|
| `nano_banana_2`, Auflösung **1k** (Default) | `credits: 1`, `credits_exact: 1.5` | *aus eigenen Läufen nicht belegt* | — |
| `nano_banana_2`, Auflösung **2k** | `credits: 2`, `credits_exact: 2` | **−2 cr** | **exakt** |

Die alte Notiz verglich einen **1k-Preflight** mit Buchungen **unbekannter Auflösung**. Das war kein Widerspruch, sondern ein Vergleich zweier verschiedener Konfigurationen.

**Beleg für 2k = 2,0 cr:** heute 15 einzelne Buchungen über `nano_banana_2`, **alle −2 cr**, alle bei 2k (4 × 14:12, 4 × 15:18, 4 × 15:22, 3 × 15:56). Kontostand 3.219,9 → 3.185,9 = 34 cr = 15 × 2 + 4 × 1 (Seedream). Rechnet auf.

### Der maßgebliche Wert

**2,0 Credits je Bild** (`nano_banana_2`, 2K, 16:9). Gegenüber dem in der alten Analyse verwendeten 1,5 sind das **+33,3 %**.

Bei 300 Bildern für eine 20-Minuten-Folge: 600 cr statt 450 cr — **150 Credits Unterschied**, genau die Größenordnung, die die Aufgabe befürchtet hat.

**Warum nicht 1k nehmen und die Hälfte sparen?** Weil 40,5 % der Shots als Standbild mit Kamerafahrt laufen (§2). Eine Ken-Burns-Fahrt **schneidet in das Bild hinein** — bei 1080p-Ausgabe und bis zu 8 % Zoom braucht die Quelle Reserve. 1k (1024 px) liegt bereits unter 1080p. **2K ist hier technisch erforderlich, nicht Komfort.**

---

## 2. Shotmodell

```
shots           = laufzeit / 4,00 s      Median Langform (125 Shots),
                                         bestätigt durch 4,12 s / 3,73 s im Kurzformat
bewegtshots     = shots × 0,568          GEMESSEN (ORB-Homographie + optischer Fluss)
standbildshots  = shots × 0,405          GEMESSEN
rest            = shots × 0,027          unklassifiziert, wird als Bewegtshot gerechnet
```

| | **20:00** (1200 s) | **12:12** (732 s) |
|---|---|---|
| Shots gesamt | **300** | **183** |
| davon bewegt (56,8 %) | 170,4 | 103,9 |
| davon Standbild (40,5 %) | 121,5 | 74,1 |
| unklassifiziert (2,7 %) | 8,1 | 4,9 |

### ⚠️ Video wird nach Sekunden abgerechnet, nicht nach Shots

Die Shotanteile oben genügen für den **Bild**bedarf (ein Bild je Shot). Für die **Clip**kosten sind sie zu niedrig, denn die gemessenen Bewegtclips sind **1,27 × länger** als Standbildshots:

| Klasse | Anteil nach Shots | mittlere Dauer | **Anteil nach Sekunden** |
|---|---|---|---|
| A — Standbild mit Fahrt | 40,5 % | 3,48 s | **34,7 %** |
| B — Bewegtclip | 56,8 % | 4,44 s | **61,8 %** |
| Grenzfall | 2,7 % | 5,38 s | **3,6 %** |
| **Video gesamt (B + Grenzfall)** | **59,5 %** | | **65,3 %** |

**Gerechnet wird deshalb: Bilder nach Shotzahl, Clips nach Sekundenanteil (65,3 %).** Mit dem Shotanteil zu rechnen würde die Clipkosten um rund 10 % zu niedrig ansetzen.

Videosekunden: **783,6 s** bei 20:00 · **478,0 s** bei 12:12.

---

## 3. ffmpeg-Baustein: Standbild mit Kamerafahrt

Ein Standbildshot braucht **kein Videomodell** — ein Bild plus ein Zoompfad, lokal gerechnet, **Kosten null**. Das ist der größte einzelne Hebel der ganzen Rechnung.

Parameter aus der Stilspezifikation (A4): Zoomrate Median −0,07 %/s, P10 −1,44 %/s, P90 +2,31 %/s, **keine Rotation**. Der Baustein unten fährt +1,5 %/s — innerhalb der gemessenen Spanne.

```bash
ffmpeg -y -loop 1 -i shot_042.png \
  -filter_complex "zoompan=z='min(1+0.015*on/25,1.5)':d=100:\
x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25,format=yuv420p" \
  -t 4 -c:v libx264 -crf 18 -preset veryfast shot_042.mp4
```

**Verifiziert, nicht behauptet** — der Aufruf wurde ausgeführt: Ergebnis 1920×1080, 25 fps, 100 Frames, Dauer exakt 4,000 s.

Stellschrauben: `0.015` = Zoom pro Sekunde (0,000 bis 0,023 deckt die gemessene Spanne ab) · `d=100` = Frames (4 s × 25) · Für einen Schwenk statt Zoom `x=` durch einen Pfad wie `'(iw-iw/zoom)*on/100'` ersetzen.

---

## 4. Kostentabelle (Credits, inkl. Voiceover)

**Preise** — alle aus dem Kostendokument, Bildpreis aus §1 korrigiert:

| Posten | Wert | Herkunft |
|---|---|---|
| `nano_banana_2` 2K | **2,0 cr/Bild** | **abgerechnet**, 15 Buchungen |
| `veo3_1_lite` | 1,0 cr/s, Raster 4/6/8 s | `get_cost` |
| `kling3_0_turbo` | 1,5 cr/s, Raster 3–15 s ganzzahlig | `get_cost` |
| Quantisierungsfaktor veo | **1,2577** (+25,8 %) | Dauerraster gegen die gemessene 125-Shot-Verteilung |
| Quantisierungsfaktor kling | **1,1102** (+11,0 %) | dito |

Das Raster entscheidet mehr als der Sekundenpreis: veo ist mit 1,0 cr/s nominal ein Drittel billiger als kling, verliert aber 25,8 % der bezahlten Clipzeit an das grobe 4/6/8-Raster.

**Abgerechnete Clipsekunden:**

| Länge | Modell | V1 | V2 | V3 |
|---|---|---|---|---|
| 20:00 | veo3_1_lite | 1509,2 s | 985,5 s | 492,8 s |
| 20:00 | kling3_0_turbo | 1332,2 s | 870,0 s | 435,0 s |
| 12:12 | veo3_1_lite | 920,6 s | 601,2 s | 300,6 s |
| 12:12 | kling3_0_turbo | 812,7 s | 530,7 s | 265,3 s |

### 20:00

| Variante | Videomodell | günstigst (1,0/1,5) | mittel (1,5/2,0) | schlechtest (2,0/3,0) |
|---|---|---|---|---|
| **V1** Storikon 1:1 | veo3_1_lite | 2.972 cr | 4.026 cr | 5.836 cr |
| **V1** Storikon 1:1 | kling3_0_turbo | 3.706 cr | 5.005 cr | 7.303 cr |
| **V2** gemessene Aufteilung | veo3_1_lite | **2.186 cr** | **2.979 cr** | **4.265 cr** |
| **V2** gemessene Aufteilung | kling3_0_turbo | 2.665 cr | 3.618 cr | 5.223 cr |
| **V3** Zweitverwendung 50 % | veo3_1_lite | 1.147 cr | 1.544 cr | 2.186 cr |
| **V3** Zweitverwendung 50 % | kling3_0_turbo | 1.387 cr | 1.863 cr | 2.665 cr |

### 12:12

| Variante | Videomodell | günstigst | mittel | schlechtest |
|---|---|---|---|---|
| **V1** Storikon 1:1 | veo3_1_lite | 1.819 cr | 2.462 cr | 3.566 cr |
| **V1** Storikon 1:1 | kling3_0_turbo | 2.266 cr | 3.059 cr | 4.461 cr |
| **V2** gemessene Aufteilung | veo3_1_lite | **1.340 cr** | **1.823 cr** | **2.608 cr** |
| **V2** gemessene Aufteilung | kling3_0_turbo | 1.632 cr | 2.213 cr | 3.192 cr |
| **V3** Zweitverwendung 50 % | veo3_1_lite | 706 cr | 948 cr | 1.340 cr |
| **V3** Zweitverwendung 50 % | kling3_0_turbo | 852 cr | 1.143 cr | 1.632 cr |

### Zu den drei Varianten

**V1 — Storikon 1:1.** Jeder Shot als Videogenerierung, auch die statischen. Vermutlich so, wie der Kanal es macht. **Obergrenze.**

**V2 — gemessene Aufteilung.** 65,3 % der Sekunden als Videogenerierung, 34,7 % als Bild plus ffmpeg-Fahrt. Bildbedarf bleibt bei 100 % der Shots. **Das ist die realistische Arbeitsweise für eine Eigenproduktion** und spart gegenüber V1 rund 26 %.

**V3 — Zweitverwendung 50 %. ⚠️ HYPOTHETISCH, kein Befund über Storikon.**
Die Messung ergab **rho = 1,00**: null Dubletten, null Ausschnitte, jeder Shot ist eigenes Material. **Die V3-Variante der alten Kostenanalyse ist für Storikon damit widerlegt.** Sie steht hier als **mögliche eigene Arbeitsweise**, nicht als Nachbau des Vorbilds.
**Einschränkung:** rho wurde an 94 und 57 Sekunden **Kurzformat** gemessen. Über zwanzig Minuten ist Wiederverwendung deutlich wahrscheinlicher — die Messung **schließt sie für eine Langform nicht aus**. V3 ist also weder belegt noch ausgeschlossen.

### Seedream-Vergleichszeile (nur Preis, **keine Option**)

| Länge | `nano_banana_2` | `seedream_v4_5` | Differenz |
|---|---|---|---|
| 20:00 | 600 cr | 300 cr | 300 cr |
| 12:12 | 366 cr | 183 cr | 183 cr |

**Nicht empfohlen.** In der Stilabnahme landeten alle vier `seedream_v4_5`-Kandidaten auf den Rängen 8, 9, 11 und 12; ihr Laplace-Verhältnis lag bei 0,22–0,30, sie rendern zu glatt für diesen Look. Die 300 Credits sind gespart, indem man den Stil verfehlt.

---

## 5. Euro — alle drei Kurse

Der Kurs bleibt mehrdeutig (`monthly_final_price_cents` stand auf 0). **Es wird nicht behauptet, welcher gilt.**

### 20:00

| Variante | Modell | @ 0,0475 €/cr | @ 0,0330 €/cr | @ 0,00275 €/cr |
|---|---|---|---|---|
| V1 | veo3_1_lite | 141–277 € | 98–193 € | 8,17–16,05 € |
| V1 | kling3_0_turbo | 176–347 € | 122–241 € | 10,19–20,08 € |
| **V2** | **veo3_1_lite** | **104–203 €** | **72–141 €** | **6,01–11,73 €** |
| V2 | kling3_0_turbo | 127–248 € | 88–172 € | 7,33–14,36 € |
| V3 | veo3_1_lite | 54–104 € | 38–72 € | 3,15–6,01 € |
| V3 | kling3_0_turbo | 66–127 € | 46–88 € | 3,81–7,33 € |

### 12:12

| Variante | Modell | @ 0,0475 €/cr | @ 0,0330 €/cr | @ 0,00275 €/cr |
|---|---|---|---|---|
| V1 | veo3_1_lite | 86–169 € | 60–118 € | 5,00–9,81 € |
| V1 | kling3_0_turbo | 108–212 € | 75–147 € | 6,23–12,27 € |
| **V2** | **veo3_1_lite** | **64–124 €** | **44–86 €** | **3,68–7,17 €** |
| V2 | kling3_0_turbo | 78–152 € | 54–105 € | 4,49–8,78 € |
| V3 | veo3_1_lite | 34–64 € | 23–44 € | 1,94–3,68 € |
| V3 | kling3_0_turbo | 40–78 € | 28–54 € | 2,34–4,49 € |

---

## 6. Voiceover — separat

Modell `seed_audio`, **hartes Limit 2.048 Zeichen je Aufruf** (bei 8.000 Zeichen: `422 — String should have at most 2048 characters`).

| Größe | 20:00 | 12:12 |
|---|---|---|
| gesprochene Wörter | ~2.800 | ~1.708 |
| Zeichen (bei ~5,9 Zeichen/Wort inkl. Leerzeichen) | ~16.520 | ~10.077 |
| Aufrufe à 2.000 Zeichen | **9** | **6** |
| Preis je Aufruf | **12,0 cr** (per `get_cost` bestätigt) | 12,0 cr |
| **Summe** | **108 cr** | **72 cr** |
| in Euro @ 0,0475 | 5,13 € | 3,42 € |

Die 12,0 cr wurden in dieser Aufgabe mit einem exakt 2.000 Zeichen langen Prompt neu bestätigt. Zeichenzahl je Wort ist **geschätzt**, Aufrufzahl und Preis sind belegt.

**Praktische Folge:** Neun Blöcke bedeuten acht Nahtstellen im Voiceover, an denen Tonhöhe und Tempo springen können. Das ist ein Qualitätsrisiko, kein Kostenrisiko.

---

## 7. Reichweite der Credits

**Vorhanden: 3.185,9 cr. Monatskontingent: 3.000 cr.**

Für **eine 20-Minuten-Folge**:

| Variante | Modell | günstigst | mittel | schlechtest | Folgen je 3.000 cr |
|---|---|---|---|---|---|
| V1 | veo3_1_lite | ✅ 2.972 | ❌ 4.026 | ❌ 5.836 | 0,5 – 1,0 |
| V1 | kling3_0_turbo | ❌ 3.706 | ❌ 5.005 | ❌ 7.303 | 0,4 – 0,8 |
| **V2** | **veo3_1_lite** | ✅ 2.186 | ✅ 2.979 | ❌ 4.265 | **0,7 – 1,4** |
| V2 | kling3_0_turbo | ✅ 2.665 | ❌ 3.618 | ❌ 5.223 | 0,6 – 1,1 |
| V3 | veo3_1_lite | ✅ 1.147 | ✅ 1.544 | ✅ 2.186 | 1,4 – 2,6 |
| V3 | kling3_0_turbo | ✅ 1.387 | ✅ 1.863 | ✅ 2.665 | 1,1 – 2,2 |

**Die entscheidende Zahl:** Selbst in der günstigsten realistischen Variante (V2 + veo) passt **noch nicht einmal eineinhalb** 20-Minuten-Folgen in ein Monatskontingent. Bei mittlerem Ausschuss ist es **eine Folge pro Monat** — und die schöpft das Kontingent fast vollständig aus.

Ein wöchentlicher Rhythmus mit 20-Minuten-Folgen ist mit 3.000 Credits/Monat **nicht darstellbar**, in keiner Variante außer V3 bei niedrigem Ausschuss.

---

## 8. Gemessen vs. angenommen

### Gemessen

| Zahl | Wert | Verfahren |
|---|---|---|
| Bildpreis `nano_banana_2` 2K | **2,0 cr** | 15 Einzelbuchungen aus `transactions`, Kontostand rechnet auf |
| Bildpreis `seedream_v4_5` | 1,0 cr | 4 Einzelbuchungen |
| Sekundenpreise veo / kling | 1,0 / 1,5 cr/s | `get_cost`, Kostendokument |
| Dauerraster | 4/6/8 s · 3–15 s | `models_explore` |
| Quantisierungsfaktoren | 1,2577 / 1,1102 | Raster gegen die 125-Shot-Verteilung gerechnet |
| Median-Shotlänge | 4,00 s | 125 Shots Langform; 4,12 / 3,73 s Kurzformat |
| **Bewegt-/Standbildanteil** | **56,8 % / 40,5 %** | ORB-Homographie, bimodal, per optischem Fluss gegengeprüft |
| **Anteil nach Sekunden** | **65,3 % Video** | dieselben Daten, nach Dauer gewichtet |
| Bewegtclips länger als Standbild | Faktor 1,27 | mittlere Dauer 4,44 s vs 3,48 s |
| Zoomrate der Kamerafahrten | −1,44 bis +2,31 %/s | 15 sauber vermessene Shots |
| Mehrfachverwendung Kurzformat | rho = 1,00 | pHash + Homographie, 0 Treffer |
| Voiceover je 2.000 Zeichen | 12,0 cr | `get_cost` in dieser Aufgabe |
| Voiceover-Limit | 2.048 Zeichen | 422-Fehler |
| ffmpeg-Baustein | 4,000 s, 1920×1080 | Aufruf ausgeführt und per `ffprobe` geprüft |
| Kontostand | 3.185,9 cr | `balance` |

### Angenommen

| Annahme | Wert | Warum offen |
|---|---|---|
| **Ausschussfaktor Bild** | 1,0 / 1,5 / 2,0 | **ungemessen — die einzige große Unbekannte** |
| **Ausschussfaktor Clip** | 1,5 / 2,0 / 3,0 | **ungemessen** |
| Zeichen je gesprochenem Wort | ~5,9 | Konvention, nicht am Kanal gemessen |
| Wörter je Minute | 140 | daraus 2.800 Wörter für 20 Minuten |
| Shotlänge in der 20-Minuten-Folge | 4,00 s wie bei 12:12 | längere Folgen könnten anders geschnitten sein |
| Bewegt-/Standbildanteil gilt für Langform | ja | gemessen an Shorts |
| Titelkarten kosten nichts | ja | im Schnittprogramm baubar |
| V3-Zweitverwendung 50 % | gesetzt | **für Storikon widerlegt** (rho=1,00), als eigene Option gerechnet |
| Euro-Kurs | drei Lesarten | Preisdaten mehrdeutig |

### Randnotiz zum Ausschuss — bewusst keine Zahl

Im Stillauf waren von 8 Kandidaten 4 unbrauchbar (alle `seedream_v4_5`). **Das ist Modellwahl, keine Ausschussquote** — die vier scheiterten am falschen Modell, nicht an Zufall. Zwei weitere (`k3`, `k2`) trugen Letterbox-Balken; das käme einer Ausschussquote näher, sind aber nur 2 von 8 bei n=8. **Daraus wird hier keine Zahl abgeleitet.**

---

## 9. Was diese Rechnung nicht enthält

| Posten | Status |
|---|---|
| **Musik / Orchester-Score** | **Nicht über Higgsfield lösbar.** `sonilo_music` ist laut Toolbeschreibung ausschließlich für die Game-Pipeline freigegeben, nicht für eigenständige Audioproduktion. Extern einzukaufen, Kosten nicht ermittelt. |
| **Foley / Soundeffekte** | Ebenso — `mirelo_text_to_audio` nur für die Game-Pipeline. |
| **Schnitt / Assembly** | 300 Clips müssen geschnitten, getimt und gegradet werden. Bei 20 Minuten der größte **Zeit**posten der Produktion. Kein Higgsfield-Posten. |
| **Titelkarten** | Im gemessenen Material 4,8 % der Shots. Grafikarbeit im Schnittprogramm. |
| **Kartenanimation** | 2,4 % der Shots. Braucht ein Motion-Graphics-Werkzeug. |
| **Skript und Recherche** | Kompletter Vorlauf. Bei 2.800 Wörtern Fließtext der eigentliche inhaltliche Aufwand. |
| **Upscaling auf 4K** | Alle Preise gelten für 2K-Bilder und 720p-Clips. `upscale_video` nicht abgefragt. |
| **Farbkorrektur** | Der Anker liegt 25,5 Prozentpunkte unter der Zielsättigung — im Schnitt nachzuziehen, kostet Zeit, keine Credits. |

**Die Higgsfield-Zahl ist der Materialpreis, nicht der Produktionspreis.**

---

## 10. Was ein Ausschuss-Messlauf kostet

Der Ausschussfaktor spannt die Endsumme um **Faktor 2,0** auf (V2/veo: 2.186 bis 4.265 cr). Er ist die einzige verbliebene große Unbekannte. So wäre er zu messen:

**Aufbau:** 20 Clips mit dem festgelegten Anker `stil-anker-v1` (`d9ec37ca-e7aa-49c6-bebb-3c90339bd6b1`) erzeugen, jeweils 4 s, Motive aus einem echten Folgenskript. Dann zählen, wie viele ohne Nachgenerierung in den Schnitt könnten.

| Testumfang | Rechnung | Kosten |
|---|---|---|
| Nur Bildausschuss (20 Startbilder) | 20 × 2,0 cr | **40 cr** |
| Bild + Clip, `veo3_1_lite` 4 s | 40 + 20 × 4,0 cr | **120 cr** |
| Bild + Clip, `kling3_0_turbo` 4 s | 40 + 20 × 6,0 cr | **160 cr** |

**Empfehlung: die 120-cr-Variante.** Sie misst beide Ausschussfaktoren an einem Durchlauf. Gemessen an einer 20-Minuten-Folge, die zwischen 2.186 und 4.265 cr kostet, sind 120 cr **rund 3 %** — und sie halbieren die Unsicherheit der Planung. Bei n=20 ist der Vertrauensbereich noch grob (±11 Prozentpunkte bei einer Quote um 50 %), aber es ist der Unterschied zwischen einer geratenen und einer gemessenen Zahl.

---

## 11. Zwei Sätze zum Schluss

**Was kostet eine 20-Minuten-Folge realistisch?** In der realistischen Arbeitsweise (V2 — gemessene Aufteilung, `veo3_1_lite`, Standbildshots lokal per ffmpeg) liegt sie bei **2.186 bis 4.265 Credits inklusive Voiceover**, im mittleren Ausschussfall bei rund **2.979 Credits**; in Euro sind das **104 bis 203 €** zum belegten Top-up-Kurs, **72 bis 141 €** zur monatlichen und **6 bis 12 €** zur jährlichen Abo-Lesart — der Kurs ist damit eine größere Unsicherheit als der Ausschuss, weil zwischen seinen Lesarten Faktor 12 liegt, während der Ausschuss nur Faktor 2 aufspannt.

**Welche eine Messung verengt die Spanne am stärksten?** Nicht der Ausschusslauf, sondern die **Klärung des Credit-Kurses** — eine Auskunft darüber, welchen Betrag du pro Abrechnungszeitraum zahlst und wie viele Credits er enthält, kostet null Credits und beseitigt den Faktor 12; erst danach lohnt der 120-Credit-Ausschusslauf, der den verbleibenden Faktor 2 auf etwa Faktor 1,3 zusammenzieht.
