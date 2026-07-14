# Konkurrenz-Muster — Was die schnellsten Space-KI-Kanäle richtig machen

Stand: 14.07.2026. **Datenbasis: eigene Scrapes** (Video-für-Video: Titel, Views, Dauer) über
17 Space-Kanäle — 5 Deep-Dives (`analyse/space/`, inkl. Watch-Seiten) + 13 Light-Scrapes
(about/videos/RSS, je ~30 jüngste Videos). Kanäle ohne auflösbares Handle (CosmicLens,
Acronium, beyonddiscovery) verworfen. Ergänzt um Web-Recherche (Cool Worlds/Columbia,
Slop-Crackdown 2026). Alle Kanäle sind KI-produziert/faceless oder mit unserer Pipeline
(Higgsfield + NASA-Footage + TTS) vollständig rekonstruierbar. Auswertung: `analyse/pattern_report.py`.

---

## 1. Ranking (nach Wachstumstempo = Subs/Monat)

| # | Kanal | Subs | Alter | Upl/Mon | **Subs/Mon** | Views/Mon | Median-Views | Konsistenz¹ | Hit-Länge² |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Proof | 32,5k | **3 Wo.** | 19,8 | **49.400** | 3,2M | 13.161 | 0,7 % ⚠️ | 24,5 min |
| 2 | Ridddle | 3,54M | 12,4 J | 2,1 | 23.800 | 461k | 79.907 | **26,3 %** | 21,8 min |
| 3 | DestinySpace | 2,01M | 8,4 J | 3,2 | 19.900 | 3,9M | 191.500 | 0,7 % | 12,4 min |
| 4 | Cosmicus | 91,8k | 5,5 Mon | 16,8 | 16.800 | 3,9M | **2.416** ⚠️ | 1,8 % | 24,8 min |
| 5 | TheSpaceRace | 830k | 5 J | 7,6 | 13.900 | 3,1M | **431.806** | 8,8 % | 13,9 min |
| 6 | Space_Chip | 1,16M | 8,5 J | 4,4 | 11.400 | 4,1M | 55.597 | 12,5 % | 11,1 min |
| 7 | NSpaceNews | 614k | 4,9 J | **33,8** | 10.400 | 2,6M | 5.350 ⚠️ | 11,1 % | 9,4 min |
| 8 | Kosmo | 812k | 6,7 J | **1,8** | 10.200 | 1,8M | **667.500** | 9,7 % | **76,7 min** |
| 9 | VoyagerSpace | 571k | 6 J | 3,2 | 7.900 | 1,5M | 134.342 | 12,2 % | 24,0 min |
| 10 | spacemattersdoc | 329k | 4,1 J | 3,7 | 6.600 | 1,3M | 31.500 | 9,0 % | 37,7 min |
| 11 | RealHyperspeed | 246k | 3,3 J | 21,9 | 6.100 | 2,2M | 7.874 ⚠️ | 12,3 % | 122 min³ |
| 12 | InsaneCuriosity | 648k | 8,9 J | 19,0 | 6.100 | 1,1M | 10.350 ⚠️ | 5,9 % | 17,8 min |
| 13 | fexl | 258k | 3,8 J | 3,6 | 5.600 | 1,1M | 70.859 | 10,8 % | 28,2 min |
| 14 | Eternityinspace | 190k | 3,2 J | 30,5 | 4.900 | 1,4M | **115** ☠️ | 32 %⁴ | 18,1 min |
| 15 | officialcosmosprodigy | 130k | 4,1 J | 8,7 | 2.600 | 387k | 3.573 ⚠️ | 9,7 % | 12,1 min |
| 16 | astrumextra | 303k | 10,5 J | 1,5 | 2.400 | 514k | 212.953 | 26,4 % | 85,7 min |
| 17 | Starlight_Ai | 19,1k | 13 Mon | 2,7 | 1.400 | 189k | 4.600 | 0,2 % | 11,2 min |

¹ Konsistenz = Median/Max der jüngsten ~30–40 Videos: hoch = „System" (jedes Video trägt), niedrig = „Lotterie" (1 Hit, Rest tot).
² Median-Dauer der Top-10-Videos nach Views. ³ RealHyperspeed-Hits sind 2h-Compilations (anderes Publikum). ⁴ Eternityinspace: 32 % von Max **358** Views — konsistent tot.
⚠️ = Median unter ~15k trotz Reichweiten-Anspruch · ☠️ = klinisch tot.

**Subs/Monat bei Veteranen-Kanälen unterschätzt deren Peak** (Lebenszeit-Mittel). Deshalb zählt die Kombination: Subs/Mon + Median + Konsistenz.

---

## 2. DAS MUSTER — 8 verifizierte Befunde

### ⭐ M1 · Konsistenz schlägt Kadenz — die wichtigste Korrektur
Die **gesunden** Kanäle (Median ≥ 50k, Konsistenz 9–26 %) laden **1,5–7,6×/Monat**:
Kosmo 1,8 · astrumextra 1,5 · Ridddle 2,1 · DestinySpace 3,2 · VoyagerSpace 3,2 · fexl 3,6 · Space_Chip 4,4 · TheSpaceRace 7,6.
Die **toten** Kanäle laden **19–34×/Monat**: NSpaceNews 33,8 (Median 5,3k) · Eternityinspace 30,5 (Median **115**!) · RealHyperspeed 21,9 · InsaneCuriosity 19.
→ **Masse produziert nachweislich tote Mediane.** Das Playbook-„2–4 Videos/Woche" ist nach dieser Datenlage falsch herum: **1–2 polierte Videos/Woche ist das Gewinner-Band** (obere Grenze TheSpaceRace ~2/Woche). Cosmicus (16,8/Mon) sieht auf Gesamtreichweite gut aus, aber der Median der letzten ~40 Videos ist **2.416** — das Spam-Muster frisst den Kanal bereits.

### M2 · Zwei Längen-Modelle funktionieren — dazwischen stirbt es
Gepoolt über 131 Videos mit Dauer+Views: **10–15 min → Median 1,3M** · 15–20 → 145k · 20–27 → 19k · 27–40 → 11k.
- **Modell Standard (11–15 min):** TheSpaceRace (13,9), Space_Chip (11,1), DestinySpace (12,4). Die Mega-Hits (26M, 17M, 4,9M) liegen ALLE hier.
- **Modell Premium-Doku (60–90 min):** Kosmo (Hit-Länge 76,7, Median 667k!) und astrumextra (85,7, Median 213k) — wenige, lange, hochwertige Docs.
- Die 20–27-min-Zone ist bei den jungen KI-Kanälen (Proof, Cosmicus) besetzt — und genau dort sind die Mediane mickrig.
→ **Unsere 13:12 (Folge 1) liegt im Hit-Sweetspot.** Nicht künstlich auf 20+ strecken; 2 Mid-Rolls gehen ab 8 min.

### M3 · Die Titel-Formel ist Hygiene, kein Motor (Negativkontrolle!)
Die **toten** Kanäle benutzen die „Gewinner-Formeln" am HÄUFIGSTEN: Eternityinspace 67 % Urgency + 83 % Autorität (Median 115) · officialcosmosprodigy 80 % Autorität (Median 3,5k). Die **gesunden**: TheSpaceRace 0 % Urgency/63 % Autorität · Kosmo 0 % Urgency/40 % Fragen · Space_Chip 0 % auf allen Reiz-Formeln (Median 56k).
→ Formel-Sättigung ist ein **Slop-Marker**, den Zuschauer (und 2026 auch YouTube) erkennen. Autoritäts-Anker ja (17–63 %), aber nie im Dauerfeuer, nie zwei gleiche Muster nacheinander.

### M4 · Angst skaliert nicht — Neugier skaliert
Angst-/Schockwörter bei Gewinnern: TheSpaceRace 3 %, Kosmo 0 %, Space_Chip 0 %, Ridddle 3 %. Bei Verlierern: RealHyperspeed 30 %, Eternityinspace 23 %.
Die größten Hits sind **reine Neugier-Lücken**: „What NASA Found on Io" (4,9M) · „Real Images From Our Solar System" (17M) · „The First Minutes The Dinosaurs Went Extinct" (26M).

### M5 · Fragen-Titel sind das Systemkanal-Werkzeug
Kosmo 40 % · Ridddle 50 % · InsaneCuriosity 47 % (dessen gesunde Ära) · Space_Chip 20 %. „What/How/Can/Why" — die offene Frage IST der Klickgrund, kein Fake-Alarm nötig. Deckt sich mit unserer Schaufenster-Regel.

### M6 · Lotterie vs. System — zwei Wachstumsarten, nur eine hält
- **Lotterie:** Proof (1 Hit = 2M, Median 13k, Konsistenz 0,7 %), Starlight_Ai (1 Hit 2,1M, Median 4,6k → driftete zu Vögeln, tot), Cosmicus (frühe Hits, jetzt Median 2,4k).
- **System:** TheSpaceRace (Median 431k!), Kosmo (668k), astrumextra (213k), DestinySpace-Backkatalog.
→ Ein Hit macht keinen Kanal. **Der Median ist die Metrik, die zählt.** Systemkanäle bauen ihn über Packaging-Disziplin + Binge-Backkatalog (Playlists, Serien) auf.

### M7 · Der Evergreen-Backkatalog trägt die Veteranen
DestinySpace: 4,4M Views/Monat bei nur 3,2 Uploads — die Mega-Hits („Dinosaurs", „Real Images", „Kepler") sind **zeitlos** und sammeln jahrelang. News-Riding (Proof, Cosmicus) gibt den Anfangsschub, Evergreen bezahlt die Miete.
→ Mischverhältnis fürs erste Jahr: ~1× News-Riding : 1× Evergreen (unsere Folge 1 = News-Riding auf 3I/ATLAS ✓, Folge 2 = K2-18b hat beides ✓).

### M8 · 2026-Kontext: Der Slop-Crackdown ist real (Web-Beleg)
YouTube demotet/löscht „AI slop" aktiv (Forbes 01/2026; ein 3I/ATLAS-Fake-Kanal wurde komplett entfernt — Loeb/Medium). Die Muster M1/M3 (tote Mediane bei Spam-Kanälen) sind vermutlich schon der sichtbare Effekt. **Sichtbares redaktionelles Urteil + On-Screen-Quellen** (unsere §5b-Regeln) sind die Absicherung, die kein Slop-Kanal kopiert.

---

## 3. Ableitungen für UNS (konkret)

**Für den Launch von Folge 1 (3I/ATLAS):**
1. Länge 13:12 = Sweetspot ✓ — nichts ändern.
2. Titel „Is 3I/ATLAS Alien Technology? What the Evidence Really Shows" = Frage + Anker, kein Fake-Alarm ✓ (M4/M5).
3. **Direkt Playlist/Serie anlegen** („SIGNAL · Interstellar Objects") — Systemkanäle leben vom Binge-Pfad (M6).
4. Nicht am Launch-Tag nachschieben: Erst Performance lesen, Folge 2 im Abstand von 3–7 Tagen.

**Für die Produktion von Folge 2 (K2-18b):**
5. **Ziel-Länge 12–16 min** statt 19–20. Das v4-Skript (~2.600 Wörter ≈ 19,5 min) für die Vertonung auf **~1.900–2.100 Wörter** straffen — Kürzungsmasse: Segment 2/3 Redundanzen, nicht die Beats. (M2; die 20–27-min-Zone ist die Todeszone der jungen KI-Kanäle.)
6. Kadenz-Plan: **1–2 Folgen/Woche, poliert** — NICHT 4+ (M1). Lieber jede Folge mit Fakten-Gate + On-Screen-Quellen als Masse.
7. Titel-Rotation erzwingen: nie zweimal hintereinander dieselbe Formel (M3). Folge 1 = Frage-Titel → Folge 2 = Abrechnungs-Titel („…Then a Dozen Teams Took It Apart") ✓.
8. Evergreen-Kern sichern: K2-18b-Folge so schneiden, dass sie auch in 12 Monaten funktioniert (kein „this week"; Datteln nur wo nötig) (M7).
9. Median > Max als unser KPI: Ziel ist nicht der 2M-Ausreißer, sondern dass Video 5 noch 10k+ macht. Review nach jedem Upload gegen diese Tabelle.

---

*Anhang: Web-Recherche-Layer (Top-30-Außensicht, 2025/26-Schnellwachser, verifizierte Wachstumszahlen) wird nach Abschluss der laufenden Deep-Research ergänzt.*
