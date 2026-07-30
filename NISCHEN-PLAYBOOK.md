# 🎯 Nischen-Playbook — wie wir Nischen finden (kanal-unabhängig)

> **Zweck:** `SPACE-PLAYBOOK.md` sagt, wie wir *einen* Kanal bauen. Dieses Dokument sagt, **welchen Kanal wir überhaupt bauen** — reproduzierbar, für jeden künftigen Kanal.
> **Datenbasis:** 12 Agenten (6 Rechercheure + 6 adversariale Gegenprüfer), ~320 Tool-Calls, 30.07.2026. Rohmaterial + Prüfprotokolle: siehe §11.
> **Lesereihenfolge bei einer neuen Nischen-Idee:** §1 → §2 (Kill-Gates) → §3 (Nachfrage) → §4 (Arithmetik) → §5 (Papier-Test) → §6 (Geld). Nie überspringen, nie umsortieren.

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

## 2. Stufe 1 — Die 6 Kill-Gates (binär, VOR jeder Nachfrage-Recherche)

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

### G3 · Originalitäts-Substrat (der Interchangeability-Test)
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

### G6 · Trägt ≥50 Folgen
Wenn der Themenpool nach 20 Folgen leer ist, war es ein Video-Format, keine Nische.

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

---

## 12. Die Kurzfassung — Nischen-Check auf einer Seite

```
STUFE 1 · KILL-GATES (binär, ein Nein = Ende)
  [ ] G1  Keine reale lebende Person im Zentrum
  [ ] G2  Freier Asset-Pool: API/Bulk + Bewegtbild o. 1.000 Stills + PD/CC0 + 50 Themen
  [ ] G3  Originalitäts-Substrat: Primärquelle / Verdict / eigene Messung pro Folge
          → Interchangeability-Test: <5 austauschbare Kanäle?
  [ ] G4  Englisch (Deutsch = Tonspur, nicht Kanal)
  [ ] G5  Kein MFK / YMYL-Beratung / ineligible Kategorie
  [ ] G6  Trägt ≥50 Folgen

STUFE 2 · NACHFRAGE (2×2)
  [ ] ≥3 Kanäle <50k Abos mit ≥100k-Video in 12 Mon., davon ≥1 unter 12 Mon. alt
  [ ] 2×2-Feld bestimmt: System / Frühe Welle / Gesättigt / Keine Nachfrage
      → Rot oder Orange: Ende

STUFE 3 · ARITHMETIK
  [ ] Break-even = Kosten ÷ (RPM/1000)          mit RPM = unteres Drittel × 0,7
  [ ] Nötiger Median = (Ziel$ ÷ RPM × 1000) ÷ Uploads
  [ ] Nischen-Median der 10k–100k-Tier liegt DARÜBER?  → sonst Ende

STUFE 4 · PAPIER-TEST (0 €, 1 Tag)
  [ ] 30 Themen · 20 Titel in <30 Min · 10 Thumbnail-Skizzen

STUFE 5 · GELD
  [ ] Stop-Loss 700–1.050 € / 20–30 Folgen, Review bei Folge 10
  [ ] Nur EINE Test-Nische parallel
  [ ] Kanal-2-Bedingung erfüllt (Zustand, nicht Datum)
  [ ] Kein geteiltes Template/Stimme/Rhythmus mit anderen eigenen Kanälen
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

## CHANGELOG
- **30.07.2026** — Erstfassung. 12 Agenten (6 Recherche + 6 adversariale Gegenprüfung), ~320 Tool-Calls. Kernergebnis: Die kursierende „Profi-Methode" ist überwiegend Vendor-SEO ohne Primärdaten → Beweis-Hierarchie A/B/C eingeführt, eigene Messung schlägt gekaufte Rubriken. 5-Stufen-Prozess mit 6 binären Kill-Gates VOR der Nachfrage-Recherche (validiert gegen die eigenen Fälle: Krimi stirbt an G1/G2, BLACKBOX an G4). MLA-Fund: deutscher Markt über Tonspur statt Zweitkanal. Asset-Pool-Katalog mit 15 Pools + 4 Rechtsfallen. Zeitkritisch: EU-KI-VO Art. 50 ab 02.08.2026, NASA-Insignia-Regel gegen KI-Bilder.
