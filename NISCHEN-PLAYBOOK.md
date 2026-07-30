# 🎯 Nischen-Playbook — wie wir Nischen finden (kanal-unabhängig)

> **Zweck:** `SPACE-PLAYBOOK.md` sagt, wie wir *einen* Kanal bauen. Dieses Dokument sagt, **welchen Kanal wir überhaupt bauen** — reproduzierbar, für jeden künftigen Kanal.
> **⚡ Ausführbar:** Der Satz „finde eine perfekte Nische" löst `.claude/skills/nische-finden/` aus. Dieses Dokument ist die **Herleitung**, die Skill die **Prozedur**. Kurzfassung: §12.
> **Datenbasis:** zwei Recherchewellen à 12 Agenten (je 6 Rechercheure + 6 adversariale Gegenprüfer), ~655 Tool-Calls, 30.07.2026. Welle 1: Methodik/Tooling. Welle 2: *Leute mit nachweisbarem Geld* — Käufer-Ökonomie, benannte Operator, MCN-Aggregate, Post-Mortems. **Welle 2 hat Teile von Welle 1 widerlegt → §1b.**
> **Lesereihenfolge bei einer neuen Nischen-Idee:** §1 + §1b → §2 (Kill-Gates) → §3 (Nachfrage) → §4 (Arithmetik) → §5 (Packaging) → §6/§10b (Geld). Nie überspringen, nie umsortieren.

---

## 1. ⭐ Der wichtigste Befund: Die „Profi-Methode" ist zu 90 % Vendor-Marketing

Das ist das zentrale Ergebnis der Recherche, und es ändert, wie wir mit allen Zahlen umgehen.

Die adversariale Gegenprüfung hat systematisch **dieselbe Struktur** gefunden: Nischen-Schwellenwerte, Scorecards und „Branchenkonventionen" stammen fast ausschließlich aus **Blogs von Tool-Anbietern**, die sich gegenseitig zitieren und dabei die Websuche fluten. Konkret zerlegt:

| Behauptung, die überall steht | Was die Prüfung fand |
|---|---|
| „Outlier = 3× Median, Branchenstandard" | **Erfunden.** vidIQ rechnet gegen den **Durchschnitt** (Bänder <2×/2–5×/5–10×/>10×), ViewStats gegen die letzten 9 Uploads, 1of10 filtert 6×–100×. Kein Konsens — und **alle vier sind kanal-relativ, nicht nischen-relativ** (Kategorienfehler) |
| „Paddy Galloway sucht 5×–15×-Anomalien" | **Zirkulär.** Einzige Fundstelle ist der Blog eines Konkurrenz-Tools, kein Primärzitat |
| Feste Nischen-Scorecards (7×0–10, Kill unter 5) | Existieren wörtlich — aber **unkalibriert, ohne Datenbasis, in sich widersprüchlich** (Schwelle fordert ≥8, Kill greift erst <5) |
| „Median statt Durchschnitt" als Tool-Konvention | **Blog-Meinung eines Ein-Mann-Blogs**, nicht Herstellerangabe |
| RPM-Tabellen nach Nische | Werte **existieren**, widersprechen sich aber um Faktor 2–4 zwischen Quellen |
| „74,8 % der Kanäle scheitern" | **Falsche Kohorte** — gemessen an Kanälen, die 2019 schon ≥10k Abos hatten. Keine Neustart-Basisrate |

**Die Konsequenz — unsere Beweis-Hierarchie (verbindlich):**

| Stufe | Quelle | Status |
|---|---|---|
| **A — bindend** | YouTube-Hilfe/Policy, blog.youtube, Google-Developer-Docs, offizielle Behördenseiten, peer-reviewte Studien | Als Regel verwendbar |
| **B — Heuristik** | Praktiker-Aussagen mit Namen und Kontext, MCN-Daten (z. B. AIR Media-Tech) | Als Hypothese verwendbar, immer als solche kennzeichnen |
| **C — Rauschen** | Tool-Blogs, SEO-„Guides", Affiliate-Seiten, Scraper-Statistikseiten | Nur als Ideengeber. **Nie als Schwellenwert** |

**Und die eigentliche Lehre:** Wir haben in `research/konkurrenz-muster.md` bereits eine 17-Kanal-Primärdatenbasis, die wir selbst erhoben haben. **Die schlägt jede gekaufte Rubrik.** Der Weg ist nicht, bessere Tabellen zu finden — es ist, die eigene Messung zu erweitern.

---

## 1b. ⭐⭐ Die Korrektur, die schmerzt: Top-Verdiener bewerten Nischen überhaupt nicht

Eine zweite Recherche (12 Agenten, Fokus: *Leute mit nachweisbarem Geld*, nicht Blogger) hat drei Befunde geliefert, die **die erste Fassung dieses Playbooks teilweise widerlegen.** Sie stehen hier vorn, weil alles Folgende davon abhängt.

### Befund 1 — Das Nischen-Scoring ist eine Erfindung der Tool-Branche

- **Das geleakte MrBeast-Produktionshandbuch enthält das Wort „niche" NULL Mal.** Der Prüfer hat das PDF selbst extrahiert (36 Seiten) und gegrept: `niche` 0 · `score` 0 · `greenlight` 0 · `rubric` 0. Echtheit von Ex-Mitarbeitern gegenüber Business Insider bestätigt; das Unternehmen bestreitet sie nicht, bestätigt sie aber auch nicht.
- **Paddy Galloway wörtlich** (Volltranskript, Creator Science): *„there's no niche where I can't get traction."* Sein verifiziertes Verfahren ist eine **Sichtung**, kein Gate: *„search that term golf, filter it for longer videos … then sort by most viewed."*
- Was Top-Verdiener stattdessen belegbar tun: **Packaging vor Produktion** (*„THIS IS WHY YOU MUST KNOW THE TITLE AND THUMBNAILS"*), **Format-Rotation** (*„every channel that rehashes formats for years always dies"*), **Ideen-Überschuss** (10×–30× der Produktionsrate).

→ **Konsequenz:** Punktesummen bleiben in diesem Playbook nur als *Kommunikationsmittel*. Entscheidungen fallen an **Kill-Gates** und der **Arithmetik**. Die 40-Punkte-Bewertungen in unseren bisherigen Nischen-Dokumenten (Krimi 12/40, BLACKBOX 29/40) sind als Zusammenfassung brauchbar, als Begründung nicht.

### Befund 2 — Die Streuung INNERHALB einer Nische ist größer als die zwischen Nischen

AIR Media-Tech (echtes MCN, 3.595 monetarisierte Kanal-Monate, *„read straight from Studio"*), Education & Science:

| P25 | Median | P75 | Streuung |
|---|---|---|---|
| **$2,31** | $10,22 | $19,50 | **8,4×** — die breiteste aller Nischen |

Alle-Nischen-Median: **$2,30**. → **Wer mit $10 RPM plant, plant auf dem 75. Perzentil.** Der Planwert ist **P25**, nicht der Median. Und: Die Nischenwahl entscheidet weniger als die Ausführung — deshalb zügig durch die Gates statt endlos vergleichen.
*(Kohorten-Vorbehalt: AIR-Partnerkanäle, 10k–50M Abos, 44 Länder; für Education & Science nennt AIR keine Fallzahl.)*

### Befund 3 — Der einzige geldverifizierte Faceless-Operator macht genau das, was „Qualitäts"-Raster ausschließen

Fortune berichtete (mit vom Betroffenen gelieferten Screenshots, kein Audit) über einen Operator mit **$40.000–60.000/Monat** aus **fünf** aktiven Kanälen. Sein umsatzstärkster: *„a 'Boring History' channel built around six-hour 'history to sleep to' documentaries"* — dazu Tier-Compilations, Prank-Videos, Anime-Edits, Bollywood-Clips, Promi-Klatsch. Seine Strategie in seinen Worten: **„small edges inside formats that already work."** Seine Erwartung: das trägt *„until around 2027."*

Und: **YouTube hat ausdrücklich klargestellt**, dass es *„no change to the reused content policy which reviews … clips, compilations, and reaction videos"* gibt. Compilations und Sleep-Dokus sind also **nicht per Policy verboten** — meine frühere Formulierung, sie seien „strukturell ausgeschlossen", war als Rechtsaussage falsch.

→ **Konsequenz: Es gibt zwei verschiedene Spiele, und die Kriterien invertieren sich.** Das muss VOR der Nischensuche geklärt sein:

| | **Extraktion** | **Equity** |
|---|---|---|
| Ziel | Cash jetzt | verkaufbarer Vermögenswert |
| Beleg | verifiziert profitabel (s. o.) | Broker-Kriterien erfüllbar |
| Fenster | 1–3 Jahre, dann tot (der Operator sagt das selbst) | offen |
| Exit-Wert | keiner | 1,2×–2,2× Jahresgewinn |
| Gate K3 (Originalität) | fällt weg | bindend |

Dieses Playbook ist auf **Equity** ausgelegt — nachhaltiger $10k-Kanal, der eine Policy-Welle übersteht und verkäuflich ist. Das ist eine *Wahl*, keine Naturgesetzlichkeit. Wer Extraktion will, braucht ein anderes Playbook.

---

## 2. Stufe 1 — Die 7 Kill-Gates (binär, VOR jeder Nachfrage-Recherche)

**Die Reihenfolge ist der eigentliche Trick.** Fast alle machen es falsch: erst ein spannendes Thema finden, dann merken, dass es rechtlich oder wirtschaftlich tot ist.

> **Selbsttest an unseren eigenen Fällen:** Die Krimi-Idee („Diebe im Gesetz") wäre an **G1 und G2** in zehn Minuten gestorben — wir haben stattdessen eine Vollrecherche über sechs Dimensionen gefahren. Und BLACKBOX (Technik-Katastrophen) scheitert an **G4**. Beides hätte dieses Gate vorab gezeigt.

Keine Punkte, keine Aufrechnung: **ein „nein" = Nische verworfen.**

### G1 · Keine reale Person im Zentrum
Kein Kanal, dessen Folgen ohne die Nennung/Abbildung identifizierbarer, lebender Personen nicht funktionieren.
*Warum:* Persönlichkeitsrecht, KUG, Verdachtsberichterstattung (BGH VI ZR 262/21), YouTube-Likeness-Detection (seit 18.05.2026 für alle verifizierten Nutzer 18+ — Voice-Clones noch **nicht** abgedeckt), EU-KI-VO. Verstorbene >10 Jahre und Rollen-statt-Namen sind der Ausweg.
*Präzision aus der Gegenprüfung:* Kaliforniens AB 1836/2602 gelten **nur** für KI-Replikate Verstorbener bzw. Vertragsklauseln mit Performern — eine Doku *über* eine lebende Person fällt unter keins von beiden. Das echte Risiko ist Right of Publicity, Äußerungsrecht und die YouTube-Policy.

### G2 · Freier Asset-Pool mit maschinellem Zugang
Alle vier Bedingungen: **(i)** API oder Bulk-Download · **(ii)** Bewegtbild oder ≥1.000 verwertbare Stills · **(iii)** Rechtsstatus pauschal klärbar (PD/CC0) · **(iv)** trägt ≥50 Folgenthemen.
*Warum:* Ohne Pool bricht die KI-Pipeline (Krimi-Lesson: 80–350 €/Folge statt 35 €). Der verifizierte Pool-Katalog steht in §8.

### G3 · Originalitäts-Substrat (der Interchangeability-Test) — *nur im Equity-Spiel bindend*
> ⚠️ **Korrigiert (§1b, Befund 3):** Dieses Gate ist eine **Equity-Entscheidung** (Verkäuflichkeit + Policy-Robustheit), **keine Rechtspflicht.** YouTube sagt ausdrücklich, dass Compilations/Clips/Reactions weiter zulässig sind, und der eine verifizierte Verdiener lebt von Sleep-Dokus. Wer Extraktion spielt, streicht dieses Gate — und akzeptiert das 1–3-Jahres-Fenster.
Pro Folge muss **zwingend** mindestens einer dieser menschlichen Beiträge anfallen: eigene Primärquellen-Recherche · eigenes redaktionelles Urteil (Verdict) · eigene Messung/Auswertung.
*Operationalisierung:* Formuliere den Kanal-Pitch in einem Satz. Findest du ≥5 Kanäle, deren Videos man gegen die eigenen tauschen könnte, ohne dass ein Zuschauer es merkt → **verworfen.**
*Warum (Stufe A):* YouTubes Policy verlangt wörtlich „**meaningful** difference" und „The substance of each video should be materially varied"; VP Trust & Safety **Matt Halprin** bestätigte (Juli 2026): Bewertung erfolgt auf **Kanalebene**, ist **tool-agnostisch** („regardless of whether AI, CGI, or no additional tools were used"), und die Anzahl der Meldungen ist irrelevant. Einspruchsfrist **21 Tage**. Das Dachprinzip heißt „original, not interchangeable".
*Strukturell ausgeschlossen:* Kompilation, Vorlesen, Listicle, Quiz, generische Motivation, Reddit-Nacherzählung, Ambient/Sleep. Dort ist echte Variation unmöglich.

### G4 · Sprachmarkt = Englisch
*Warum:* Der deutsche RPM liegt bei ~0,6× US, der adressierbare Markt aber nur bei ~0,25×. Beide Faktoren multiplizieren sich gegen dich. **Zweiter Kanal = zweite englische Nische, nicht zweite Sprache.** Für Deutsch gibt es einen besseren Weg — siehe §7.

### G5 · Keine Kategorie mit Monetarisierungs-Deckel
Raus bei: **Made-for-Kids-Verdacht** (Feature-Verlust laut Google-Doc: keine Kommentare, keine Playlists, kein Endscreen; die peer-reviewte COPPA-Studie in *Management Science*, 04.05.2026, fand nach dem 2020er-Settlement −20 % Views, −18 % Output, −9 % Originalanteil bei 5.066 Kanälen) · **YMYL mit Beratungscharakter** (Gesundheit, Finanz-/Krypto-Empfehlung, Recht, Gambling — eine KI-Stimme als „Experte" ist dort doppelt exponiert) · **dauerhaft ineligible Themen** (Kindesmissbrauch, Kinderhandel, Essstörungen).
*Präzision:* Seit Januar 2026 sind sechs Themen bei **nicht-grafischer** Darstellung monetarisierbar (häusliche Gewalt, Selbstverletzung, Suizid, sexueller Missbrauch Erwachsener, Abtreibung, sexuelle Belästigung) — die Regeln wurden dort **gelockert**, nicht verschärft.
*Erlaubt bleibt:* hohe-CPM-Themen **ohne** Beratung — Wissenschaft/Doku, Technik-Erklärung, Markt-**Daten** statt Markt-**Tipps**.

### G6 · Trägt 150 Folgen à ≥3 Min
Wenn der Themenpool nach 20 Folgen leer ist, war es ein Video-Format, keine Nische. Die 150 sind als Sanity-Check von Jellysmacks Katalogtiefe-Anforderung übernommen (*„gibt die Nische 150 Titel her?"*) — bewusst hoch, weil ein zu enger Pool der häufigste stille Tod ist.

### G7 · Ohne Person übertragbar
Der Kanal muss ohne einen benannten Menschen funktionieren und verkäuflich sein.
*Warum (Geldgrund):* Broker führen *„High personalization/personality-dependent content"* wörtlich als Wertminderer; für die Eigentumsübertragung ist ein **Brand Account** (kein persönliches Google-Konto) Pflicht. Wer eine Personenmarke baut, baut einen Job, kein Asset.

---

## 3. Stufe 2 — Nachfrage messen: die 2×2-Diagnose

Erst wenn alle 6 Gates „ja" sind. Das hier ist das analytisch wertvollste Werkzeug des Playbooks.

**Was gemessen wird — pro Nische, über 15–30 Kanäle:**
- **Median** der Longform-Views (nie Durchschnitt, nie Top-Video)
- Abonnenten
- **Kanalalter** (Beitrittsdatum)
- **Views ÷ Abos** (Verhältnis)
- Datum des jüngsten Outliers

**Die Diagnose:**

| | **Große Kanäle holen Views** | **Große Kanäle holen keine Views** |
|---|---|---|
| **Kleine Kanäle (<50k) holen Outlier** | 🟢 **System-Nische** — rein | 🟡 **Frühe Welle** — schnell rein, klein testen |
| **Kleine Kanäle holen keine Outlier** | 🟠 **Gesättigt** — nur mit Format-Twist | 🔴 **Keine Nachfrage** — raus. *Das ist kein Geheimtipp.* |

Das rote Feld ist der teuerste Fehler im ganzen Prozess: **„unbesetzt" und „keine Nachfrage" sehen identisch aus.** Die Krimi-Nische war rot (Feldtest @VerbrechensInc: 10 Monate, 4.210 Abos, Median ~2k) — und wirkte auf den ersten Blick wie eine offene Lücke.

**Das Kleinkanal-Gate** (unsere Setzung, als Heuristik deklariert — es gibt dafür keine belastbare Fremdquelle):
> Mindestens **3 verschiedene** Kanäle unter 50k Abos mit je einem Video ≥100k Views in den letzten 12 Monaten, davon **mindestens einer unter 12 Monate alt.**
> Weniger als 3 → Lotterie, nicht Nische. Fehlt das Alters-Signal → das Fenster ist zu, es bliebe nur Verdrängung.

**Warum kleine Kanäle das Signal sind:** vidIQ formuliert es (Stufe B, Herstellerseite): „If only huge channels get views, the niche is saturated." Ein Kanal mit 8k Abos und 300k Views auf einem Video beweist mehr über die Nische als ein 4-Mio.-Kanal mit denselben 300k — weil im ersten Fall der **Stoff** zieht und nicht die Marke.

**Beim Outlier-Score sauber bleiben:** `Outlier = Views(t) ÷ Baseline des eigenen Kanals bei gleichem Alter t`. Das ist eine **kanal-relative** Kennzahl — sie sagt, welches *Thema* auf einem *fremden* Kanal überperformt hat. Sie sagt **nichts** über die Attraktivität einer Nische. Die einzige belegte Skala ist vidIQs Farbcode (Stufe A, Herstellerangabe): **<2× schwarz · 2–5× blau · 5–10× violett · >10× rot.** Über 10× vorsichtig sein: solche Werte sind oft extern getrieben und nicht reproduzierbar.

---

## 4. Stufe 3 — Das Arithmetik-Gate (10 Minuten, entscheidet mehr als alles andere)

Zwei Formeln. Wer sie nicht rechnet, hofft.

```
Break-even-Views/Folge = Kosten pro Folge ÷ (RPM ÷ 1000)
Views/Monat für Ziel    = (Ziel-$ ÷ RPM) × 1000
Nötiger Median/Folge    = Views/Monat ÷ Uploads pro Monat
```

**Bei euren Zahlen** (35 € ≈ 38 $/Folge, konservativ RPM $4, 8 Folgen/Monat):
- Break-even: **9.500 Views/Folge**
- $10.000/Monat: **2,5 Mio. Views/Monat** → **~310k Median-Views pro Folge**

**Screening-Gate:** Liegt der beobachtete Nischen-Median der 10k–100k-Abo-Kanäle unter diesem Wert, ist das Umsatzziel in dieser Nische **arithmetisch** nicht erreichbar. Dann: Nische verwerfen, Ziel senken oder Uploads erhöhen — aber nicht weiterhoffen.

> ⚠️ **Korrigiert (§1b, Befund 2):** Der Planwert ist **P25, nicht der Median** — für Doku/Science/Education **$2,31** (AIR, 3.595 Kanal-Monate). Mit RPM $2,31 und den Defaults: Break-even **16.450 Views/Folge**, $10k-Ziel = **4,33 Mio. Views/Monat** → nötiger Median **541.000/Folge**. Das ist die ehrliche Zahl; die $4-Rechnung unten ist das optimistische Szenario.
> Zusätzlich **Saison-Abschlag**: Januar liegt **34 %** unter November (AIR, 13 Werte wörtlich bestätigt).

**RPM als Band, nie als Punktwert** (Gegenprüfung hat hier hart korrigiert):

| Nische | Spanne | Anmerkung |
|---|---|---|
| Finance | $5–17 RPM / $15–50 CPM | vidIQ, 2026 — aber YMYL-Falle (G5) |
| Tech | $4–10 | Mediacube, 10/2025 |
| **Doku / Science / Education** | **$3–10 — umstritten** | AIR Media-Tech (echtes MCN, 01.07.2026): Median **$10,22**. LenosTube: $2,75–6,88. **Es gibt keinen Konsenswert** |
| Health/Fitness | $3–7 | Beratungscharakter meiden |
| Entertainment | $2–5 | |

**Regel:** Immer mit dem **unteren Drittel** rechnen, und **×0,7** für Nicht-Q4. Der Dezember→Januar-Einbruch von 30–40 % ist als Größenordnung belegt — Nischen-Entscheidungen nie auf Dezember-Zahlen stützen. Launch-Timing: Kanal in Q1/Q2 aufbauen, damit die Reichweite im Q4-Peak steht.

---

## 5. Stufe 4 — Der Papier-Test (0 €, ein Tag)

Vor dem ersten Euro Produktionskosten:

1. **30 Folgenthemen** in 3–5 wiederholbaren Formaten aufschreiben
2. **20 Titel** — wenn das länger als 30 Minuten dauert, ist die Nische zu dünn
3. **10 Thumbnail-Skizzen**

Nicht erreichbar ohne Wiederholung → **sofort verwerfen.** Dieser Test kostet nichts und tötet die meisten Kandidaten.

---

## 6. Stufe 5 — Geld, Stop-Loss und der Zeitpunkt für Kanal Nr. 2

**Urteilsfenster vorher fixieren** (Heuristik, nicht belegt — Agentur-Selbstauskünfte wurden von der Gegenprüfung verworfen):
- 12–15 Videos / 90 Tage = frühester Diagnosepunkt
- 20–30 Videos / 3–6 Monate = Nischen-Verdikt
- **Vorher gilt:** CTR unter ~2 % oder Retention unter ~30 % → **Packaging ist schuldig, nicht die Nische.** Nie eine Nische für ein Thumbnail-Problem verwerfen.

**Budget-Stop-Loss:** 20–30 Folgen × 35 € = **Deckel 700–1.050 € pro Nische**, hart, mit Abbruch-Review bei Folge 10. **Maximal eine Test-Nische parallel** — ein Test frisst dieselbe Kapazität wie eine reguläre Folge.

**Bedingung für Kanal Nr. 2 — ein Zustand, kein Datum:**
> (a) SIGNAL produziert **ohne neue Entscheidungen pro Folge** (Pipeline + Config statt Diskussion), **UND**
> (b) Kanal 2 kostet pro Folge weniger Aufwand als SIGNAL — oder es gibt einen bezahlten Editor.

**Multi-Kanal-Regel (Cluster-Schutz, Stufe B aber gut begründet):** Zwischen eigenen Kanälen dürfen sich **Skript-Struktur, VO-Stimme, Template, Musikbett, Upload-Rhythmus und Thumbnail-Grammatik nicht teilen.** Google Research beschreibt ein produktiv eingesetztes Cluster-Terminierungssystem (Sentence-BERT-Textembeddings + Publishing-Frequenz + Infrastruktur-Clustering, 50k Cluster / 130k Kanäle in 6 Monaten) — die Plattform wird im Paper *nicht* benannt, YouTube ist aber naheliegend. Umformulierte Gleichstruktur wird erkannt. **Ein Slop-Verdacht darf nie zwei Kanäle treffen.**

**Beweis-Akte pro Folge:** Recherche-Notizen, Skript-Entwürfe, Quellen-Dossier, Projektdateien archivieren. Reviewer akzeptieren Nachweise des Produktionsprozesses, keine Absichtserklärungen.

---

## 7. Die Sprachfrage: Tonspur statt Zweitkanal

Das ist der stärkste einzelne Fund der Recherche — **Stufe A, offizielle YouTube-Quellen:**

- YouTube **Multi-Language Audio (MLA)** ist seit **10.09.2025** für alle offen. Offizieller Benchmark: Kanäle mit Mehrsprachigkeit ziehen **„over 25 % of their watch time … from views in the video's non-primary language"**. Jamie Oliver verdreifachte seine Reichweite, Mark Rober fährt >30 Sprachen.
- **Auto-Dubbing** deckt **27 Sprachen** ab, davon 8 mit „Expressive Speech" — **Deutsch ist dabei.** Offiziell: „more than 6 million daily viewers" schauen mindestens 10 Minuten in einer gedubbten Spur (Stand Dezember, Post vom 04.02.2026).

**Was das praktisch heißt:** Der deutsche Markt ist über eine **Tonspur auf dem englischen Kanal** erreichbar — mit dem Backkatalog, den Watchstunden und der Algorithmus-Historie des bestehenden Kanals. Ein eigener deutscher Kanal fängt bei null an und deckelt sich zusätzlich beim RPM.

**Regel:** Auto-Dubbing an, aber **„Publish manually"** (Qualitätskontrolle), nur Expressive-Speech-Sprachen. Benchmark 25 % Watchtime aus Nicht-Primärsprache; wenn nach 4 Folgen unter 10 % → abschalten. Ein separater Sprachkanal erst bei ~1 Mio. Views/Monat.

> ⚠️ **Das betrifft BLACKBOX direkt.** Das Konzept in `research/zweitkanal-technik-katastrophen-konzept.md` ist auf Deutsch gebaut und verliert dadurch ~6 Punkte (29/40 statt ~35/40). Derselbe Kanal **auf Englisch, mit deutscher Tonspur**, hätte den großen Markt, das höhere RPM *und* das deutsche Publikum. Die deutschen Fälle (Überlingen, Eschede, Ramstein) funktionieren auf Englisch genauso — sie sind international kaum erzählt, was sie eher wertvoller macht. **Empfehlung: BLACKBOX auf Englisch drehen, Deutsch als Tonspur.** Entscheidung liegt bei dir; ich habe die Zahlen dazu geliefert.

---

## 8. Der Asset-Pool-Katalog (verifiziert, mit maschinellem Zugang)

Das operative Herzstück von G2. Ein Pool auf dieser Liste heißt: Kanal ist produzierbar.

| Pool | Inhalt | Rechtsstatus | Zugang |
|---|---|---|---|
| **NASA** images.nasa.gov / SVS | Foto, Video, Sondendaten | PD (US-Gov) — **Ausnahmen s. u.** | REST-API |
| **NOAA Ocean Exploration** | ROV-Tiefsee, roh + produziert, ProRes422 | „All video on the portal is in the public domain" — **Credit „NOAA Ocean Exploration" Pflicht**, einzelne Objekte urheberrechtlich geschützt | Portal + NCEI-Bulk |
| **NARA** (US-Nationalarchiv) | Filme, Fotos, Akten; 1,9 Mio. Bilder in DPLA | „no known copy restrictions" | API read/write + Bulk |
| **Smithsonian Open Access** | >4,5 Mio. Objekte, 19 Museen | CC0 | api.si.edu + AWS Open Data |
| **Library of Congress** | Fotos, Karten, Filme | gemischt, großer PD-Anteil | JSON-API, **ohne Key** |
| **CourtListener / RECAP** | Urteile, Dockets, Oral Arguments | US-Gerichtsentscheidungen PD | REST v4 + Quartals-Bulk |
| **CIA CREST** | ~930k Dokumente / >12 Mio. Seiten | PD | Reading Room + IA-Volltext |
| **NTSB** | Unfallberichte alle Verkehrsträger ab 1962 | PD | REST-API, **kein Key** |
| **CSB** | 101 professionelle 3D-Unfallanimationen | PD (Behördenwerk) | csb.gov + IA-Spiegel |
| **USGS** | Vulkane, Geohazard | PD | API |
| **LLNL** | 750 deklassifizierte Nukleartest-Filme | PD | Lab-Release |
| **Europeana** | EU-Kulturerbe | 14 Rights-Statements, **nur 4 frei nutzbar** | API, Rights-Filter Pflicht |
| **Internet Archive / Prelinger** | Ephemeral Films | **gemischt** — Derivate ausdrücklich freigegeben | advancedsearch-API |
| **Wikimedia Commons** | Bilder/Video | **pro Datei** | MediaWiki-API |
| arXiv / PubMed Central | Papers | **Lizenz pro Paper** | API |

### Die vier Rechtsfallen (jede hat schon Kanäle gekostet)

1. **Contractor-Ausnahme.** US-Behördenwerke sind PD — aber: „Contractors and grantees are not considered Government employees; generally, they hold copyright to works they produce for the Government."
2. **⚠️ NASA-Insignia — betrifft SIGNAL direkt.** „The NASA Insignia, Logotype, identifiers, and imagery are **not** in the public domain." NASA **untersagt ausdrücklich die Verwendung ihrer Insignien zusammen mit KI-generierten Bildern** und fordert KI-Kennzeichnung. Erkennbare Personen in NASA-Material = Right-of-Publicity-Risiko. **Aktion: Alle vier Master und das Branding auf NASA-Logos in KI-Szenen prüfen.**
3. **URAA-Falle.** 1996 wurde US-Copyright an ausländischen Werken automatisch wiederhergestellt. **PD im Herkunftsland ≠ PD in den USA** — und YouTubes Forum sind die USA. Prüfliste beim Copyright Office.
4. **„Liegt auf archive.org" ist wertlos.** Das Internet Archive „does not make guarantees as to the copyright status of items"; Rechteangaben stammen meist vom Uploader. **Archive.org ist ein Fundort, keine Quelle.**

**Und ESA ist nicht PD:** ESA/Hubble-Material ist **CC BY 4.0** — Namensnennung ist Pflicht, Endorsement-Wirkung für kommerzielle Produkte untersagt, Logos nur mit Extra-Erlaubnis, Musik/Code/Papers fallen nicht darunter.

### Der Pool ist kein Burggraben

Er ist **Eintrittskarte und Kostenboden** — per Definition für jeden Konkurrenten offen. Verteidigbar ist nur die **Verarbeitung**:

- **Recherchetiefe** — „Recherche, die das Publikum nicht mit einer Suche hätte machen können"
- **Der eigene, QC-geprüfte Clip-Katalog** (`produktion/clip-katalog.md`) — das ist der eigentliche Vermögenswert, ab Tag 1 pro Kanal mitführen
- Format und Marke

**Anti-Slop-Klausel (Pflicht, weil ein PD-Pool zugleich ein Flag-Risiko ist):** Pro Folge mindestens **eine Aussage, die nur aus Primärquellen-Arbeit stammen kann** — eine Berichtsnummer, ein Sitzungsprotokoll, ein Datensatz. Eine PD-Kompilation ohne diese Klausel nie veröffentlichen. Reines „KI-Stimme über Archivmaterial" ist Reused Content, egal wie legal das Material ist.

*Ehrliche Einordnung:* Ob PD-Pools von YouTube **explizit** als Reused-Content-Auslöser genannt werden, ließ sich **nicht** belegen — das ist Community-Interpretation. Offiziell greifbar sind nur „meaningful difference" und „template with little to no variation / easily replicable at scale".

---

## 9. Werkzeug: was ihr schon habt, was fehlt

**Ihr habt ~70 % des Profi-Werkzeugs gebaut** — nur als Einmal-Analyse. In `analyse/` steckt:

| Datei | Was es leistet | Rolle im Playbook |
|---|---|---|
| `fetchlib.py` | Gedrosselter Scraper (2 req/s, Backoff, Consent-Wall-Erkennung) | Basis, kein API-Key nötig |
| `gather.py` | Pro Kanal: Abos, Beitrittsdatum, Videoliste mit exakten Views via RSS, Monetarisierungs-Signale | Datenerhebung §3 |
| `compute.py` | Median, p25/p75, `hit_ratio`, `median_to_max_ratio`, `uploads_pro_tag`, `days_channel_to_hit`, `desc_boiler_hash` | **Genau die Metriken aus §3** |
| `pattern_report.py` | Titel-Formel-Quoten, Kadenz, Subs/Monat | Muster-Erkennung |

`compute.py` klassifiziert schon: Median <10k **und** hit_ratio <5 % → `LOTTERIE`; Median ≥100k → `SYSTEM`. Das ist die 2×2-Diagnose in Ansätzen.

**Was fehlt — drei Dinge:**
1. **Discovery.** `gather.py` braucht eine Handle-Liste als Input. Es fehlt der Schritt „Nischen-Keyword → Kandidaten-Kanäle".
2. **Kanalalter-Achse.** `days_channel_to_hit` existiert, wird aber nicht zur Diagnose „frühe Welle vs. gesättigt" genutzt.
3. **Nischen-Aggregation.** Alles ist pro Kanal; es fehlt das Urteil pro **Nische**.

→ Nächster Schritt: `analyse/nischen_scan.py`, das auf `fetchlib`/`gather` aufsetzt und pro Nischen-Keyword das 2×2-Urteil ausgibt.

**Tooling-Realität (korrigiert):**
- **YouTube Data API v3:** Quoten wurden granular umgestellt (Sekundärquellen datieren auf ~01.06.2026). Aktuell laut Google-Doku: **100 `search.list`-Calls/Tag** als *eigenes* Kontingent, plus **10.000 Einheiten/Tag** für alles andere. `videos.list` kostet 1 Einheit für **bis zu 50 Video-IDs** → Statistik-Auswertung ist praktisch gratis, **die Suche ist der harte Deckel.** Zwei-Stufen-Pipeline ist Pflicht, weil `search.list` keine Views/Dauer liefert. Grenze ~500 Ergebnisse pro Suchanfrage.
- **Kostenlos und unterschätzt:** vidIQ-Extension (Outlier-Score im Free-Tier), YouTube-Studio-Forschungstab (Suchvolumen Low/Medium/High, markiert „content gaps"), Test & Compare (3 Thumbnail-Varianten, Sieger nach Watch-Time, bis 14 Tage, 0 €).
- **Untauglich für Nischenjagd:** Playboard listet nur Kanäle ab **1.000 Abos und 1 Mio. kumulierten Views** — genau die kleinen Kanäle, die das Signal tragen, fehlen dort.
- **Preise nicht übernehmen:** Fast alle kursierenden Tool-Preise waren veraltet oder unbelegt. Bestätigt: 1of10 Free / $29 / $69. Alles andere selbst auf der Herstellerseite prüfen.
- **Methodenrisiko:** Wenn alle dieselben Tools benutzen, finden alle dieselben Outlier. Ein Vorsprung entsteht nicht aus dem Tool, sondern aus dem Pool-Zugang und der Recherchetiefe.

---

## 10. ⏰ Zeitkritisch (betrifft SIGNAL jetzt, nicht erst den nächsten Kanal)

1. **EU-KI-VO Art. 50 gilt ab 02.08.2026 — in drei Tagen.** Offenlegungspflicht für KI-generierte/manipulierte Inhalte, Bußgeld bis 15 Mio. € oder 3 % Umsatz. Ihr seid als EU-Deployer direkt betroffen. Markierungspflicht für Alt-Systeme ab 02.12.2026. **Vor dem 02.08.2026 veröffentlichte Inhalte sind nicht rückwirkend zu labeln** — F1–F4 sind also geschützt, alles ab F5 braucht die Kennzeichnung. Die KI-Disclosure steht bereits in `UPLOAD-CHECKLISTE.md`; sie ist ab jetzt **rechtlich**, nicht nur policy-seitig verbindlich.
2. **NASA-Insignia-Regel prüfen** (§8, Falle 2): NASA untersagt Insignien in Kombination mit KI-Bildern. Betrifft potenziell alle vier Master und das Branding.
3. **Voice-Clones sind noch nicht von der Likeness-Detection abgedeckt** — das ist eine Lücke, die sich schließen wird. Keine Kanal-Strategie darauf bauen.

---

## 10b. Die Käufer-Ebene — der einzige Ort, wo Nischenbewertung mit Geld quittiert wird

Wer Kanäle kauft, muss Nischen bewerten und haftet für Fehler. Das ist der härteste verfügbare Maßstab.

### Was tatsächlich bezahlt wird

| Quelle | Multiple | Basis |
|---|---|---|
| Flippa, 3 abgeschlossene YouTube-Deals Q1/2026 | **1,19× · 1,48× · 1,71× Jahresgewinn** | ⚠️ alle drei von **einem** Broker, n=3 — ein Maklerbuch, kein Markt |
| Empire Flippers Scoreboard (tatsächlich verkauft) | **26,3× Monatsgewinn** (typisch) · 28,3× premium · **36,7×** ab $1M · 14,5× distressed | 2.653 Verkäufe, $593.000.849 — aber **alle Asset-Klassen**, nicht YouTube-spezifisch |
| Flippa-Aggregat 2025 | YouTube 1,8× Ø, 3,9× Top-Quartil; YouTube-Volumen **+155 %** | Basis (annual/monthly, sold/asking) von Flippa **nicht offengelegt** |

**Planwert: 1,2×–2,2× Jahresgewinn** (self-serve bis vetted-brokered), 3,0× nur in der $1M+-Klasse.
**Ehrliche Lücke:** Für *tatsächlich verkaufte YouTube-Kanäle* existiert **keine veröffentlichte Multiple-Statistik.** Die kursierenden „20–40× Monat" stammen ausschließlich aus Rechner- und SEO-Seiten. 26,3× Monat = 2,19× Jahr ist ein *asset-klassenfremder* Mittelwert — als Größenordnung brauchbar, nicht als YouTube-Zahl.

### Was den Preis zerstört (Broker-Dokumente, wörtlich)

- *„High personalization/personality-dependent content"* → **G1 und G7 haben hier ihren Geldgrund**
- *„Uneven view distribution (one viral video dominating)"* → deshalb ist der **Median** die Metrik, nicht der Hit
- Copyright-Strikes: *„Make sure 90 days have passed since your strike was issued before listing"*
- Pflicht für die Übertragung: **Brand Account** (kein persönliches Google-Konto), 0 aktive Strikes, *„All content is original and owned by the seller (no unlicensed footage or music)"*, 12 Monate AdSense-Exporte, *„Content production process documented"*
- Red Flag: *„Revenue too high for view count"*

### Die Kapitalseite ist kein Käufer für uns — mit einer nutzbaren Ausnahme

Spotter hat >$940 Mio. an Creator ausgezahlt (Variety 10/2024, Firmenangabe), aber 10/2025 Studio geschlossen und Personal abgebaut; Jellysmacks JellyFi-Katalogprogramm wurde Anfang 2024 zu nicht offengelegten Konditionen verkauft. **Für Kanäle unserer Größe war dieser Markt nie zugänglich.**
Nutzbar bleiben Spotters **Primärkriterien** (spotter.com/creator-capital): *„long-form YouTube videos are a must"*, Shorts-only disqualifiziert, **Rechte-Vollbesitz Pflicht**. Das deckt sich exakt mit dem Public-Domain-Asset-Setup (§8) — unser Pool-Gate ist damit money-verified, nicht nur bequem.
*(Nicht tragfähig und daher gestrichen: die kursierende Spotter-Schwelle „1 Mio. Views/Monat" ist von 2022 und gehört zu einer de-priorisierten Produktlinie; „$15.000–$40 Mio." ist unbelegt.)*

### Portfolio-Risiko: Operator-Ansteckung ist die reale Gefahr

Der harte Beleg ist **nicht** das Google-Paper zur Cluster-Terminierung — dessen Zahlen (50k Cluster / 130k Kanäle) sind aus der aktuellen Fassung **herausredigiert**, es ist nicht peer-reviewed, und „YouTube" kommt darin **nicht vor**. Der Mechanismus (Cluster statt Einzelvideo; Titel-/Beschreibungs-Terme, Upload-Pacing, geteilte Infrastruktur) bleibt aber plausibel.

Der empirische Beleg ist **True Crime Case Files: fünf Kanäle EINES Betreibers, alle terminiert nach einer einzigen Aufdeckung** (Grund offiziell *„child safety … sexualization of minors"*, nicht „KI"). Dazu das Zwei-Stufen-Muster von Screen Culture / KH Studio: Demonetisierung → Relabeling → Rückfall → Termination (Dez. 2025).

→ **Regeln:** nichts zwischen eigenen Kanälen teilen (Skript-Skelett, VO-Stimme, Template, Musikbett, Thumbnail-Grammatik, Upload-Rhythmus) · getrennte Marken-/AdSense-Struktur · Beweis-Akte pro Folge.

### Content ID ist Normalbetrieb, kein Nischen-Filter

**2.502.941.368 Claims in 2025**, ~99 % automatisiert, **>90 % monetarisiert der Claimant**, **>6 % „likely false assertion of copyright ownership"** (YouTube-Transparenzbericht, 06.06.2026). Ein Claim ist erwartbar — plane den Widerspruchsweg ein, statt eine Nische deswegen zu verwerfen.

### Haftungs-Deckel: warum G1 Geld wert ist

- **Upchurch, Bundesjury Nashville, 18.05.2026: $17,5 Mio.** — und entscheidend: Kläger wurden als **Privatpersonen** eingeordnet → *actual malice* nicht erforderlich, **Fahrlässigkeit genügt.**
- **Tokio, 17.11.2022: ¥500 Mio.** für 54 Werke (¥200/View); der Uploader hatte ~¥7 Mio. verdient → Faktor **~71**.

Das sind die Zahlen hinter „keine benannten lebenden Personen" und „keine gerippten Streams".

---

## 11. Was NICHT gilt (Hygiene-Liste — damit wir nicht rückfällig werden)

Diese Zahlen kursieren breit, sind aber von der Gegenprüfung verworfen. **Nie als Grundlage verwenden:**

- „Outlier = 3× Median" als Branchenkonvention · „Paddy Galloway 5×–15×" · „8k Abos / 300k Views"-Fallbeispiel (rhetorisch, quellenlos)
- „search.list kostet 100 Einheiten" (veraltet) und alle darauf gebauten Quota-Rechnungen
- Die Open-Source-Filterschwellen (≤50k Abos / ≥75k Median / ≥10× / ≤12 Monate) — die gelten für **Shorts**, nicht Longform
- „74,8 % der Kanäle scheitern" als Neustart-Basisrate · „Faktor 167" als Präzisionszahl
- Doku/Science-RPM „$4–6" als Konsens (Gegenbeleg: Median $10,22) · „US:Indien = 10–25×" (Faktor-5-Widerspruch zwischen Quellen)
- „16 Kanäle terminiert" (korrekt: **11 terminiert + 5 Inhalts-Wipes**) · „~10 Mio. $ Jahresumsatz" (Dritt-Schätzung) · „<1 % Overturn-Rate" bei Einsprüchen (Metrik-Verwechslung)
- Zuschauer-Slop-Ratings als bestätigtes **Rankingsignal** (YouTube hat die Gewichtung nicht offengelegt) — nur als Selbsttest-Heuristik brauchbar
- Shorts-RPM „$0,10 vs. $20 = 200×" als Punktwert (Richtung stimmt, Zahl nicht) · alle Tool-Preise außer 1of10
- Kurzgesagt als Referenz für unsere Kostenstruktur (~70 Mitarbeiter, München)

**Neu aus der Geld-Recherche verworfen:**
- „Nischenwert = Monatsgewinn × 26" und „unter $2.000/Monat unverkäuflich" — der 26,3×-Wert ist ein **asset-klassenfremder** Mittelwert; die $2.000-Schwelle ist **Empire-Flippers-Hauspolitik**, keine Marktschwelle (Flippa verkauft darunter). Die 91-%-Ablehnungsquote stammt aus **2020/21**
- Multiples pro Nische aus den Empire-Flippers-Kategorien (7×–36×) — das sind **Angebotspreise**, n=1–4 pro Kategorie
- „Ziel muss ≤10 % des Nischen-Deckels sein" und „Median der Top-10-Videos" — **im Galloway-Transkript nicht vorhanden**; seine 10 % beschreiben sein eigenes *Headroom*, nicht eine Obergrenze
- Galloways Trichter als eine Zahl — er spreizt selbst zwischen *„maybe you're left with 3 or 4 videos"* (aus 100) und einem *„100-10-1 framework"*. Bandbreite **10×–30×** ausweisen
- „30 % / 5 % / 95 % / 80-20-Zeitallokation" (Colin & Samir) — Redaktions-Paraphrase, keine Primäraussage
- Alle MrBeast-Zahlen (818 Sekunden, „simple") als Norm für einen Kanal ohne Publikum — das Handbuch koppelt sie ausdrücklich an *„our audience is massive"*
- „16 % Policy-Tod pro Quartal" — Einmalwelle als Rate missdeutet, plus Rechenfehler (17≠16)
- „50.000 Cluster / 130.000 Kanäle" als Faktum — aus der aktuellen Paper-Fassung entfernt
- „Education hat die höchsten Shorts-Opportunitätskosten" — abgeleitet aus einer **leeren Zelle** (n=0 Shorts-Kanäle im Education-Sample)
- Die Upload-U-Kurve als „Gewinnzone" — AIR wörtlich: *„upload count and RPM barely correlate at all"*, und die Achse ist RPM, nicht Umsatz
- Jede Sponsoring-CPM-Zahl nach Nische — existiert nicht; IZEAs eigene Zahlen widersprechen sich um ~3×
- Noah Morris' $250k/Monat und alle NexLev-Zahlen — Selbstauskunft eines Kursverkäufers, widersprüchliche Kanalzahl (6 vs. „20+")
- „CoComelon+Blippi für $120 Mio." — das war eine **Finanzierungsrunde**, kein Kaufpreis; alle Moonbug-Kaufpreise sind unbestätigt
- BBTV-RPM ($0,53) als Realitätsanker — 2023, Firma delistet, andere Metrik-Definition (Konzernumsatz/alle Netzwerk-Views)

---

## 12. Die Kurzfassung — Nischen-Check auf einer Seite

> **Ausführbar als Skill:** `.claude/skills/nische-finden/SKILL.md`. Der Satz „finde eine perfekte Nische" löst die Prozedur aus. Dieses Playbook ist die Herleitung, die Skill ist die Ausführung.

```
STUFE 0 · WELCHES SPIEL?   Extraktion (Cash, 1-3 J. Fenster) oder Equity (verkäuflich)?
                            Bei Extraktion faellt G3 weg. Nicht raten - fragen.
          Parameter: Kosten/Folge · Uploads/Monat · Ziel · RPM = P25 der Nische

STUFE 1 · KILL-GATES (binär, ein Nein = Ende, keine Aufrechnung)
  [ ] G1  Keine benannten lebenden Personen      (Upchurch $17,5 Mio., Fahrlässigkeit genügt)
  [ ] G2  Freier Pool: API/Bulk + PD/CC0 + volle Rechte   (Spotter-Kriterium)
  [ ] G3  Originalitäts-Substrat  — NUR im Equity-Spiel bindend
  [ ] G4  Englisch                               (Deutsch = MLA-Tonspur, nicht Kanal)
  [ ] G5  Kein MFK / YMYL-Rat / KI-Persona zu Gesundheit-Recht-Finanzen-Politik
  [ ] G6  Trägt 150 Folgen à ≥3 Min
  [ ] G7  Ohne Person übertragbar                (Broker-Wertminderer)

STUFE 2 · HEADROOM + SCAN
  [ ] Galloway-Sichtung: Suche → Longform-Filter → nach Views sortieren (Decke lesen)
  [ ] python3 analyse/nischen_scan.py "<kw>" --limit 25 --rpm 2.31
      NACHFRAGE (trägt die Nische?)  ×  FENSTER (kommen Neue durch?)
      🟢 System · 🟠 tragfähig/Fenster eng · 🟡 frühe Welle · 🔴 keine Nachfrage

STUFE 3 · ARITHMETIK  (P25, nicht Median!)
  [ ] Break-even        = Kosten ÷ (RPM/1000)
  [ ] Nötiger Median    = (Ziel$ ÷ RPM × 1000) ÷ Uploads
  [ ] Liegt das über dem BESTEN aktiven Kanal-Median der Nische?
      → dann ist das Ziel dort arithmetisch unerreichbar. Ziel senken /
        Uploads erhöhen / Nicht-AdSense einplanen. Nicht weiterhoffen.
  [ ] Saison: Januar −34 % gegen November

STUFE 4 · PACKAGING-TEST (die eigentliche Profi-Methode, 0 €)
  [ ] 20 Titel in <30 Min · 10 Thumbnail-Konzepte
  [ ] Jede Folge in Titel+Thumbnail versprechbar, ohne das Verdict zu verraten?
  [ ] ≥3 unterscheidbare Folgen-Formate (Rotation — "rehashing formats always dies")
  [ ] Ideen-Backlog 10×–30× der Produktionsrate

STUFE 5 · GELD & PORTFOLIO
  [ ] Stop-Loss: 20–30 Folgen × Kosten, hart. Abbruch-Review bei Folge 10
  [ ] Nur EINE Test-Nische parallel
  [ ] Kanal-2-Bedingung erfüllt (Zustand, kein Datum)
  [ ] Nichts geteilt zwischen eigenen Kanälen: Skript-Skelett, Stimme, Template,
      Musikbett, Thumbnail-Grammatik, Upload-Rhythmus  (Operator-Ansteckung!)
  [ ] Beweis-Akte pro Folge archiviert
```

---

## Quellen (Stufe A — bindend)

**Policy & Enforcement:** [Reused/Inauthentic Content (Primärtext)](https://support.google.com/youtube/answer/1311392) · [Advertiser-friendly Guidelines](https://support.google.com/youtube/answer/6162278) · [Halprin/Three Buckets (TechCrunch 20.07.2026)](https://techcrunch.com/2026/07/20/youtube-clarifies-policies-around-ai-slop-and-upsetting-videos/) · [Sensitive-Content-Update 01/2026 (Tubefilter)](https://www.tubefilter.com/2026/01/15/youtube-sensitive-content-ad-monetization-guidelines-update/) · [Mohan-Jahresbrief 21.01.2026](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/) · [Likeness Detection für alle 18+](https://www.socialmediatoday.com/news/youtube-expands-likeness-detection-to-all-users-over-18/820440/) · [Altered-Content-Disclosure](https://support.google.com/youtube/answer/14328491) · [Google Research: Cluster-Terminierung](https://research.google/pubs/scalable-detection-of-adversarial-synthetic-slop-and-coordinated-media-abuse-a-lora-enabled-multimodal-defense-system/)
**Mehrsprachigkeit:** [MLA-Rollout blog.youtube](https://blog.youtube/news-and-events/multi-language-audio-open-to-all/) · [Auto-Dubbing 27 Sprachen / Expressive Speech](https://blog.youtube/news-and-events/auto-dubbing-expansion/)
**API & Tools:** [Quota-Kosten (Google Dev)](https://developers.google.com/youtube/v3/determine_quota_cost) · [Getting Started/Quota](https://developers.google.com/youtube/v3/getting-started) · [vidIQ Outlier-Bänder](https://support.vidiq.com/en/articles/9660010-outliers) · [Playboard-Aufnahmeschwelle](https://playboard.co/en/about)
**Recht & Assets:** [NASA Brand Center — Insignia/KI-Regel](https://www.nasa.gov/nasa-brand-center/images-and-media/) · [Copyright Office URAA Circ. 38b](https://www.copyright.gov/circs/circ38b.pdf) · [Internet Archive Rights-Disclaimer](https://help.archive.org/help/rights/) · [ESA/Hubble CC BY 4.0](https://esahubble.org/copyright/) · [NOAA Media Kit](https://oceanexplorer.noaa.gov/news/media-kit.html) · [NARA Developer](https://www.archives.gov/developer) · [Smithsonian Open Access](https://edan.si.edu/openaccess/docs/) · [LoC APIs](https://www.loc.gov/apis/) · [CourtListener Bulk](https://www.courtlistener.com/help/api/bulk-data/) · [Europeana Rights](https://pro.europeana.eu/page/available-rights-statements) · [EU-KI-VO Art. 50 FAQ](https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act)
**Studien:** [COPPA/MFK-Studie, Management Science 04.05.2026](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.05295) · [McGrady et al., How Big is YouTube (JQD 2023)](https://journalqd.org/article/view/4066)
**Stufe B (Heuristik, als solche gekennzeichnet):** [AIR Media-Tech RPM-Daten 01.07.2026](https://air.io/en/air-data-findings/which-youtube-niche-makes-the-most-money-in-2026-ranked-by-real-rpm-and-cpm) · [Mediacube RPM 10/2025](https://mediacube.io/en-US/blog/youtube-rpm) · [vidIQ Niche Finder](https://vidiq.com/youtube-niche-finder/)

---

## Quellen der Geld-Ebene (§1b, §10b)

**Transaktionen/Aggregate:** [Flippa Closed Deals Q1/2026](https://flippa.com/blog/closed-deals-on-flippa-q1-2026/) · [Flippa M&A Insights 2025](https://flippa.com/blog/2025-online-business-ma-insights-from-flippa/) · [Empire Flippers Scoreboard (verkauft)](https://empireflippers.com/scoreboard/) · [EF Listing-Anforderungen](https://empireflippers.com/business-listing-requirements/) · [EF Kanal verkaufen — Wertminderer](https://empireflippers.com/sell-youtube-channel/) · [Flippa Käufer-DD](https://flippa.com/blog/buy-youtube-channel/) · [Spotter Creator Capital (Primärkriterien)](https://www.spotter.com/creator-capital) · [Variety: Amazon/Spotter $940 Mio.](https://variety.com/2024/digital/news/amazon-invests-spotter-digital-creator-economy-1236194916/) · [Tubefilter: Spotter Studio geschlossen](https://www.tubefilter.com/2025/10/22/spotter-studio-shutdown-layoffs/)
**RPM-Aggregat:** [AIR: echte RPM-Daten](https://air.io/en/air-data-findings/how-much-does-youtube-really-pay-in-2026-real-rpm-data-from-300-channels) · [AIR: Nischen-Ranking](https://air.io/en/air-data-findings/which-youtube-niche-makes-the-most-money-in-2026-ranked-by-real-rpm-and-cpm) · [AIR: Shorts vs. Longform](https://air.io/en/air-data-findings/youtube-shorts-rpm-vs-long-form-how-much-do-shorts-earn-in-2026)
**Primäraussagen:** [Galloway-Volltranskript (Creator Science)](https://podcast.creatorscience.com/paddy-galloway-2/) · [MrBeast-Handbuch (Leak-Auswertung)](https://www.tubefilter.com/2024/09/17/mrbeast-internal-production-guide-leaked-key-points/) · [ViewStats Outlier-Doku](https://viewstats.zendesk.com/api/v2/help_center/en-us/articles/22966946776091.json) · [YouTube A/B Test & Compare](https://support.google.com/youtube/answer/16391400)
**Policy/Recht:** [Inauthentic Content (Primärtext)](https://support.google.com/youtube/answer/1311392) · [YouTube-Klarstellung 07/2025](https://www.socialmediatoday.com/news/youtube-clarifies-monetization-update-inauthentic-repeated-content/752892/) · [Google Research: S-CTS](https://storage.googleapis.com/gweb-research2023-media/pubtools/1039291.pdf) · [COPPAcalypse (Management Science)](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.05295) · [Nielsen Gauge Mai 2026](https://www.nielsen.com/news-center/2026/streaming-embarks-on-annual-summer-ascent-in-nielsens-may-2026-gauge-reports/)
**Post-Mortems:** [XDA: 16 der Top-100 entfernt](https://www.xda-developers.com/youtube-just-deleted-over-4-7-billion-views-worth-ofai-slop-videos/) · [THR: Faceless Creator & KI-Schaden](https://www.hollywoodreporter.com/business/digital/faceless-creators-youtube-ai-damage-1236617586/)

---

## CHANGELOG
- **30.07.2026 (Abend)** — Geld-Ebene ergänzt (12 Agenten, Fokus „Leute mit nachweisbarem Geld statt Blogger", ~335 Tool-Calls). **Drei Befunde widerlegen die Erstfassung:** (1) Top-Verdiener bewerten Nischen überhaupt nicht — MrBeast-Handbuch enthält „niche" null Mal, Galloway sagt *„no niche where I can't get traction"* → Scoring auf Kommunikationsmittel herabgestuft, Entscheidungen fallen an Gates + Arithmetik; (2) Streuung innerhalb einer Nische (8,4× bei Education & Science) übersteigt die zwischen Nischen → Planwert ist **P25 ($2,31)**, nicht der Median; (3) der einzige geldverifizierte Faceless-Operator lebt von Sleep-Dokus und Compilations, und YouTube erlaubt die ausdrücklich → **G3 auf „nur im Equity-Spiel bindend" korrigiert**, Zwei-Spiele-Unterscheidung eingeführt. Neu: §10b Käufer-Ebene (Multiples 1,2×–2,2× Jahresgewinn, Wertminderer wörtlich, Operator-Ansteckung via True Crime Case Files, Content-ID-Realität, Haftungs-Deckel Upchurch $17,5 Mio.), G7 (Übertragbarkeit), G6 auf 150 Folgen. Ausführbar gemacht als `.claude/skills/nische-finden/`.
- **30.07.2026** — Erstfassung. 12 Agenten (6 Recherche + 6 adversariale Gegenprüfung), ~320 Tool-Calls. Kernergebnis: Die kursierende „Profi-Methode" ist überwiegend Vendor-SEO ohne Primärdaten → Beweis-Hierarchie A/B/C eingeführt, eigene Messung schlägt gekaufte Rubriken. 5-Stufen-Prozess mit 6 binären Kill-Gates VOR der Nachfrage-Recherche (validiert gegen die eigenen Fälle: Krimi stirbt an G1/G2, BLACKBOX an G4). MLA-Fund: deutscher Markt über Tonspur statt Zweitkanal. Asset-Pool-Katalog mit 15 Pools + 4 Rechtsfallen. Zeitkritisch: EU-KI-VO Art. 50 ab 02.08.2026, NASA-Insignia-Regel gegen KI-Bilder.
