# Was kostet so ein Video mit Higgsfield? — Fall @NebulaProphecy

> Frage: „Was kostet die Erstellung von so einem Video mit Higgsfield?"
> Referenz: [They Left Him to Die in Chains… but the River Creature Had Other Plans](https://www.youtube.com/watch?v=vy96cmv-2ck) · 20:21 · 8,0 Mio. Views in 2 Wochen
> Erhoben 31.07.2026. Stückkosten sind **eigene Messwerte** aus `produktion/folge-01-v4/budget-ledger.md`, keine Listenpreise.
> Rechner: `produktion/pipeline/kosten_kalk.py`

---

## 1. Erst der Kanal — er ist der eigentliche Befund

| | |
|---|---|
| Kanal | [@NebulaProphecy](https://www.youtube.com/@NebulaProphecy) |
| Land | Spanien |
| Start | **5. September 2025** (10,8 Monate) |
| **Videos** | **5** |
| Abonnenten | 78.800 |
| **Gesamt-Views** | **11.892.518** |
| Median | 652.000 |
| Selbstbeschreibung | „all crafted entirely with AI tools" |

| Video | Länge | Views | Alter |
|---|---:|---:|---|
| [They Left Him to Die in Chains…](https://youtu.be/vy96cmv-2ck) | 20:21 | **8.000.000** | 2 Wochen |
| [Renegade Pirate / Cursed Island / Mermaid](https://youtu.be/O1kSruACE6o) | 19:33 | 3.000.000 | 3 Wochen |
| [Hostile Planet EP 1](https://youtu.be/6ZD2Q9DTNeU) | 12:22 | 652.000 | 2 Monate |
| [They Sent Him to Hunt It…](https://youtu.be/BDvJlnMiAns) | 16:13 | 578.000 | 1 Monat |
| [Hostile Planet EP 2](https://youtu.be/JRMD45eAVL0) | 18:18 | 198.000 | 1 Monat |

**Fünf Videos. 11,9 Millionen Views. Gestartet im selben Monat wie @Erdarchiv.** Das ist die höchste Views-pro-Video-Leistung, die in diesem Repo dokumentiert ist — 2,4 Mio. im Schnitt gegen unsere Folge-1-Größenordnung.

---

## 2. Das Kostengesetz, das man falsch rechnet

Man denkt in **Clips** — Higgsfield rechnet in **Sekunden Ausgabe-Video**.

245 Clips à 5 s und 153 Clips à 8 s sind beide 1.221 Sekunden und kosten **dasselbe**. Die Clipzahl ist für die Rechnung irrelevant. Es gibt genau eine Größe, die den Preis bewegt:

> ### Die KI-Video-Deckung: welcher Anteil der Laufzeit ist generiertes Bewegtbild?

Alles andere ist gratis: Standbild mit Kamerafahrt im Schnittprogramm, gemeinfreies Archivmaterial, Reuse aus dem Clip-Pool. **0 Credits.**

### Unsere gemessenen Stückkosten

| Posten | Credits | pro Sekunde | **pro Minute KI-Video** |
|---|---:|---:|---:|
| Seedance 720p / fast / 5 s | 17,5 | 3,5 Cr/s | **9,97 €** |
| Seedance 1080p / std / 5 s | 45 | 9,0 Cr/s | **25,65 €** |
| Seedance 4K / high / 5 s | 110 | 22,0 Cr/s | **62,70 €** |
| Nano Banana Pro 1k (start_image) | 2 | — | je Shot |

Kurs: 2.000 Cr = 95 € → **1 Cr = 0,0475 €**

---

## 3. Die Antwort — 20:21 Laufzeit

Reroll-Faktor: **1,3× (gut)** bis **1,8× (realistisch)**. Unsere eigenen Folgen lagen bei 1,08–1,42×; ein Story-Video mit wiederkehrenden Figuren und Fabelwesen liegt höher, weil Charakter-Konsistenz Fehlversuche produziert.

### 1080p / std — die Stufe, die wir selbst fahren

| KI-Deckung | KI-Sekunden | Shots | **€ (gut)** | **€ (realistisch)** |
|---:|---:|---:|---:|---:|
| 8 % *(unser Muster)* | 98 | 20 | 57 € | 79 € |
| 25 % | 305 | 61 | 177 € | 245 € |
| 50 % | 610 | 122 | 354 € | 491 € |
| **75 %** | **916** | **183** | **532 €** | **736 €** |
| 100 % | 1.221 | 244 | 709 € | **981 €** |

### Die anderen zwei Stufen, bei 100 % Deckung

| Stufe | € (gut) | € (realistisch) |
|---|---:|---:|
| 720p / fast | 294 € | 407 € |
| **1080p / std** | **709 €** | **981 €** |
| 4K / high | 1.689 € | **2.338 €** |

## 📌 Die Zahl

**Bei 1080p und hoher Deckung: 530 – 980 € pro Video, nur Higgsfield.**

Für ein Fantasy-Story-Video ist die Deckung zwangsläufig hoch — Flusskreatur, Ketten, Meerjungfrau: dafür existiert **kein Archivmaterial**. Realistisch sind 60–90 %, weil solche Kanäle Establishing-Shots wiederverwenden und mit Slow Motion streckten. Mein Mittelwert: **rund 700 €.**

In 4K wären es **1.700 – 2.300 €.** Die Videoqualität des Referenzvideos legt eher 1080p nahe.

Dazu kommen: Voiceover ~20.000 Zeichen (bei uns im ElevenLabs-Creator-Abo enthalten, ~3–4 €), Musik, Schnitt (lokal, 0 €).

---

## 4. Der Vergleich, der wehtut

| | @NebulaProphecy | **SIGNAL F3/F4** |
|---|---:|---:|
| Laufzeit | 20 Min | 13 Min |
| KI-Video-Deckung | ~75–100 % | **~8 %** |
| Video-Generierungen | ~180–245 | **13** |
| Higgsfield-Ist | ~700 € (geschätzt) | **31,52 € / 32,37 €** |
| **Faktor** | | **≈ 22×** |

Der Unterschied ist **nicht** Qualität und **nicht** Länge. Er ist eine einzige Entscheidung: Wir generieren 63 Sekunden KI-Video pro Folge und füllen die übrigen zwölf Minuten mit gemeinfreier NASA/ESA-Footage, Standbildern mit Kamerafahrt und Pool-Reuse. Nebula Prophecy generiert alles.

**Und das ist genau Gate D2 unseres Nischen-Systems** („freier Materialpool vorhanden"). Fantasy-Story-Content reißt D2 — es gibt keinen gemeinfreien Pool für Flusskreaturen. Das System hat diese Kostenfolge korrekt vorhergesagt: **ein gerissenes D2 kostet hier Faktor 22 im Budget.**

---

## 5. Rechnet es sich? — die unbequeme Antwort

Bei 8 Mio. Views ist die Frage trivial. Bei den anderen vier Videos nicht.

Angesetzter RPM für englischsprachige KI-Story-Unterhaltung: **2–5 $** (breites internationales Publikum drückt den RPM; keine Wirtschafts-/Finanz-Werbekategorie).

| Video | Views | Erlös bei 2–5 $ | Kosten ~760 $ | Ergebnis |
|---|---:|---:|---:|---|
| Chains / River Creature | 8.000.000 | **16.000 – 40.000 $** | 760 $ | ✅ Volltreffer |
| Pirate / Mermaid | 3.000.000 | 6.000 – 15.000 $ | 760 $ | ✅ |
| Hostile Planet EP 1 | 652.000 | 1.300 – 3.300 $ | 760 $ | ✅ knapp |
| They Sent Him to Hunt It | 578.000 | 1.160 – 2.900 $ | 760 $ | ⚠️ dünn |
| Hostile Planet EP 2 | 198.000 | **400 – 990 $** | 760 $ | ❌ **Verlust bis Nullsumme** |

**Kanal gesamt:** 11,9 Mio. Views → geschätzt **24.000 – 59.000 $** gegen ~3.800 $ Produktionskosten in 11 Monaten.

### Was daraus folgt

**Dieses Geschäftsmodell funktioniert nur über den Ausbrecher.** Bei 700 € Stückkosten liegt die Nullsumme bei rund **200.000 – 380.000 Views pro Video**. Zwei der fünf Videos liegen an oder unter dieser Linie. Die beiden Treffer tragen alles.

Zum Vergleich unser Modell: bei 32 € Stückkosten liegt die Nullsumme bei **7.000 – 17.000 Views**. Das ist ein völlig anderes Risikoprofil — wir brauchen keinen Volltreffer, um nicht zu verlieren.

| | Nullsumme pro Video |
|---|---:|
| KI-Vollproduktion (700 €) | **200.000 – 380.000 Views** |
| SIGNAL-Muster (32 €) | **7.000 – 17.000 Views** |

---

## 6. Praktische Hürde heute

Aktuelles Higgsfield-Guthaben: **200,9 Cr** (Plan: Ultra). Für ein solches Video bräuchte es **~15.000 Cr**. Die Top-up-Pakete gehen bis 4.000 Cr — es wären also vier Käufe und rund 700 €. Das steht in keinem Verhältnis zum bestehenden Folgen-Deckel von 50 €.

**Ein Testlauf wäre möglich:** ein 2-Minuten-Cold-Open in Story-Machart, 100 % Deckung, 1080p → 24 KI-Sekunden × … bzw. 120 s × 9 Cr/s × 1,3 = **~1.500 Cr ≈ 70 €**. Das beantwortet die Qualitätsfrage, ohne 700 € zu binden.

---

## 7. Was an dieser Rechnung unsicher ist

1. **Die KI-Deckung des Referenzvideos ist nicht gemessen, sondern geschätzt (60–90 %).** Ich konnte sie nicht bestimmen: Higgsfields `video_analysis_create` brach mit „Something went wrong" ab, und der Download für eigene Schnitterkennung wurde von YouTube bot-geblockt (HTTP 403 / „Sign in to confirm you're not a bot"). **Das ist die größte Unsicherheit der ganzen Rechnung** — sie bewegt das Ergebnis zwischen 354 € und 981 €. Auflösbar in einer Minute durch Hinschauen: Wie viel des Videos ist echtes Bewegtbild, wie viel ist Standbild mit langsamer Kamerafahrt?
2. **Der RPM von 2–5 $ ist angesetzt, nicht gemessen.** Bei 8 Mio. Views verschiebt jeder Dollar RPM das Ergebnis um 8.000 $.
3. **Der Reroll-Faktor 1,3–1,8× ist aus unseren Doku-Folgen übertragen.** Charakter-Konsistenz über 180 Shots könnte deutlich teurer ausfallen.
4. **Die Stückkosten gelten für Seedance.** Veo 3.1 oder Kling 3.0 in `pro`/`4k` liegen darüber; Higgsfields API gibt die Credit-Preise nicht aus, unsere Werte stammen aus eigenen `get_cost`-Messungen bei F1.
5. **Views-Werte sind YouTubes gerundete Anzeige** (8M, 3M). Die exakten Zahlen liegen nicht vor.

---

## CHANGELOG
- **31.07.2026** — Kostenanalyse zum Referenzvideo. Kernbefund: Higgsfield rechnet **pro Sekunde Ausgabe-Video**, nicht pro Clip — die einzige preistreibende Größe ist die KI-Video-Deckung. Bei 1080p und hoher Deckung **530–980 € pro 20-Minuten-Video**, in 4K 1.700–2.300 €. Gegen unsere eigenen 31,52/32,37 € pro Folge ist das **Faktor 22**, und der Grund ist gerissenes Gate D2 (kein gemeinfreier Materialpool für Fantasy-Stoff). Nullsumme verschiebt sich damit von 7.000–17.000 auf 200.000–380.000 Views pro Video — zwei der fünf Nebula-Videos liegen an dieser Linie. Rechner als `produktion/pipeline/kosten_kalk.py` hinzugefügt, an F3/F4-Ist gegengeprüft. Deckung des Referenzvideos ungemessen (Higgsfield-Analyse failed, Download bot-geblockt).
