# Projekt: YouTube-KI-Kanal (Space-Doku)

## Kontext & Ziel
Wir bauen einen **faceless, 100 % KI-produzierten YouTube-Kanal** mit dem Ziel **$10.000+/Monat** (AdSense).
Nach ausführlicher Nischen-Recherche (Juli 2026) ist die gewählte Nische: **Space / Science-KI-Doku** (englischsprachig).

## Entschiedene Eckpunkte (nicht mehr in Frage stellen, außer der User will es)
- **Nische:** Space-KI-Doku (Modell A „NASA/JWST just…" + Modell B „Explainer"). Begründung: höchste $10k-Wahrscheinlichkeit + leichteste KI-Produktion (keine Gesichter nötig) + gemeinfreie NASA-Footage + sauberes IP.
- **Sprache:** Englisch (US-Publikum, höchste RPM).
- **Tools:** Claude (Skript/Titel) → Higgsfield (Kosmos-Visuals) + gemeinfreie NASA/ESA-Footage → KI-TTS-Voiceover → CapCut (Schnitt).
- **Video-Länge (AKTUALISIERT 14.07.2026, User-Entscheid):** **ab Folge 3 Ziel 13–15 Min** (Daten: Hit-Sweetspot 10–16 Min, Median 1,3M vs. 19k in der 20–27-Min-Zone — `research/konkurrenz-muster.md` M2). Folge 1 (13:12) ✓, Folge 2 bleibt wie gebaut ~19–20 Min (Bestandsschutz). 2 Mid-Rolls reichen. Keine 2h-Sleep-Docs.
- **Shorts (PRÄZISIERT 21.07.2026, User-Entscheid):** Shorts NIE als Monetarisierung/eigener Kanal (RPM 30–100× schlechter, Slop-Policy-Risiko), aber erlaubt als **Discovery-Trichter auf dem SIGNAL-Kanal**: Cold-Open-Cuts aus fertigen Mastern via `produktion/pipeline/make_short.py`. Regeln + Erfolgskriterien + Ergebnis-Log: `produktion/shorts/SHORTS-LOG.md`. Kein Übertrag auf Abos/Longform nach 4–6 Shorts → Experiment beenden.

## Die wichtigste Regel
**NIEMALS die Nische verlassen.** Themen-Drift ist der #1-Grund, warum Space-Kanäle abstürzen (InsaneCuriosity → Wetter, beyonddiscovery → Autos, Starlight_Ai → Vögel). 100 % Space, immer.

## Dramaturgie-Regel (ab Folge 2 verbindlich) — „Mystery-first, offenes Ende"
**Ziel ist FESSELN, nicht belehren.** Das Mysterium ist der Motor, nicht die Wissenschaft. Entschieden (User, Juli 2026):
- **Gewählte Strategie: Weg B — Mystery-first mit befriedigendem Payoff.** Hart mit dem „Ist es außerirdisch?!"-Mysterium führen, Spekulation durchs ganze Video reiten, am Ende befriedigend **aber offen** auflösen. Die **7 Pflicht-Fessel-Hebel** stehen in `SPACE-PLAYBOOK.md` §5b — jede Folge muss alle 7 erfüllen.
- **PRÄZISIERUNG (Zwei-Fragen-Prinzip, verbindlich ab v3):** „Offenes Ende" heißt NICHT „wir wissen nichts / unresolved". Das entwertet das Format und liest sich wie Slop. Trenne pro Folge sauber:
  - **Die Overclaim-Frage** (z. B. „Ist es Leben / eine Sonde?") bekommt ein **klares Urteil** (meist NOISE), mit Nachdruck — das ist das Anti-Slop-Rückgrat + Retention-Payoff.
  - **Die echte offene Frage** (z. B. „Was IST dieses Objekt dann?") trägt die **Offenheit + den Cliffhanger + ein Datum, wann wir es wissen.**
  Ein falscher Overclaim wird IMMER zugeschlagen — nur das echte Rätsel bleibt offen. So bleiben Fesseln UND Glaubwürdigkeit zusammen.
- **SCHAUFENSTER-REGEL (verbindlich ab v4):** Das Schaufenster verkauft die FRAGE, das Video liefert die ANTWORT. Thumbnail, Titel, Beschreibung (Zeile 1–2) und Cold Open versprechen, DASS ein Urteil fällt — sie verraten NICHT, welches. **Verboten im Schaufenster:** das Verdict, Verneinungen („NOT LIFE", „it wasn't life", „noise"). **Pflicht:** Neugier-Lücke + Versprechen einer klaren Antwort („we say the number out loud", „here's what it actually was"). Auf Verneinungen klickt niemand; auf ein angekündigtes Urteil schon. Das Verdict selbst wird hart IM Video ausgesprochen.
- **⚠️-REGEL (verbindlich):** Eine mit ⚠️ markierte (unverifizierte) Behauptung ist **ship-blocking**. Keine ⚠️-Behauptung geht ins VO/Vertonung, bevor die Markierung aufgelöst (belegt oder gestrichen) ist. Kein „später prüfen".
- **Das Ende NICHT hart zuschlagen.** Kein „ist halt ein Komet / MOSTLY NOISE"-Debunk, der das Rätsel tötet. Die Beweise dürfen in eine Richtung deuten, aber **genug bleibt offen**, damit das Mysterium lebt.
- **Spekulation hochdrehen**: die aufregende Möglichkeit („Was, wenn es WIRKLICH eine Sonde ist? Dann würde das bedeuten…") erst voll auskosten, bevor (weich) aufgelöst wird.
- **Immer mit Cliffhanger enden**: offene Fäden + „der nächste Besucher ist schon unterwegs" → Kommentar-Köder, Abo-Treiber, Brücke zur nächsten Folge.
- **„Signal vs. Noise" bleibt der Rahmen** (macht das Rätsel hochriskant/echt statt Boulevard), aber das Verdict wird als *Tendenz/offen* gehalten, nicht als geschlossenes Urteil.
- Referenz-Beweis „fesseln UND glaubwürdig": Cool Worlds. Warnung „reines Clickbait crasht": officialcosmosprodigy, Eternityinspace.
- **Folge 1 (3I/ATLAS) bleibt wie sie ist** (kein Re-Render) — die Regel gilt ab Folge 2.

## ⭐ Sprach-Regel (verbindlich ab F5 — User-Entscheid 28.07.2026, besonders wichtig)
**Einfache Sprache, nicht wissenschaftlich.** Wir sind eine Doku, kein Seminar — der Zuschauer schaut nebenbei am Handy.
Kernregeln (Details + Beispiele: `SPACE-PLAYBOOK.md` **§5c**): max. **2 Eigennamen pro Folge** (Rest = Rollen: „ein Team in Chicago") · **keine Fachzahlen im VO** (3σ / ppm / AU → in Alltagssprache übersetzen, exakte Werte nur in Beschreibung + Quellen-Chips) · Sätze 10–13 Wörter, ein Gedanke pro Satz · konkretes Bild statt Abstraktion · Fremdwort-Test vor der Vertonung.
**Die Substanz bleibt** (Fakten-Gate, Primärquellen, Verdicts) — wir ändern nur, WIE wir es sagen.
**PRÄZISIERUNG 29.07.2026 (§5d):** §5c gilt auch fürs BILD, nicht nur fürs Voiceover. Quellenliste in der Beschreibung bleibt vollständig (kostet null Bildzeit, ist unser Policy- und Fehler-Schutz). Quellen-Chips im Bild ab F5 **max. 4 pro Folge, Rolle + Ort statt Zitation** — kein DOI, keine arXiv-ID, kein σ/ppm im Bild (F2 hatte 10 Chips = 60 Sek Bildzeit, einer mit vollem DOI). Zuordnung wandert dafür ins gesprochene Wort: „ein Team in Puerto Rico" statt „Méndez et al.".

## Prozess-Regeln (verbindlich ab 17.07.2026 — System-Review mit User beschlossen)
1. **Upload-Tag NUR nach Checkliste:** `produktion/UPLOAD-CHECKLISTE.md` — inkl. Live-News-Check (ship-blocking), `{STATUS}`-Füllung, A/B-Thumbs, KI-Disclosure, „not made for kids".
2. **Feedback-Loop nach jedem Upload:** Playbook **§14** — Reviews bei +48 h und +7 Tagen; CTR → `research/thumb-ab-log.md`, Retention-Dips auf Fessel-Hebel mappen, Median-KPI führen. Eigene Daten schlagen Konkurrenz-Heuristiken; Regeländerungen nur bei ≥2 Folgen gleichem Muster.
3. **Skript-Gate VOR der Vertonung (neu 29.07.2026):** `produktion/pipeline/skript_lint.py <VO-Datei> --packaging <Upload-Paket>` muss mit Exit-Code 0 durchlaufen. Prüft maschinell, was bisher nur Prosa war: ⚠️-Regel (ship-blocking), Laufzeit 13–15 Min, §5c (Eigennamen/Fachzahlen/Satzlänge/Fremdwörter), Schaufenster-Verneinungen. Erzeugungs-Prozess dazu: Playbook **§15** (6 Durchgänge, nie one-shot; Chat = Urteil, Code = Regel).
4. **QC-Gate VOR dem Assemble:** `produktion/pipeline/qc_textscan.py` auf JEDEN Clip (auch Reuse!), Befund in `produktion/clip-katalog.md`. Kein Clip ohne „clean"-Status in den Schnitt. (F4-Lesson: 3 Fake-Text-Clips erst am Master gefunden → 2 Re-Renders.)
5. **Fakten-Konvention:** Jede Folge hat ihr Dossier in **`fakten/<thema>.md`** mit CHANGELOG; Live-Check-Ergebnisse dort loggen.
6. **Pipeline-Bibliothek:** Ab F5 gemeinsame Skripte in `produktion/pipeline/` statt Pro-Folge-Kopien (Drift-Risiko); pro Folge nur Config (`shot-plan.json`, `vo_manifest.json`). Bausteine: `qc_textscan.py`, `skript_lint.py`, `make_short.py`, `fetch_nasa.py`.
7. **Reuse nur über den Katalog:** `produktion/clip-katalog.md` (Motiv, Herkunft, Text-Scan-Status) ist die einzige Quelle für Pool-Wiederverwendung.

## Wo steht was
- **⭐ `NISCHEN-SYSTEM.md`** — **das operative Verfahren zur Nischenauswahl.** Der 8-Stufen-Trichter: Hülle → 80–120 Kandidaten aus 5 Quellen → 8 Disqualifikatoren → Nachfrage/Fenster-Scan → Arithmetik → Produzierbarkeit → Packaging-Beweis → Pilot. Mit Zeitbudget, Zielmenge und Abbruchkriterium je Stufe. Kerndefinition: **Nische = Publikum × Themenraum × Format**. **Ausführbar über die Skill `nische-finden`** — der Satz „finde eine perfekte Nische" startet den Trichter. Belege dazu: `NISCHEN-PLAYBOOK.md`. Werkzeug: `analyse/nischen_scan.py`.
- **`NISCHEN-PLAYBOOK.md`** — **Belegband zum System** (Herleitung, Prüfprotokolle, Asset-Pool-Katalog, Käufer-Ökonomie, Hygiene-Liste). Frühere Fassung: wie wir Nischen FINDEN (kanal-unabhängig, verbindlich für jeden neuen Kanal). **Ausführbar über die Skill `nische-finden`** — der Satz „finde eine perfekte Nische" startet die Prozedur. Stufen: Spiel klären (Extraktion vs. Equity) → 7 binäre Kill-Gates → Headroom-Sichtung + Nachfrage/Fenster-Scan → Arithmetik mit P25-RPM → Packaging-Test → Stop-Loss. Kernbefunde: die kursierende „Profi-Methode" ist überwiegend Vendor-SEO (Beweis-Hierarchie A/B/C); **Top-Verdiener bewerten Nischen gar nicht** (MrBeast-Handbuch: „niche" null Mal; Galloway: „no niche where I can't get traction") — Entscheidungen fallen an Gates und Arithmetik, nicht an Punktesummen; die Streuung INNERHALB einer Nische (8,4×) übersteigt die zwischen Nischen → Planwert ist **P25**, nicht Median. Enthält Asset-Pool-Katalog (15 Pools + 4 Rechtsfallen), Käufer-Ökonomie (1,2×–2,2× Jahresgewinn, Wertminderer), Operator-Ansteckungs-Regeln und die MLA-Regel (deutscher Markt über Tonspur statt Zweitkanal). Werkzeug: `analyse/nischen_scan.py`.
- **`SPACE-PLAYBOOK.md`** — das vollständige Gewinner-Playbook: Regeln der Top-Performer, Titel-Formel, Fessel-Mechanik §5b (7 Hebel + Zwei-Fragen-Prinzip + Schaufenster-Regel + ⚠️-Regel), Produktions-Pipeline, **§15 Skript-Werkstatt** (6 Durchgänge, 8 Erzeugungs-Regeln, Modellwahl je Durchgang), Do's & Don'ts. **Bei jeder Umsetzung §12 (Muster-Regeln) durchgehen — verbindlich.**
- **`research/konkurrenz-muster.md`** — Konkurrenz-Analyse (17 Kanäle Erstdaten + Web-Verifikation): die 8 Muster + 6 Web-Findings, Belege pro Kanal. Grundlage für Playbook §12, Regel 6/7/8.
- **`research/niche-analysis.md`** — Belegdaten: Nischen-Ranking, Einkommens-Schätzungen, Top/Mid/Low-Kanal-Tiers.

## Arbeitsstand (17.07.2026)
Kanal **SIGNAL** — Branding steht (`produktion/branding/`). **F1–F4 fertig produziert** (4K-Master auf CloudFront, Links in den `UPLOAD-PAKET-Fx.md`):
- **F1** 3I/ATLAS (13:12, live/Bestandsschutz) · **F2** K2-18b → Premiere **Sa 18.07.** · **F3** Voyager → **Sa 25.07.** · **F4** Wow!-Signal → **Sa 01.08.** (fester Slot Sa 14:00 ET / 20:00 DE)
- Budget: ~32–40 €/Folge (Deckel 50 €); Higgsfield-Restguthaben ~286 Cr → für F5-Vollproduktion (~600 Cr) Nachkauf nötig.
- **Nächste Schritte:** F2/F3/F4-Uploads nach Checkliste + §14-Reviews · F5-Thema aus `research/themen-pipeline-f3-f5.md` (Outro-Tease F4: Anisotropie) · pipeline/-Migration bei F5.
