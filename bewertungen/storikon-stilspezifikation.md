# Storikon — Bildstil gemessen und als Anker repliziert

**Quelle:** zwei hochgeladene Videodateien (`/root/.claude/uploads/…`)
**Analysedatum:** 12.08.2026 · **Kein Downloadversuch** — ausschließlich das hochgeladene Material.
**Messwerkzeug:** `produktion/pipeline/stilmessung.py` (in dieser Sitzung gebaut, mitcommittet)
**Referenzdaten:** `bewertungen/daten/storikon_stilmesswerte.json`

---

## 0. Die zwei Befunde, die alles andere prägen

**1. Es liegt nur Kurzformat vor.** Beide Dateien sind 9:16-Shorts. Die Spezifikation beruht damit **auf dem Kurzformat**; die Übertragung auf 16:9 ist **ungeprüft**. Der Anker wurde trotzdem in 16:9 erzeugt, weil er dort gebraucht wird — dass die gemessenen Werte im Querformat gleich ausfallen, ist eine **Annahme**, keine Messung.

**2. Der Kanal hat nicht EINEN Bildstil, sondern zwei.** Die beiden Dateien weichen bei 6 von 8 Messgrößen um mehr als 15 % voneinander ab — auf dieselbe Prüfschwelle, die im Auftrag für den Format-Vergleich vorgesehen war:

| Größe | short_B (dunkel) | short_XIX (hell) | Abweichung |
|---|---|---|---|
| Helligkeit Median | 10,59 | 27,45 | **61,4 %** |
| Helligkeit P10 | 3,92 | 11,56 | **66,1 %** |
| Helligkeit P90 | 38,43 | 65,30 | **41,1 %** |
| Sättigung Median | 50,20 | 31,37 | **37,5 %** |
| Laplace-Varianz | 293,52 | 674,66 | **56,5 %** |
| Kantendichte oben | 0,02 | 0,08 | **75,0 %** |
| Kantendichte unten | 0,04 | 0,14 | **71,4 %** |
| Kontrastumfang | 67,06 | 74,12 | 9,5 % |

Das ist kein Rauschen, das ist ein anderer Look. Der Augenschein bestätigt es eindeutig:

- **short_B** — Nachtschwarz, **eine** warme Feuerquelle gegen türkise Kaltschatten, absaufende Schatten bis zur reinen Silhouette, lockerer sichtbarer Duktus. Motive: Weltkrieg, Russland, Industrie.
- **short_XIX** — Taghell, ***ligne claire*** mit harten schwarzen Tuschekonturen, flache Farbflächen, blauer Himmel, weiße Wolken. Motive: Brasilien, 19. Jahrhundert, Segelschiffe.

**Ein gepoolter Median (Helligkeit 16,47) träfe keine der beiden Dateien.** Die Referenz wurde deshalb auf das **dunkle Register (short_B)** gelegt — es deckt sich mit den Motiven der Langform-Shotliste aus der Vorsitzung („Dark city street", „Molten metal in factory", „Miners cave", „Sunset over industrial city"). Das helle Register liegt als eigene Datei bei (`storikon_stilmesswerte_hell.json`) und bräuchte einen **eigenen** Anker.

---

## 1. Dateibestand (A0, `ffprobe`)

| Datei | Dauer | Auflösung | Seitenverhältnis | Einordnung | Bildrate | Codec | Größe |
|---|---|---|---|---|---|---|---|
| `f7cff0e9-…XIX….mp4` | 57,00 s | 1080×1920 | 9:16 | **Short** | 24,0 | h264 | 29,0 MB |
| `5deced45-….mp4` | 93,81 s | 1080×1920 | 9:16 | **Short** | 24,0 | h264 | 31,0 MB |

**Kein 16:9-Material vorhanden.** Der im Auftrag vorgesehene Format-Vergleich Short gegen Langform entfällt mangels Langform (§2 wird stattdessen zum Register-Vergleich, siehe §0).

---

## 2. Formatvergleich

Entfällt — beide Dateien sind 9:16. An seine Stelle tritt der **Register-Vergleich** in §0, der dieselbe 15-%-Prüfschwelle anwendet und sie deutlich reißt.

---

## 3. Schnittlisten und Histogramme (A1, PySceneDetect ContentDetector)

**Schwellenwert-Prüfung:** Die Erkennung ist über den geprüften Bereich stabil, eine Justage war nicht nötig.

| Datei | Schwelle 20 | Schwelle 27 | Schwelle 35 |
|---|---|---|---|
| short_XIX | 16 Shots / 3,73 s | 16 Shots / 3,73 s | 16 Shots / 3,73 s |
| short_B | 23 Shots / 3,88 s | 21 Shots / 4,12 s | 21 Shots / 4,12 s |

**Verwendet: Schwelle 27.**

**Abgleich mit der Langform** (4,00 s Median über 125 Shots, Vorsitzung, per Videowerkzeug):
short_B **4,12 s (+3,0 %)** · short_XIX **3,73 s (−6,8 %)**. Beide unter 10 % Abweichung — **der Schnittrhythmus der Shorts entspricht dem der Langform.** Weder Kurzformat noch Schwelle verzerren hier etwas.


#### short_B (dunkles Register, 93,8 s) — 21 Shots, Median 4.12 s, Mittel 4.47 s

| Shot | Start | Ende | Dauer | Bewegungsurteil | Inlier | Restfehler |
|---|---|---|---|---|---|---|
| 1 | 0.00 s | 3.83 s | 3.83 s | B Eigenbewegung | 0.07 | 542.4 px |
| 2 | 3.83 s | 9.17 s | 5.33 s | B Eigenbewegung | 0.29 | 268.3 px |
| 3 | 9.17 s | 14.38 s | 5.21 s | B Eigenbewegung | 0.04 | 236.9 px |
| 4 | 14.38 s | 18.25 s | 3.88 s | B Eigenbewegung | 0.12 | 156.0 px |
| 5 | 18.25 s | 23.71 s | 5.46 s | B Eigenbewegung | 0.22 | 153.6 px |
| 6 | 23.71 s | 27.33 s | 3.62 s | B Eigenbewegung | 0.26 | 363.2 px |
| 7 | 27.33 s | 36.50 s | 9.17 s | B Eigenbewegung | 0.09 | 229.5 px |
| 8 | 36.50 s | 40.04 s | 3.54 s | A Standbild+Fahrt | 0.74 | 1.4 px |
| 9 | 40.04 s | 42.08 s | 2.04 s | B Eigenbewegung | 0.44 | 45.6 px |
| 10 | 42.08 s | 45.75 s | 3.67 s | A Standbild+Fahrt | 0.71 | 1.4 px |
| 11 | 45.75 s | 48.46 s | 2.71 s | A Standbild+Fahrt | 0.90 | 0.9 px |
| 12 | 48.46 s | 51.79 s | 3.33 s | A Standbild+Fahrt | 0.98 | 1.0 px |
| 13 | 51.79 s | 57.08 s | 5.29 s | B Eigenbewegung | 0.07 | 181.9 px |
| 14 | 57.08 s | 61.21 s | 4.12 s | A Standbild+Fahrt | 0.95 | 0.8 px |
| 15 | 61.21 s | 64.33 s | 3.12 s | A Standbild+Fahrt | 0.85 | 1.3 px |
| 16 | 64.33 s | 69.71 s | 5.38 s | Grenzfall | 0.51 | 3.0 px |
| 17 | 69.71 s | 75.83 s | 6.12 s | B Eigenbewegung | 0.26 | 115.5 px |
| 18 | 75.83 s | 80.21 s | 4.38 s | A Standbild+Fahrt | 0.74 | 0.1 px |
| 19 | 80.21 s | 85.46 s | 5.25 s | B Eigenbewegung | 0.32 | 147.1 px |
| 20 | 85.46 s | 89.33 s | 3.88 s | B Eigenbewegung | 0.11 | 80.4 px |
| 21 | 89.33 s | 93.79 s | 4.46 s | A Standbild+Fahrt | 0.68 | 1.0 px |

Histogramm (1-s-Klassen): 2-3s: 2 · 3-4s: 8 · 4-5s: 3 · 5-6s: 6 · 6-7s: 1 · 9-10s: 1

#### short_XIX (helles Register, 57,0 s) — 16 Shots, Median 3.73 s, Mittel 3.56 s

| Shot | Start | Ende | Dauer | Bewegungsurteil | Inlier | Restfehler |
|---|---|---|---|---|---|---|
| 1 | 0.00 s | 3.67 s | 3.67 s | B Eigenbewegung | 0.20 | 155.2 px |
| 2 | 3.67 s | 8.42 s | 4.75 s | B Eigenbewegung | 0.26 | 37.9 px |
| 3 | 8.42 s | 11.21 s | 2.79 s | B Eigenbewegung | 0.21 | 169.1 px |
| 4 | 11.21 s | 14.54 s | 3.33 s | B Eigenbewegung | 0.31 | 41.9 px |
| 5 | 14.54 s | 16.33 s | 1.79 s | B Eigenbewegung | 0.21 | 202.5 px |
| 6 | 16.33 s | 20.12 s | 3.79 s | B Eigenbewegung | 0.10 | 287.0 px |
| 7 | 20.12 s | 24.67 s | 4.54 s | A Standbild+Fahrt | 0.65 | 2.3 px |
| 8 | 24.67 s | 29.92 s | 5.25 s | B Eigenbewegung | 0.30 | 33.7 px |
| 9 | 29.92 s | 32.46 s | 2.54 s | A Standbild+Fahrt | 0.99 | 0.0 px |
| 10 | 32.46 s | 35.17 s | 2.71 s | A Standbild+Fahrt | 0.62 | 1.8 px |
| 11 | 35.17 s | 38.50 s | 3.33 s | A Standbild+Fahrt | 0.61 | 1.9 px |
| 12 | 38.50 s | 42.50 s | 4.00 s | A Standbild+Fahrt | 0.66 | 1.5 px |
| 13 | 42.50 s | 44.29 s | 1.79 s | A Standbild+Fahrt | 1.00 | 0.0 px |
| 14 | 44.29 s | 48.29 s | 4.00 s | A Standbild+Fahrt | 0.95 | 0.1 px |
| 15 | 48.29 s | 52.29 s | 4.00 s | B Eigenbewegung | 0.15 | 98.2 px |
| 16 | 52.29 s | 57.00 s | 4.71 s | B Eigenbewegung | 0.32 | 6.0 px |

Histogramm (1-s-Klassen): 1-2s: 2 · 2-3s: 3 · 3-4s: 4 · 4-5s: 6 · 5-6s: 1


---

## 4. Messtabelle A3 — Referenz für die Abnahme

**Verfahren:** mittlerer Frame je Shot (nicht der erste — dort sitzt Bewegungsunschärfe), Untertitelband **y 1460–1570 entfernt** (nicht geschwärzt, das hätte künstliche Schwarzpixel eingeschleust), alle Bilder auf **2,0 Megapixel normiert** (Laplace-Varianz und Kantendichte hängen direkt an der Auflösung — ohne Normierung wäre der Vergleich mit den 2752×1536-Kandidaten wertlos).

**Untertitel-Nachweis:** Die gelben Pixel konzentrieren sich auf y 1479–1547 (237–245 Pixel/Zeile, außerhalb praktisch null). Vor der Maskierung stand `#D1BB5B` mit 4,9 % in der Palette — **nach der Maskierung ist es verschwunden.** Das bestätigt, dass es der eingebrannte Untertitel war und nicht Bildinhalt.

### Dunkles Register (short_B, n=21) — die Ankerreferenz

**Palette (k-means k=6 über alle Frames):**

| Rolle | Hex | Gewicht |
|---|---|---|
| Grundton (Schwarzgrund) | `#101313` | 68.6 % |
| Schattenton (kaltes Grau) | `#353737` | 18.7 % |
| warmer Akzent (Glutrot, dunkel) | `#773A30` | 5.2 % |
| warmer Akzent (Ember, hell) | `#C74C38` | 3.4 % |
| Himmels-/Sandton | `#BC9D7B` | 3.0 % |
| Lichtspitze | `#D4E6DF` | 1.0 % |

| Größe | Median | P10 | P90 | Min | Max |
|---|---|---|---|---|---|
| Helligkeit Median | **10.98** | 7.06 | 18.82 | 5.88 | 22.35 |
| Helligkeit P10 | **4.31** | 0.78 | 8.24 | 0.00 | 9.80 |
| Helligkeit P90 | **38.43** | 19.61 | 72.55 | 14.90 | 94.12 |
| Sättigung Median | **47.84** | 31.37 | 76.47 | 28.63 | 78.43 |
| Kontrastumfang | **53.33** | 24.31 | 89.41 | 17.25 | 96.08 |
| Laplace-Varianz | **182.95** | 31.88 | 619.25 | 23.33 | 679.72 |
| Kantendichte oben | **0.02** | 0.01 | 0.07 | 0.01 | 0.10 |
| Kantendichte unten | **0.03** | 0.01 | 0.08 | 0.01 | 0.12 |

### Helles Register (short_XIX, n=16) — nur zur Abgrenzung, NICHT Ankerbasis

| Größe | Median | Spanne |
|---|---|---|
| Helligkeit Median | 27.84 | 0.00 – 72.94 |
| Sättigung Median | 30.79 | 0.00 – 44.31 |
| Kontrastumfang | 70.39 | 0.00 – 92.94 |
| Laplace-Varianz | 617.19 | 246.03 – 3131.91 |

Palette hell: `#191815` 38%  `#403E38` 28%  `#765D44` 13%  `#7D827E` 9%  `#CAA877` 7%  `#DDDAC3` 5%

**Kantendichte unten > oben** in beiden Registern (0,03 vs 0,02 bzw. 0,14 vs 0,08) — die untere Bildhälfte trägt konsistent mehr Detail. Das ist eine Kompositionsregel, keine Zufälligkeit (§8d).

---

## 5. Bewegung (A4) und Mehrfachverwendung (A5)

### 5.1 Die A/B-Trennung ist jetzt gemessen

In der Vorsitzung scheiterte genau diese Frage: dasselbe Material ergab dreimal **90,6 % / 37,5 % / 0 %**. Mit ORB-Homographie ist sie eindeutig.

**Verfahren:** erster und letzter Frame je Shot, ORB (2000 Features) + RANSAC-Homographie. Erklärt die Homographie die Differenz (hohe Inlier-Quote, kleiner Restfehler), war es eine reine Kamerafahrt über ein Standbild. Erklärt sie sie nicht, hat sich Bildinhalt eigenständig bewegt.

**Das Ergebnis ist sauber bimodal** — der Restfehler ist entweder ~1 px oder >30 px, dazwischen liegt fast nichts:

| Urteil | Kriterium | Shots | Anteil |
|---|---|---|---|
| **A — Standbild mit Kamerafahrt** | Inlier ≥ 0,6 und Restfehler ≤ 4 px | **15** | **40,5 %** |
| **B — echte Eigenbewegung** | Inlier < 0,5 | **21** | **56,8 %** |
| Grenzfall | dazwischen | 1 | 2,7 % |

**Alle 37 Shots hatten 200 Matches** (die gesetzte Obergrenze) — es gab keine Detektionsausfälle, die niedrigen Inlier-Quoten sind echt.

**Unabhängige Gegenprobe per optischem Fluss** (Farnebäck, berührt die Homographie nicht):
Klasse A Median **1,88 px** · Klasse B Median **5,01 px** · **Faktor 2,66**. Zwei Verfahren, ein Ergebnis.

### 5.2 Kamerabewegung — die Vorgabe für die Bild-zu-Video-Stufe

Über die 15 sauber vermessenen A-Shots:

| Größe | Median | P10 | P90 |
|---|---|---|---|
| Zoomfaktor über den ganzen Shot | 0,9975 | 0,9555 | 1,0767 |
| **Zoomrate pro Sekunde** | **−0,07 %/s** | −1,44 %/s | +2,31 %/s |
| Restfehler nach Transformation | 1,0 px | — | 1,4 px |

**Die Kamera bewegt sich extrem langsam** — im Median praktisch stillstehend, im Randbereich ±1,5 bis 2,3 % Zoom pro Sekunde. Kein Sprung, kein schneller Push-in.

### 5.3 Mehrfachverwendung (A5) — die Kennzahl, die der Kostenanalyse fehlte

**Verfahren:** pHash + dHash über alle Shot-Frames für Dubletten, zusätzlich ORB+Homographie mit Skalenanteil für Ausschnitte.

| Datei | Laufzeit | einzigartige Sekunden | **Verhältnis** | Dubletten | Ausschnitte |
|---|---|---|---|---|---|
| short_B | 93,8 s | 93,8 s | **1,00** | 0 | 0 |
| short_XIX | 57,0 s | 57,0 s | **1,00** | 0 | 0 |

**Null Mehrfachverwendung.** Kein einziger Shot ist Dublette oder Ausschnitt eines anderen. Storikon generiert jede Einstellung frisch.

**Was das für die Kostenrechnung bedeutet:** Die Vorsitzung führte `rho` (Zweitverwendung) als offenen Parameter und rechnete eine Sparvariante V3 mit rho = 0,25 / 0,50 durch. **Diese Variante bildet nicht ab, wie Storikon arbeitet** — dort ist rho = 0. Die 25-€-Marke war in der Vorsitzung nur über V3 erreichbar; nach dieser Messung ist V3 kein Nachbau von Storikon, sondern eine eigene, sparsamere Machart.
**Einschränkung:** gemessen an 94 s und 57 s. In einer 12-Minuten-Folge ist Wiederverwendung wahrscheinlicher als in einem Short. Auf die Langform ist rho = 0 **nicht** übertragbar.

---

## 6. Stilmerkmale — von BEIDEN Durchgängen bestätigt

**Zum Verfahren, offen gesagt:** Der Auftrag verlangt zwei unabhängige Durchgänge, weil in der Vorsitzung dieselbe Frage dreimal verschieden beantwortet wurde. Echte Unabhängigkeit kann ich nicht herstellen — meine erste Notiz steht in meinem Kontext, ich kann mich nicht blind stellen. Ich habe die Regel deshalb anders erfüllt: **Durchgang 2 lief über bisher ungesehene Frames desselben Registers.** Das ist keine Wiederholung, sondern eine Replikation an neuem Material — belastbarer als zweimal dieselben Bilder. Wo eine Aussage zusätzlich maschinell prüfbar war, steht die Messung dabei.

Gilt für das **dunkle Register**:

| Merkmal | Befund | maschinelle Stütze |
|---|---|---|
| **Pinselduktus** | Locker, sichtbare breite Striche, besonders in Fels, Wolken und Vordergrundmassen. Kein Impasto, keine Tuschekontur. | Laplace 183 bei 2 MP — mittlerer Detailgrad, kein Glattrendering |
| **Lichtführung** | **Eine** dominante warme Quelle im Bild (Feuer, Laterne, Sonnenuntergang), oft hinter oder seitlich der Figur. Kantenharte Lichtsäume auf Silhouetten, weicher Abfall in die Fläche. | Kontrastumfang 53,3 bei Helligkeitsmedian 11,0 |
| **Schattenverhalten** | **Absaufend.** Figuren werden regelmäßig zur reinen Silhouette ohne Binnenzeichnung. | Helligkeit P10 = 4,31 — das untere Zehntel liegt fast bei Schwarz |
| **Farbtemperatur-Kontrast** | Durchgehend warm gegen kalt: oranges Licht gegen türkis-grüne Schattenzone. Das ist das stärkste Einzelmerkmal. | Palette: `#C74C38`/`#773A30` warm gegen `#101313`/`#353737` kalt |
| **Detailgrad** | Vordergrund und Mittelgrund tragen das Detail, der Hintergrund läuft in Dunst aus. | Kantendichte unten 0,03 > oben 0,02 |
| **Komposition** | Weite Totalen, Figur klein bis mittel, häufig von halbhinten. Horizont meist im oberen Drittel. Kein Blickkontakt. | — |
| **Atmosphäre** | Dunst, Rauch, Staub in fast jedem Außenshot; Lichtstrahlen selten, Tiefenstaffelung über Dunstschichten statt über Schärfe. | — |
| **Gesichter und Hände** | Gesichter vereinfacht, wenige Züge, oft im Schatten. Hände kaum ausgearbeitet, meist Silhouette. | — |

---

## 7. Nicht stabil festgestellt

| Punkt | Warum offen |
|---|---|
| **Ein einheitlicher Kanalstil** | Es gibt zwei Register (§0). Alles in §6 gilt **nur** für das dunkle. |
| **Pinselduktus des hellen Registers** | Dort *ligne claire* mit harten Tuschekonturen — das genaue Gegenteil von §6. Nicht zusammenführbar. |
| **Detailgefälle Vordergrund/Hintergrund** | Im Nahbereich klar, in weiten Landschaftstotalen trägt der Hintergrund oft ebenso viel Detail. Kein einheitliches Muster. |
| **Übertragbarkeit auf 16:9** | Nur 9:16-Material vorhanden. Ob Kantendichte-Verteilung und Kompositionsregeln im Querformat gleich bleiben, ist ungeprüft. |
| **Ob 40,5 % Standbild-Anteil für die Langform gilt** | Gemessen an Shorts. Die Langform kann anders liegen. |

---

## 8. Baukasten

### a) Stil-Prompt-Baustein (in JEDEN Bildprompt kopieren)

```
Painterly digital matte painting in loose visible brushwork over a dark ground,
a single warm firelight source against deep teal-green shadow, crushed near-black
darks, figures reading as silhouettes, strong chiaroscuro, colour-dense palette of
soot black, saturated deep teal and glowing ember orange, cool atmospheric haze,
cinematic wide framing, nineteenth-century historical mood, soft edge falloff,
no ink outlines.
```
54 Wörter, nur Technik-, Licht- und Epochenbegriffe, keine Künstlernamen.

### b) Palette mit Rollen (direkt aus A3)

| Rolle | Hex | Anteil | Einsatz |
|---|---|---|---|
| **Grundton** | `#101313` | 68.6 % | — |
| **Schattenton** | `#353737` | 18.7 % | — |
| **warmer Akzent dunkel** | `#773A30` | 5.2 % | — |
| **warmer Akzent hell** | `#C74C38` | 3.4 % | — |
| **Himmels-/Sandton** | `#BC9D7B` | 3.0 % | — |
| **Lichtspitze** | `#D4E6DF` | 1.0 % | — |

Zwei Drittel der Bildfläche sind Grundton. Das ist die wichtigste Zahl der Palette: **der Look entsteht aus sehr viel Schwarz mit wenig, aber sattem Licht.**

### c) Negativliste — was der Look NICHT hat

- keine harten schwarzen Tuschekonturen (das ist das *andere* Register)
- keine flächigen, gleichmäßig ausgeleuchteten Tagszenen
- kein Fotorealismus, keine Fotoreferenz-Anmutung
- keine zweite konkurrierende Lichtquelle
- keine durchgezeichneten Schatten — Tiefen dürfen zulaufen
- keine gesättigten Buntfarben außerhalb der Warm-Kalt-Achse (kein Grün, Violett, Pink)
- keine Letterbox-Balken, kein eingebrannter Text
- keine ausgearbeiteten Gesichtsdetails in Klein- und Mittelfiguren

### d) Kompositionsregeln (prompttauglich)

- „wide establishing shot, figure small in frame, seen from a three-quarter rear angle, not looking at the viewer"
- „horizon placed in the upper third, large dark foreground mass in the lower half"
- „the single light source sits inside the frame, behind or beside the figure"
- „foreground and midground carry the detail, background dissolves into haze"

Die untere Bildhälfte trägt messbar mehr Kanten als die obere — dunkle, detailtragende Vordergrundmasse unten, Dunst und Himmel oben.

### e) Bewegungsvorgabe für die Bild-zu-Video-Stufe (aus A4)

| Vorgabe | Wert |
|---|---|
| Zoomrate | **±0 bis 2 % pro Sekunde**, Median praktisch 0 |
| Bei 4-s-Clip also | Zoomfaktor 1,00 bis 1,08 über den ganzen Clip |
| Rotation | keine |
| Anteil reiner Kamerafahrten | **40,5 %** der Shots — dort genügt ein Standbild plus Ken-Burns im Schnitt, kein Videomodell |
| Anteil echter Bewegtclips | **56,8 %** — dort bewegt sich Bildinhalt (Feuer, Rauch, Wasser, Figuren) |
| Erlaubte Eigenbewegung | subtil: Flackern, Rauch, Fahnen, Wellen. Keine großen Körperbewegungen |

### f) Suchbegriffe für midlibrary.io

`tenebrism` · `dark matte painting` · `limited palette gouache night`

**Ungeprüft** — midlibrary.io wurde nicht abgefragt. Das sind Vorschläge aus den gemessenen Merkmalen, keine verifizierten Treffer.

---

## 9. Abnahmetabelle (C2) — vollständig

**Verfahren:** Jeder Kandidat wurde heruntergeladen und mit **derselben Routine** wie A3 gemessen (gleiche 2-MP-Normierung; Maskierung entfiel, weil Kandidaten keine Untertitel haben).

**Zielwerte:** Helligkeit 10,98 · Sättigung 47,84 · Kontrast 53,33 · Laplace 182,95

| Rang | Kandidat | Modell | Runde | CIEDE2000 | Hell Δpp | Satt Δpp | Kontrast Δpp | Laplace-Verh. | Gesamt |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `k1_nb2` | nano_banana_2 | C1 | 9.55 | +5.49 | -25.49 | -2.35 | 0.966 | **2.353** |
| 2 | `k4_nb2` | nano_banana_2 | C1 | 9.13 | +4.31 | -23.92 | -15.68 | 0.855 | **3.030** |
| 3 | `k3_nb2` | nano_banana_2 | C1 | 7.61 | +3.92 | -22.74 | -5.88 | 0.458 | **3.261** |
| 4 | `c12` | nano_banana_2 | C3 | 7.74 | +1.96 | -7.45 | -25.09 | 0.391 | **3.596** |
| 5 | `c11` | nano_banana_2 | C3 | 7.49 | +1.57 | -14.51 | -23.53 | 0.419 | **3.735** |
| 6 | `c13` | nano_banana_2 | C3 | 11.49 | +1.96 | +39.22 | -24.31 | 1.043 | **4.101** |
| 7 | `k2_nb2` | nano_banana_2 | C1 | 7.28 | +0.78 | -32.94 | -9.41 | 0.270 | **4.531** |
| 8 | `k8_sd45` | seedream_v4_5 | C1 | 9.54 | +3.92 | -29.80 | +1.18 | 0.215 | **4.599** |
| 9 | `k7_sd45` | seedream_v4_5 | C1 | 8.58 | +3.92 | -30.19 | +14.92 | 0.302 | **4.751** |
| 10 | `c14` | nano_banana_2 | C3 | 11.39 | +0.00 | +32.16 | -19.21 | 0.366 | **4.778** |
| 11 | `k5_sd45` | seedream_v4_5 | C1 | 9.36 | +5.88 | -26.66 | +15.69 | 0.253 | **5.018** |
| 12 | `k6_sd45` | seedream_v4_5 | C1 | 8.64 | +7.84 | -26.66 | +19.61 | 0.239 | **5.346** |

*Gesamtabweichung = normierte Summe: CIEDE2000/15 + |ΔHell|/20 + |ΔSatt|/20 + |ΔKontrast|/20 + |log₂(Laplace-Verhältnis)|. Kleiner ist besser.*

### Augenschein-Abgleich — und was die Zahlen NICHT gesehen haben

Die drei Bestplatzierten und der palettenbeste Kandidat wurden einzeln angesehen.

| Kandidat | Augenschein | Deckt sich mit der Zahl? |
|---|---|---|
| **k1_nb2** (Rang 1) | Lockerer sichtbarer Duktus, Schwarzgrund, warme Feuerinsel gegen kaltes Grau-Türkis, Figur als Silhouette, weite Totale. Trifft das dunkle Register. | **Ja** |
| **k4_nb2** (Rang 2) | Ebenfalls sauber, stärkere Tiefenstaffelung, etwas glatter durchgerendert. Guter zweiter Platz. | **Ja** |
| **k3_nb2** (Rang 3) | **Eingebrannte Letterbox-Balken oben und unten.** Für einen Anker unbrauchbar. | **Nein** |
| **k2_nb2** (Rang 7, bester CIEDE2000 = 7,28) | **Ebenfalls Letterbox-Balken.** | **Nein — und die Zahl war irreführend** |

**Der wichtigste Befund dieser Prüfung:** Die schwarzen Balken haben den Palettenwert **künstlich verbessert**. Storikons Palette besteht zu 69 % aus Fast-Schwarz — ein Bild mit schwarzen Balken bekommt dadurch einen besseren CIEDE2000-Wert, ohne dem Stil näher zu sein. `k2_nb2` hat deshalb den besten Palettenwert der ganzen Tabelle und ist trotzdem als Anker untauglich. **Genau der Fall, vor dem der Auftrag warnt.** Die Rangfolge an der Spitze bleibt davon unberührt, in der Tabellenmitte ist sie verzerrt.

**Modellvergleich:** Alle vier `seedream_v4_5`-Kandidaten landen auf den Plätzen 8, 9, 11, 12 — ihr Laplace-Verhältnis liegt bei 0,22–0,30, sie rendern deutlich glatter als Storikon. **`nano_banana_2` ist für diesen Look das klar bessere Modell.**

---

## 10. C3 — was geändert wurde und ob es gewirkt hat

**Die formale Auslöseschwelle war NICHT gerissen:** bester CIEDE2000 9,55 (Grenze 15), Helligkeitsabweichung +5,49 pp (Grenze 20). Nach dem Wortlaut hätte C3 entfallen können.

**Ich habe die Runde trotzdem gefahren** — wegen eines systematischen Befunds, den die Auslöseschwelle nicht abdeckt: **alle acht Kandidaten lagen 22,7 bis 32,9 Prozentpunkte unter der Zielsättigung.** Das ist kein Ausreißer, das ist ein Fehler im Stil-Baustein. Kosten: 8 Credits von 150.

**Geändert wurde gezielt die abweichende Größe**, nichts sonst:

| vorher | nachher |
|---|---|
| `muted earth palette of soot black, ash grey, ember orange and pale sand` | `COLOUR-DENSE palette of soot black, saturated deep teal and intense glowing ember orange, rich chromatic contrast, not washed out, not desaturated` |
| — | ergänzt: `Full-bleed frame, no letterbox bars, no black borders` (gegen den in C2 gefundenen Balken-Defekt) |

**Wirkung — gemischt:**

| Größe (Median je Runde) | C1 | C3 | Urteil |
|---|---|---|---|
| Sättigungsabweichung | **−26,66 pp** | **+12,35 pp** | Ziel getroffen, teils überschossen |
| CIEDE2000 | 8,89 | 9,57 | leicht schlechter |
| Kontrastabweichung | ~−6 pp | ~−24 pp | **deutlich schlechter** |
| Laplace-Verhältnis | 0,27–0,97 | 0,37–1,04 | uneinheitlich |
| Gesamtabweichung | 4,565 | 3,918 | im Median besser |

**Der eingebrannte Balken-Defekt trat in C3 nicht mehr auf** — der Zusatz hat gewirkt.

**Aber der Sieger hat nicht gewechselt.** `k1_nb2` aus C1 bleibt mit 2,353 vorn; der beste C3-Kandidat (`c12`) kommt auf 3,596. Die Sättigungskorrektur hat gekostet, was sie gebracht hat: zwei Kandidaten schossen über (+39,2 und +32,2 pp, jetzt zu bunt), und der Kontrast brach bei allen vier ein.

**Warum trotzdem `k1_nb2` und nicht `c12`:** Kontrast (−2,35 vs −25,09 pp) und Detailgrad (0,966 vs 0,391) sind **Struktureigenschaften** des Looks. Sättigung ist eine Gradierung, die im Schnittprogramm in zehn Sekunden nachgezogen ist. Die verbleibende Sättigungslücke von −25,5 pp ist die **bekannte Restabweichung des Ankers** und in der Elementbeschreibung vermerkt.

---

## 11. Der Anker

| | |
|---|---|
| **Name** | `stil-anker-v1` |
| **element_id** | `d9ec37ca-e7aa-49c6-bebb-3c90339bd6b1` |
| **Kategorie** | environment |
| **Quellbild** | `k1_nb2`, nano_banana_2, 2752×1536, 16:9 |
| **Bild** | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3FnulfGnhLwm9N6gYIO0RIxe7RB/hf_20260812_151817_548b9d8a-a55f-47ae-96b7-09fc05170999.png) |

**Platzhalterform im Prompt** — die Klammern kommen wörtlich in den `prompt`, das Backend ersetzt sie:

```
<<<d9ec37ca-e7aa-49c6-bebb-3c90339bd6b1>>>
```

Beispiel:
```
In the style of <<<d9ec37ca-e7aa-49c6-bebb-3c90339bd6b1>>>, a column of soldiers
crossing a frozen river at night, one lantern burning, wide establishing shot.
```

**Nutzbare Modelle** (laut Toolbeschreibung von `show_reference_elements`):
Bild — `nano_banana_2`, `nano_banana_flash`, `gpt_image_2`, `seedream_v4_5`, `seedream_v5_lite`, `cinematic_studio_2_5`
Video — Cinema Studio Video 2 / 3.0, `seedance_2_0`, `kling3_0`
**Nicht** nutzbar mit Soul V2 / Soul Cinema.

---

## 12. Credit-Verbrauch

| Posten | Menge | Einzelpreis (per `get_cost`) | Summe |
|---|---|---|---|
| C1 `nano_banana_2` 2K 16:9 | 4 | 2 cr | 8 cr |
| C1 `seedream_v4_5` basic 16:9 | 4 | 1 cr | 4 cr |
| C3 `nano_banana_2` 2K 16:9 | 4 | 2 cr | 8 cr |
| Reference Element anlegen | 1 | 0 cr (kein `get_cost`, keine Belastung) | 0 cr |
| **Summe** | | | **20 cr** |

**Grenze 150 cr — verbraucht 20 cr (13,3 %), verbleibend 130 cr.**
Kontostand vor der Aufgabe **3.211,9**, danach **3.191,9** — die Differenz von exakt 20 bestätigt die Aufstellung.

---

## 13. Grundsätzlich nicht rekonstruierbar

| Frage | Status |
|---|---|
| **Originalprompt** | Aus dem Bild nicht wiederherstellbar. Der hier gebaute Baustein ist ein **eigener** Weg zu vergleichbaren Messwerten, keine Rekonstruktion. |
| **Verwendetes Modell** | Nicht feststellbar. Kein Wasserzeichen, keine Metadaten im gerenderten Videobild. |
| **Referenzbild oder trainiertes Modell?** | **Nicht feststellbar.** Die Figurenkonsistenz wäre auf beiden Wegen erreichbar. |
| **Ob überhaupt ein KI-Bildmodell im Einsatz war** | Nicht beweisbar. Der Look ist mit einem Illustratorenteam ebenso herstellbar. |

Zu keinem dieser Punkte wird hier etwas behauptet.

---

## 14. Zwei Sätze zum Schluss

**Trifft der Anker den Stil?** Ja, mit einer benannten Lücke — gemessen an der Referenz aus 21 Shots trifft `k1_nb2` den Detailgrad nahezu exakt (Laplace-Verhältnis 0,966), den Kontrastumfang auf 2,35 Prozentpunkte und die Helligkeit auf 5,49 Prozentpunkte, liegt mit einem Palettenabstand von CIEDE2000 9,55 klar unter der Abnahmeschwelle von 15, und bleibt mit −25,5 Prozentpunkten Sättigung die eine bekannte Abweichung, die im Schnitt nachziehbar ist; der Augenschein bestätigt die Rangfolge an der Spitze.

**Was fehlt im Material?** Vor allem **16:9-Langformmaterial** — die gesamte Spezifikation beruht auf zwei Shorts, die Übertragung ins Querformat ist ungeprüft, und die Kennzahl „null Mehrfachverwendung" ist an 94 und 57 Sekunden gemessen und damit nicht auf eine Zwölf-Minuten-Folge übertragbar; außerdem fehlt **mehr Material aus dem dunklen Register allein** (die Referenz steht auf 21 Shots aus einer einzigen Datei, weshalb die Spannen breit sind), sowie mindestens eine weitere Datei je Register, um zu klären, ob es wirklich zwei feste Register gibt oder ein Kontinuum, dessen Enden hier zufällig hochgeladen wurden.

