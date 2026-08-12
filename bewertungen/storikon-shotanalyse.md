# Shot-für-Shot-Analyse: Сторикон „How the Industrial Revolution Changed the World"

**Zielvideo:** `49DUxc4j0Wo`, 12:12 (732 s) — die Medianlänge der 9 Langform-Videos.
**Analysedatum:** 12.08.2026
**Preisdaten:** übernommen aus `bewertungen/higgsfield-kosten-storikon.md` (dort per `get_cost` erhoben). **Kein Generierungsjob abgesendet, keine neue Preisabfrage nötig.**

---

## ⚠️ Vorab: Das beauftragte Messverfahren war nicht durchführbar

Schritt 1–4 setzen die Videodatei voraus (PySceneDetect, ORB/Homographie, pHash, Gesichts-Embeddings). **Die Datei ließ sich nicht beschaffen.**

Die Toolchain wurde vollständig aufgebaut und funktioniert: `yt-dlp`, `ffmpeg`, `numpy`, `opencv`, `scenedetect`, `imagehash`, Deno als JS-Runtime, der EJS-Challenge-Solver und der bgutil-PO-Token-Provider (Token-Erzeugung nachweislich erfolgreich). Die Formatauflösung lief durch (`399+251`). Am Mediendownload scheiterte es:

```
youtube.com          -> HTTP 200   (erreichbar)
*.googlevideo.com    -> CONNECT tunnel failed, 502
Proxy-Log: connect_rejected | gateway answered 502 to CONNECT (policy denial or upstream failure)
```

**`*.googlevideo.com` — der CDN-Host, auf dem die Mediendaten liegen — ist durch die Egress-Policy dieser Session gesperrt.** Die Proxy-Dokumentation (`/root/.ccr/README.md`) verlangt ausdrücklich, solche Sperren zu melden statt sie zu umgehen. Das wurde befolgt.

**Ersatzinstrument:** multimodale Videoanalyse (`NexLev:watch_youtube_video_and_ask`, Gemini). Das Modell greift serverseitig auf das Video zu und ist von der Sperre nicht betroffen. Es liefert Schnittgrenzen zuverlässig — aber **nicht** die pixelgenauen Verfahren aus Schritt 2–4. Was dadurch offen bleibt, steht in §7. Jede Zahl unten trägt ihr Verfahren.

---

## 1. Schnittliste

**Erhebungsverfahren:** Das Video wurde in Fenster zerlegt; je Fenster wurde eine vollständige Einstellungsliste (Startzeit, Dauer, Klasse, Motiv) abgefragt.

**Zuverlässigkeitsprüfung (Ersatz für die beauftragte Schwellenwert-Justage):** Fenster 1 (00:00–02:02) wurde **zweimal unabhängig** abgefragt. Beide Durchgänge ergaben **exakt 32 Shots**, die Schnittgrenzen wichen um **≤ 1 s** voneinander ab. Die Schnitterkennung ist damit belastbar. (Die im Auftrag genannten Vergleichsfenster 3,75 / 4,62 / 4,29 s stammen aus *anderen* Videos und sind auf dieses Video nicht anwendbar; die Doppelmessung tritt an ihre Stelle.)

**Abdeckung:** 00:00–08:08 = **488,2 s von 732 s (66,7 %)**. Die letzten 244 s (08:08–12:12) sind **nicht gemessen** — das Tagelimit des Analysewerkzeugs war erschöpft (§7).

**Spalte „Zweitverwendung":** durchgehend `n. e.` — die dafür nötige Bildprüfung (pHash/Homographie) war nicht möglich (§3). „Verdacht" markiert Paare, die sich allein in der **Motivbeschreibung** stark ähneln; das ist ein Hinweis, **keine** Feststellung.

| # | Start | Dauer | Klasse | Motiv | Zweitverwendung |
|---|---|---|---|---|---|
| 1 | 0:00.00 | 2.1 s | C | Warning text and logo | n. e. |
| 2 | 0:02.00 | 3.0 s | P | Windmill farm sunset | n. e. |
| 3 | 0:05.00 | 2.1 s | P | Ship harbor night | n. e. |
| 4 | 0:07.00 | 5.1 s | P | Family reading fireplace | n. e. |
| 5 | 0:12.00 | 4.0 s | P | City street harbor | Verdacht |
| 6 | 0:16.00 | 2.1 s | P | Men pulling ropes | n. e. |
| 7 | 0:18.00 | 3.0 s | P | Horse cart water wheel | n. e. |
| 8 | 0:21.00 | 4.1 s | P | Workers factory | Verdacht |
| 9 | 0:25.00 | 5.1 s | P | Horse wagons road | n. e. |
| 10 | 0:30.00 | 5.1 s | P | Rural landscape house | Verdacht |
| 11 | 0:35.00 | 2.0 s | D | Map Europe gears | n. e. |
| 12 | 0:37.00 | 3.1 s | P | Book gold coins | n. e. |
| 13 | 0:40.00 | 6.1 s | P | Men harbor gold | n. e. |
| 14 | 0:46.00 | 4.1 s | P | Miners cave | n. e. |
| 15 | 0:51.00 | 3.1 s | P | Crying miner | n. e. |
| 16 | 0:54.00 | 5.1 s | P | Water flooding mine | n. e. |
| 17 | 0:59.00 | 5.1 s | P | Horse barrels barn | n. e. |
| 18 | 1:04.00 | 5.1 s | P | Man writing desk | Verdacht |
| 19 | 1:09.00 | 4.1 s | P | Small steam engine | Verdacht |
| 20 | 1:13.00 | 3.1 s | P | Large steam engine | Verdacht |
| 21 | 1:16.00 | 6.1 s | P | Men examining machinery | n. e. |
| 22 | 1:22.00 | 4.1 s | P | Steam engines mine | n. e. |
| 23 | 1:26.00 | 4.1 s | P | Women textile mill | n. e. |
| 24 | 1:30.00 | 3.0 s | P | Train river boat | n. e. |
| 25 | 1:33.00 | 3.1 s | P | Hand mechanical device | n. e. |
| 26 | 1:37.00 | 5.1 s | P | Men technical plans | n. e. |
| 27 | 1:42.00 | 3.1 s | P | Man shoveling coal | n. e. |
| 28 | 1:45.00 | 3.1 s | P | Industrial city chimneys | Verdacht |
| 29 | 1:48.00 | 4.1 s | P | Train exiting tunnel | n. e. |
| 30 | 1:52.00 | 3.1 s | P | Modern city skyline | Verdacht |
| 31 | 1:55.00 | 3.1 s | C | Russian title text | n. e. |
| 32 | 1:58.00 | 1.4 s | P | Men dark factory | n. e. |
| 33 | 2:02.00 | 1.4 s | P | Factory interior with workers | Verdacht |
| 34 | 2:03.00 | 3.8 s | P | Workers and horses in street | n. e. |
| 35 | 2:07.00 | 2.9 s | P | Wooden machine with chains | n. e. |
| 36 | 2:10.00 | 3.0 s | P | Close-up of moving gears | n. e. |
| 37 | 2:13.00 | 4.1 s | P | Mine shaft looking upwards | n. e. |
| 38 | 2:17.00 | 3.0 s | P | Factory with spinning wheels | n. e. |
| 39 | 2:20.00 | 7.4 s | P | Industrial city skyline smoking | Verdacht |
| 40 | 2:27.00 | 4.1 s | P | Man with mustache in library | n. e. |
| 41 | 2:31.00 | 5.0 s | P | Molten metal in factory | n. e. |
| 42 | 2:36.00 | 1.9 s | P | Modern vs historical person split | n. e. |
| 43 | 2:38.00 | 4.3 s | P | City view from high window | n. e. |
| 44 | 2:42.00 | 2.1 s | P | Machine wheel with fire | n. e. |
| 45 | 2:45.00 | 6.0 s | P | Line of men in field | n. e. |
| 46 | 2:51.00 | 5.0 s | P | Industrial riverfront with chimneys | Verdacht |
| 47 | 2:56.00 | 3.0 s | P | Workers operating factory machine | Verdacht |
| 48 | 2:59.00 | 3.0 s | P | Horses pulling carriage in rain | n. e. |
| 49 | 3:02.00 | 4.1 s | P | Crowd watching massive machine wheel | n. e. |
| 50 | 3:06.00 | 3.0 s | P | Man pushing cart in mine | n. e. |
| 51 | 3:09.00 | 4.0 s | P | Two men drinking beer | n. e. |
| 52 | 3:13.00 | 5.1 s | P | Sunset over industrial city | n. e. |
| 53 | 3:18.00 | 3.0 s | C | Title card Birth of Factories | n. e. |
| 54 | 3:21.00 | 3.0 s | P | Large weaving machine operating | n. e. |
| 55 | 3:24.00 | 5.0 s | P | Blacksmith working at anvil | n. e. |
| 56 | 3:29.00 | 4.0 s | P | Man working at desk | Verdacht |
| 57 | 3:33.00 | 3.0 s | P | Close-up of hands sewing | n. e. |
| 58 | 3:36.00 | 4.0 s | P | Men examining architectural plans | n. e. |
| 59 | 3:40.00 | 2.0 s | P | Chimneys against red sky | n. e. |
| 60 | 3:42.00 | 4.0 s | P | Long factory hallway with workers | Verdacht |
| 61 | 3:46.00 | 3.0 s | P | Hands adjusting machine parts | n. e. |
| 62 | 3:49.00 | 5.0 s | P | Men at long factory workbench | n. e. |
| 63 | 3:54.00 | 4.0 s | P | Large spools of red thread | n. e. |
| 64 | 3:58.00 | 5.0 s | P | Complex spinning machine operating | n. e. |
| 65 | 4:03.00 | 1.0 s | P | Large clock face in factory | Verdacht |
| 66 | 4:04.00 | 4.0 s | P | Workers moving crates under clock | n. e. |
| 67 | 4:08.00 | 3.5 s | P | Warehouse filled with storage sacks | n. e. |
| 68 | 4:11.00 | 5.3 s | P | People browsing outdoor clothing market | n. e. |
| 69 | 4:16.00 | 3.0 s | P | Workers beside massive industrial wheels | n. e. |
| 70 | 4:19.00 | 5.2 s | P | Modern car assembly factory line | n. e. |
| 71 | 4:25.00 | 2.8 s | C | Text card about moving cities | n. e. |
| 72 | 4:27.00 | 3.7 s | P | Men standing before large building | n. e. |
| 73 | 4:31.00 | 2.5 s | P | Crowd of workers near factories | n. e. |
| 74 | 4:34.00 | 2.2 s | P | Close-up of weary worker faces | n. e. |
| 75 | 4:36.00 | 3.6 s | P | Rural houses near industrial factories | n. e. |
| 76 | 4:39.00 | 3.2 s | P | People migrating from rural village | n. e. |
| 77 | 4:43.00 | 3.8 s | P | Signpost for Manchester with wagons | n. e. |
| 78 | 4:46.00 | 5.0 s | P | Industrial city with smoking chimneys | Verdacht |
| 79 | 4:51.00 | 5.4 s | P | Large red industrial factory building | n. e. |
| 80 | 4:57.00 | 3.6 s | P | Tired workers at factory bench | Verdacht |
| 81 | 5:00.00 | 3.7 s | P | Workers operating heavy factory machinery | Verdacht |
| 82 | 5:04.00 | 0.5 s | P | Young boy working in foundry | n. e. |
| 83 | 5:05.00 | 3.6 s | P | Factory workers in foundry | Verdacht |
| 84 | 5:08.00 | 5.9 s | P | Dark city street | Verdacht |
| 85 | 5:14.00 | 4.1 s | P | Hands counting coins | n. e. |
| 86 | 5:18.00 | 2.9 s | P | Workers lifting buckets | n. e. |
| 87 | 5:21.00 | 4.0 s | P | Old city panorama | n. e. |
| 88 | 5:25.00 | 3.8 s | P | Modern city street | Verdacht |
| 89 | 5:29.00 | 2.2 s | C | Text on black background | n. e. |
| 90 | 5:31.00 | 3.0 s | P | Rural landscape and town | Verdacht |
| 91 | 5:34.00 | 4.0 s | P | Carriage on rainy road | Verdacht |
| 92 | 5:38.00 | 4.0 s | P | Man writing at desk | Verdacht |
| 93 | 5:42.00 | 7.0 s | P | Carriage on night road | Verdacht |
| 94 | 5:49.00 | 5.0 s | P | Steam engine wheels | Verdacht |
| 95 | 5:54.00 | 4.0 s | P | Hands holding globe | n. e. |
| 96 | 5:58.00 | 5.0 s | P | Train on wooden bridge | n. e. |
| 97 | 6:03.00 | 4.5 s | P | Passengers inside train | n. e. |
| 98 | 6:06.00 | 1.0 s | P | Man on train looking out | n. e. |
| 99 | 6:07.00 | 4.0 s | P | Workers building railroad tracks | n. e. |
| 100 | 6:11.00 | 8.0 s | P | Large train station interior | n. e. |
| 101 | 6:19.00 | 4.0 s | P | Two men watching train approach | n. e. |
| 102 | 6:23.00 | 4.0 s | P | Train crossing bridge at sunset | n. e. |
| 103 | 6:27.00 | 3.0 s | D | Men looking at large map | n. e. |
| 104 | 6:30.00 | 8.0 s | P | Railroad tracks through countryside | n. e. |
| 105 | 6:38.00 | 5.0 s | D | Railroad tracks encircling the globe | n. e. |
| 106 | 6:43.00 | 5.0 s | P | Workers moving large wooden crate | n. e. |
| 107 | 6:48.00 | 3.0 s | P | Close-up of train wheels moving | n. e. |
| 108 | 6:51.00 | 4.0 s | P | Train arriving at busy station | n. e. |
| 109 | 6:55.00 | 4.0 s | P | Hand writing on ledger | n. e. |
| 110 | 6:59.00 | 6.0 s | P | Large steamship on rough seas | n. e. |
| 111 | 7:05.00 | 5.0 s | P | Split screen sailboat vs steamship | n. e. |
| 112 | 7:10.00 | 5.0 s | P | Hand adjusting train controls | n. e. |
| 113 | 7:15.00 | 5.0 s | P | Row of clocks for cities | n. e. |
| 114 | 7:20.00 | 4.0 s | P | Man checking pocket watch outside | Verdacht |
| 115 | 7:24.00 | 4.0 s | P | Man checking watch in station | Verdacht |
| 116 | 7:28.00 | 3.0 s | P | Close-up of mans face | n. e. |
| 117 | 7:31.00 | 5.0 s | P | Large clock tower face | Verdacht |
| 118 | 7:36.00 | 7.0 s | P | Train moving through city night | n. e. |
| 119 | 7:43.00 | 3.0 s | C | Text Birth of modern society | n. e. |
| 120 | 7:46.00 | 5.0 s | P | Close-up of mans eyes | n. e. |
| 121 | 7:51.00 | 5.0 s | P | Large crowd in industrial city | Verdacht |
| 122 | 7:56.00 | 3.0 s | P | Interior of glass-roofed station | n. e. |
| 123 | 7:59.00 | 5.0 s | P | Rural house in vast fields | n. e. |
| 124 | 8:04.00 | 3.0 s | P | Man kneeling with shovel | n. e. |
| 125 | 8:07.00 | 1.0 s | P | Family sitting at dinner table | n. e. |


### 1.1 Kennzahlen der Schnittliste (gemessene 488,2 s)

| Größe | Wert |
|---|---|
| Shots gemessen | **125** |
| Messspanne | 488,2 s (66,7 % von 732 s) |
| **Median-Shotlänge** | **4,00 s** |
| **Mittelwert-Shotlänge** | **3,91 s** |
| Kürzester / längster Shot | 0,5 s / 8,0 s |
| Schnittdichte | 0,256 Shots/s |

**Histogramm der Shotlängen (1-Sekunden-Klassen, n=125):**

| Klasse | Anzahl | |
|---|---|---|
| 0–1 s | 1 | █ |
| 1–2 s | 6 | ██████ |
| 2–3 s | 12 | ████████████ |
| 3–4 s | 38 | ██████████████████████████████████████ |
| 4–5 s | 30 | ██████████████████████████████ |
| 5–6 s | 29 | █████████████████████████████ |
| 6–7 s | 4 | ████ |
| 7–8 s | 3 | ███ |
| 8–9 s | 2 | ██ |

Der Schwerpunkt liegt eng zwischen 3 und 6 s (97 von 125 Shots = 78 %). Das ist für die Kostenrechnung wichtig: fast jeder Shot fällt in ein Dauerraster, das die Videomodelle direkt bedienen können.

---

## 2. Verteilung nach Klasse

**⚠️ Die im Auftrag verlangte Trennung A (Standbild mit Kamerafahrt) / B (echt generierter Bewegtclip) ist NICHT GEMESSEN — sie ist am Instrument gescheitert.** Drei unabhängige Durchgänge über dieselben Shots ergaben:

| Durchgang | Prompt-Variante | Anteil „bewegt" |
|---|---|---|
| 1 | A/B-Klassifikation, offen | **90,6 %** (29 von 32) |
| 2 | A/B-Klassifikation, „eingefrorenes Gemälde = A" betont | **37,5 %** (12 von 32) |
| 3 | Forensisch, mit Zwang zur Benennung des bewegten Elements | **0 %** (0 von 20) |

Durchgang 3 lieferte für alle 20 Shots dieselbe Antwort ohne ein einziges benanntes Element — das liest sich als Pauschalantwort, nicht als Einzelfallurteil. **Drei Durchgänge, drei unvereinbare Ergebnisse: die A/B-Quote wird deshalb nicht behauptet, sondern in §5 als offener Parameter `b` geführt.**

Was das Instrument **zuverlässig** trennen kann (visuell eindeutige Kategorien):

| Klasse | Shots | Anteil Shots | Sekunden | Anteil Sekunden |
|---|---|---|---|---|
| **P** — bildliche Szene (Gemäldestil; A **oder** B, ungetrennt) | 116 | 92,8 % | 462,0 s | 94,6 % |
| **C** — Titelkarte / Texttafel | 6 | 4,8 % | 16,2 s | 3,3 % |
| **D** — Karte / Diagramm | 3 | 2,4 % | 10,0 s | 2,0 % |
| **E** — fotorealistisches Archiv-/Stockmaterial | **0** | 0 % | 0 s | 0 % |

**Zwei belastbare Befunde:** Der Kanal verwendet **kein** Archiv- oder Stockmaterial (E=0) — alles ist erzeugt. Und **94,6 % der Laufzeit sind bildliche Szenen**; Titelkarten und Karten zusammen kosten nur 5,4 % der Laufzeit.

**Hochrechnung auf die volle Laufzeit** (Annahme: gleiche Schnittdichte im ungemessenen Drittel — §6):
**≈ 187 Shots**, davon ≈ 174 P, ≈ 9 C, ≈ 4 D.

---

## 3. Kennzahl „einzigartige generierte Sekunden : Laufzeit" — NICHT ERMITTELT

Der Auftrag nennt dies „die zentrale Kennzahl der ganzen Analyse". **Sie konnte nicht gemessen werden.** Beide vorgesehenen Verfahren setzen die Videodatei voraus:

- **3a Perceptual Hashing** über Keyframes — Keyframe-Extraktion unmöglich (kein Videofile).
- **3b Ausschnitt-Erkennung** per Feature-Matching + Homographie mit Skalierungsanteil — dito.

Ein Ersatz über das multimodale Modell scheiterte am Tagelimit (§7), und wäre für diese Frage ohnehin schwach: Das Instrument hat schon bei der einfacheren A/B-Frage dreimal widersprüchlich geantwortet.

**Was stattdessen vorliegt — ausdrücklich KEINE Messung:** Ein Textvergleich der 125 Motivbeschreibungen findet **25 Kandidatenpaare** über **30 der 125 Shots**, z. B. „Man writing desk" (1:04) ↔ „Man working at desk" (3:29) ↔ „Man writing at desk" (5:38), oder „Carriage on rainy road" (5:34) ↔ „Carriage on night road" (5:42). Ob es sich um dasselbe Ausgangsmaterial, um Ausschnitte davon oder schlicht um ähnliche Motive handelt, **ist damit nicht entschieden**. Die Zahl taugt als Recherchehinweis, nicht als Kostenfaktor.

**Konsequenz für die Rechnung:** Die Zweitverwendung wird in §5 als offener Parameter `rho` geführt, nicht als Messwert.

---

## 4. Wiederkehrende Figuren — NICHT ERMITTELT

Das beauftragte Verfahren (Gesichtserkennung über alle Keyframes, Clustern der Embeddings) setzt die Videodatei voraus und war nicht durchführbar. Das Tagelimit des Ersatzinstruments war erschöpft, bevor diese Frage gestellt werden konnte.

**Es wird deshalb keine Figurenzahl behauptet.** In §5 stehen die Figuren-Einmalkosten mit **0 Credits** in der Rechnung — nicht weil sie null wären, sondern weil sie unbekannt sind. Das Vorgängerdokument hält zusätzlich fest, dass für beide Konsistenzwege (`show_reference_elements`, `show_characters`) **kein `get_cost` existiert**, die Einmalkosten je Figur also auch preislich nicht ermittelbar sind. Der dort genannte Tooltip-Anhaltspunkt (~30 cr/Figur) würde bei 3 Figuren ≈ 90 cr bedeuten — das ist gegenüber den Spannen unten klein, aber es bleibt unbelegt.

**Hinweis aus der Motivliste:** Die Beschreibungen deuten auf eine Erzählweise ohne durchgehende Hauptfigur hin (überwiegend „Workers…", „Men…", „Crowd…", anonyme Rollen). Wenn sich das bestätigt, wäre der Bedarf an Reference Elements gering. **Das ist eine Beobachtung an Textlabels, keine Messung.**

---

## 5. Kostenrechnung

### 5.1 Rechenweg

Statt pauschal „Sekunden × Sekundenpreis" wird **die gemessene Dauerverteilung gegen das Dauerraster der Modelle** gerechnet (`models_explore`): jeder Shot wird auf die kleinste zulässige Clipdauer ≥ Shotdauer aufgerundet.

| Modell | zulässige Dauern | mittlere **abgerechnete** Dauer je P-Shot | Quantisierungsverlust |
|---|---|---|---|
| `veo3_1_lite` | 4 / 6 / 8 s | **4,97 s** | **+25 %** |
| `kling3_0_turbo` | ganzzahlig 3–15 s | **4,41 s** | **+11 %** |

Mittlere echte P-Shotdauer: 3,98 s. **Das grobe 4/6/8-Raster von Veo frisst ein Viertel der bezahlten Clipzeit** — ein Effekt, den eine reine Sekundenrechnung verschluckt.

```
kosten = ((1-rho) * n_P + n_D) * bildpreis * ausschuss_bild
       + b * (1-rho) * n_P * mittl_abger_dauer * sekundenpreis * ausschuss_clip
       + voiceover (72 cr)
       + figuren_einmalkosten (0 - NICHT ERMITTELT, §4)

n_P = 174 (hochgerechnet)   n_D = 4    n_C = 9 (kostenlos, im Schnittprogramm gebaut - Annahme)
b   = Anteil echt animierter P-Shots        NICHT GEMESSEN (§2)
rho = Anteil Shots aus Zweitverwendung      NICHT GEMESSEN (§3)
```

Spannen: unten = Ausschuss 1,0/1,0, oben = Ausschuss_bild 2,0 / Ausschuss_clip 3,0.

### 5.2 V1 „Storikon 1:1" — nur als Funktion von `b` darstellbar

Weil die A/B-Quote nicht gemessen ist, hat V1 **keinen Einzelwert**. Die Bandbreite über `b` ist größer als die über den Ausschuss:

| Kombination | b=0,25 | b=0,50 | b=0,75 | b=1,00 |
|---|---|---|---|---|
| **A** veo3_1_lite + seedream_v5_lite | 466–1077 cr | 682–1724 cr | 898–2372 cr | 1114–3020 cr |
| **B** kling3_0_turbo + nano_banana_2 | 628–1471 cr | 915–2335 cr | 1203–3198 cr | 1491–4062 cr |

**Gesamtunsicherheit V1: 466 bis 4062 Credits** — Faktor 8.7 zwischen bester und schlechtester Ecke. Davon geht Faktor 2.4 auf `b` (ungemessen) und Faktor 3 auf den Ausschuss (ungemessen).

### 5.3 V2 „eigene Fassung" (b=0,50) und V3 „sparsam" (b=0,50 + Zweitverwendung)

`b=0,50` ist hier **Vorgabe des Auftrags**, keine Messung. `rho` ist ebenfalls ungemessen — V3 wird deshalb in zwei Stufen gezeigt.

| Kombination | V2 (rho=0) | V3 rho=0,25 | V3 rho=0,50 |
|---|---|---|---|
| **A** veo3_1_lite + seedream_v5_lite | 682–1724 cr | 531–1313 cr | 379–903 cr |
| **B** kling3_0_turbo + nano_banana_2 | 915–2335 cr | 706–1772 cr | 497–1210 cr |

*V2 ist rechnerisch identisch mit V1 bei b=0,50 — die Vorgabe „50 % generiert" trifft genau die Mitte des offenen V1-Korridors.*

### 5.4 Euro — alle drei Kurse nebeneinander

Der Kurs ist mehrdeutig (`monthly_final_price_cents` stand auf 0). Es wird **nicht** behauptet, welcher gilt.

| Variante / Kombination | Credits | @ 0,0475 €/cr | @ 0,0330 €/cr | @ 0,00275 €/cr |
|---|---|---|---|---|
| V1 b=1,00 (A) | 1114–3020 | 53–143 € | 37–100 € | 3,06–8,30 € |
| V1 b=1,00 (B) | 1491–4062 | 71–193 € | 49–134 € | 4,10–11,17 € |
| V2 b=0,50 (A) | 682–1724 | 32–82 € | 23–57 € | 1,88–4,74 € |
| V2 b=0,50 (B) | 915–2335 | 43–111 € | 30–77 € | 2,52–6,42 € |
| V3 rho=0,50 (A) | 379–903 | 18–43 € | 13–30 € | 1,04–2,48 € |
| V3 rho=0,50 (B) | 497–1210 | 24–57 € | 16–40 € | 1,37–3,33 € |

---

## 6. Gemessen vs. angenommen

### Gemessen (mit Verfahren)

| Zahl | Wert | Verfahren |
|---|---|---|
| Shotzahl (Messspanne) | 125 | Multimodale Einstellungsliste, 5 Fenster; Fenster 1 doppelt erhoben, beide 32 Shots, Grenzen ≤1 s Abweichung |
| Messspanne | 488,2 s von 732 s | Summe der erhobenen Shotdauern |
| Median-Shotlänge | 4,00 s | Median über 125 Shotdauern |
| Mittelwert-Shotlänge | 3,91 s | Mittel über 125 Shotdauern |
| Histogramm | siehe §1.1 | 1-s-Klassierung derselben 125 Werte |
| Klassenverteilung P/C/D/E | 116/6/3/**0** | Multimodale Klassifikation, auf visuell eindeutige Klassen beschränkt |
| Anteil bildlicher Szenen | 94,6 % der Sekunden | aus Klassenverteilung |
| Kein Stock-/Archivmaterial | E = 0 | Klassifikation über alle 125 Shots |
| Zulässige Clipdauern | 4/6/8 bzw. 3–15 s | `models_explore(action:'get')`, Vorgängerdokument |
| Abgerechnete Dauer je P-Shot | 4,97 s / 4,41 s | gemessene Dauerverteilung gegen das Dauerraster gerechnet |
| Sekunden- und Bildpreise | 1,0/1,5 cr/s; 1,0/1,5 cr | `get_cost`, Vorgängerdokument |
| Voiceover | 72 cr | `get_cost` bei 2000 Zeichen × 6 Blöcke, Vorgängerdokument |

### Angenommen (ausdrücklich nicht gemessen)

| Annahme | Gesetzt auf | Warum offen |
|---|---|---|
| **`b` — Anteil echt animierter Shots** | Parameter 0,25–1,00 | Instrument lieferte 90,6 % / 37,5 % / 0 % (§2) |
| **`rho` — Zweitverwendung** | Parameter 0 / 0,25 / 0,50 | pHash + Homographie nicht durchführbar (§3) |
| **Ausschuss Bild / Clip** | 1,0–2,0 / 1,0–3,0 | nirgends messbar; **größter einzelner Hebel neben `b`** |
| Hochrechnung 125 → 187 Shots | Faktor 1,499 | letztes Drittel ungemessen; unterstellt gleiche Schnittdichte |
| `b` gleichverteilt über Shotdauern | ja | unbekannt, ob lange Shots eher animiert sind |
| Titelkarten (C) kosten 0 | ja | im Schnittprogramm baubar, kein Higgsfield-Posten |
| Karten/Diagramme (D) = 1 Bild | ja | Animation darüber im Schnittprogramm |
| Figuren-Einmalkosten | 0 cr | Figurenzahl unbekannt (§4) **und** kein `get_cost` vorhanden |

---

## 7. Nicht ermittelt / gescheitert

| # | Vorhaben | Ergebnis |
|---|---|---|
| 1 | **Videodownload** (`yt-dlp`, ≤1080p) | **Gescheitert.** `*.googlevideo.com` durch Egress-Policy gesperrt: `connect_rejected — gateway answered 502 to CONNECT (policy denial)`. `youtube.com` selbst liefert HTTP 200. Toolchain (Deno, EJS-Solver, bgutil-PO-Token, Formatauflösung `399+251`) lief; nur der Mediendownload ist gesperrt. Nicht umgangen — die Proxy-Dokumentation verlangt Meldung statt Umgehung. |
| 2 | **Schritt 1** PySceneDetect / ffmpeg-Scene-Filter | Nicht durchführbar (keine Datei). Ersetzt durch multimodale Einstellungsliste; Schwellenwert-Justage entfällt, stattdessen Doppelmessung (§1). |
| 3 | **Schritt 2** ORB/SIFT + Homographie für A/B | Nicht durchführbar (keine Datei). Ersatzmessung **fehlgeschlagen**: 3 Durchgänge → 90,6 % / 37,5 % / 0 %. Als Parameter `b` geführt. |
| 4 | **Schritt 3a** pHash/dHash über Keyframes | Nicht durchführbar (keine Datei). |
| 5 | **Schritt 3b** Ausschnitt-Erkennung per Homographie mit Skalierung | Nicht durchführbar (keine Datei). |
| 6 | **Schritt 3c** Kennzahl einzigartige generierte Sekunden : Laufzeit | **Nicht ermittelt** — Folge von 4 und 5. Als Parameter `rho` geführt. |
| 7 | **Schritt 4** Gesichtserkennung + Embedding-Clustering | Nicht durchführbar (keine Datei); Ersatzabfrage am Tagelimit gescheitert. Keine Figurenzahl behauptet. |
| 8 | **Fenster 08:08–12:12** (244 s, letztes Drittel) | **Nicht gemessen.** `RATE LIMIT EXCEEDED: 15/15 calls in the last 24 hours` (NexLev PRO). |
| 9 | Fenster 04:04–06:06, erster Durchgang | Antwort brach nach 60,5 s von 122 s ab; in zwei Hälften nacherhoben. |
| 10 | Figuren-Einmalkosten in Credits | **Nicht ermittelt** — `show_reference_elements(create)` und `show_characters(train)` haben keinen `get_cost`-Parameter (Vorgängerdokument §5/§7). |

---

## 8. Was ich vom Nutzer brauche

**Eine Frage — sie schließt den Euro-Teil ab:**

> **Welchen Betrag zahlst du pro Abrechnungszeitraum für Higgsfield, und wie viele Credits enthält dieser Zeitraum?**
> Also z. B.: „99 € pro Jahr, darin 3.000 Credits pro Monat" oder „99 € pro Monat, darin 3.000 Credits".

Daraus fällt der Kurs (0,0475 / 0,0330 / 0,00275 €/cr — Faktor 12 dazwischen), und §5.4 reduziert sich auf eine Spalte.

**Zwei Dinge, die eine Antwort allein nicht heilt** — sie brauchen die Videodatei, nicht dich:
Freigabe von `*.googlevideo.com` in der Egress-Policy (oder ein lokaler Lauf der Toolchain, die in dieser Session fertig aufgebaut wurde) würde `b` und `rho` messbar machen. Beide zusammen bestimmen die Kosten stärker als die Modellwahl.

---

## 9. Ist eine Folge dieser Machart für 25 € produzierbar?

25 € entsprechen **526 cr** (@0,0475), **758 cr** (@0,0330) oder **9.091 cr** (@0,00275).

| Variante (Kombination A) | Credits | 526 cr | 758 cr | 9.091 cr |
|---|---|---|---|---|
| V1 b=1,00 | 1114–3020 | nein | nein | ja, ganz |
| V2 b=0,50 | 682–1724 | nein | ja, nur unten | ja, ganz |
| V3 rho=0,50 | 379–903 | ja, nur unten | ja, nur unten | ja, ganz |

> **Antwort in einem Satz: Ja, aber nur unter drei Bedingungen gleichzeitig — beim günstigsten Kurs (Abo-Jahreslesart) reicht es für jede Variante mühelos, beim Top-up-Kurs von 0,0475 €/cr dagegen nur für V3 mit konsequenter Zweitverwendung UND niedrigem Ausschuss (379 cr = 18 €), während V2 selbst im besten Fall bei 682 cr = 32 € landet und die 25 € überschreitet; eine 1:1-Kopie der Storikon-Machart (V1) verfehlt das Ziel beim Top-up-Kurs in jeder Ausschuss-Lage.**

Die Antwort steht ausdrücklich unter dem Vorbehalt, dass **`b`, `rho` und der Ausschussfaktor allesamt ungemessen** sind (§6) und die Rechnung auf dem gemessenen Zweidrittel des Videos beruht.

