---
name: nische-finden
description: Führt die Nischen-Recherche für einen neuen YouTube-Automation-Kanal nach dem Trichter in NISCHEN-SYSTEM.md aus. Nutze diese Skill, wenn der User eine Nische finden, prüfen, bewerten oder vergleichen will — z. B. "finde eine perfekte Nische", "welche Nische für Kanal 2", "prüf mal Nische X", "such mir Nischen-Ideen". Erzeugt 80-120 Kandidaten, siebt sie über 8 Disqualifikatoren, liest Nachfrage und Fenster mit analyse/nischen_scan.py, rechnet die Unit Economics, prüft Produzierbarkeit und Packaging und endet mit einem Entscheidungsdokument plus Kill-Log.
---

# Nische finden — Ausführung

**Das Verfahren steht in `NISCHEN-SYSTEM.md`.** Diese Skill ist die Ausführungsanweisung: was ich in welcher Reihenfolge tue, welche Zwischenergebnisse ich zeige, wann ich abbreche.

Vollständige Belege und Prüfprotokolle: `NISCHEN-PLAYBOOK.md`.

## Grundregeln der Ausführung

1. **Reihenfolge ist bindend.** Disqualifikatoren vor Datenerhebung. Nie eine spannende Idee recherchieren, die an einem Gate schon tot ist.
2. **Ein Nein an einem Gate = Kandidat tot.** Keine Aufrechnung, kein „aber dafür".
3. **Punkte entscheiden nichts.** Die Scorecard kommt erst bei den Finalisten und macht nur die Wahl nachvollziehbar.
4. **Absagen werden aufgeschrieben.** Das Kill-Log ist der wertvollste Teil des Ergebnisses.
5. **Grenzen mitliefern.** Wo die Messung unsicher ist, sage ich es — eine benannte Lücke ist besser als eine glatte Zahl.

## Vor dem Start klären

Nur diese zwei Dinge, und nur wenn der User sie nicht schon gesagt hat:

- **Welches Spiel?** Equity (nachhaltiges Asset, Standard) oder Extraktion (Cash, 1–3-Jahres-Fenster). Bei Extraktion fällt D4 weg und Compilations/Sleep-Content sind erlaubt.
- **Themen-Vorgabe?** Freie Suche oder ein bestimmtes Feld.

Alles andere sind Defaults, die ich nur nenne: `38 $/Folge · 8 Folgen/Monat · Ziel 10.000 $/Monat · RPM-Planwert 2,31 $ · Englisch`.

---

## Stufe 1 · Kandidaten erzeugen → 80–120

Fünf Quellen systematisch abarbeiten (`NISCHEN-SYSTEM.md §4`):

- **A · Materialpool zuerst** — den Pool-Katalog durchgehen (NASA · NOAA · NTSB/CSB/BFU · NARA · Smithsonian · LoC · CREST · CourtListener · USGS · LLNL · Europeana · IA/Prelinger · Commons). Pro Pool 5–15 Kandidaten. Das ist die stärkste Quelle, weil das Bildmaterial unsere bindende Restriktion ist.
- **B · Sprach-Arbitrage** — was performt auf Russisch/Spanisch/Portugiesisch/Japanisch, das im Englischen fehlt?
- **C · Format-Transfer** — bewiesenes Format in einen anderen Themenraum setzen.
- **D · Nachbarschaftssprung** — von einer funktionierenden Nische einen Schritt zur Seite, nicht hinein.
- **E · Nachfrage-Überhang** — Nachfrage da, Angebot alt oder schwach.

Jeder Kandidat wird als **Tripel** notiert, nicht als Thema: `Publikum × Themenraum × Format`.

**Zwischenausgabe:** Tabelle mit `Nische | Publikum | Themenraum | Format | Pool | Quelle`. Zahl nennen.

## Stufe 2 · Disqualifizieren → ~25

Acht binäre Fragen je Kandidat, ohne Websuche, aus Sachkenntnis (`§5`):

| | Frage | Tötet, wenn |
|---|---|---|
| D1 | Braucht es benannte lebende Personen? | ja |
| D2 | Freier Pool mit API/Bulk, PD/CC0, ≥50 Folgen tragfähig? | nein |
| D3 | Werbe-Sperrkategorie (MFK, YMYL-Beratung, Gambling, Adult)? | ja |
| D4 | Von 5 anderen Kanälen austauschbar? *(nur Equity-Spiel)* | ja |
| D5 | Trägt 150 Folgen à ≥3 Min? — **20 Titel in 10 Min testen** | nein |
| D6 | Hält 24 Monate? (Trend-, Policy-, Quellen-Verfall) | nein |
| D7 | Funktioniert ohne Person vor der Kamera, übertragbar? | nein |
| D8 | Englisch möglich? | nein |

**Zwischenausgabe:** Überlebende + **Kill-Log** (jeder Tote mit Gate und einem Satz Grund).

## Stufe 3 · Nachfrage und Fenster lesen → 6–8

**3a Deckensichtung:** Pro Kandidat YouTube-Suche → Filter Video/über 20 Min → nach Aufrufen sortieren. Zeigt die Decke. Sichtung, keine Schwelle.

**3b Scan:**
```bash
python3 analyse/nischen_scan.py "<keyword>" --limit 25 --rpm 2.31 --kosten 38 --ziel 10000 --uploads 8
```

Zwei getrennte Fragen — Vermischung ist der Kardinalfehler:

| | Fenster offen | Fenster eng |
|---|---|---|
| **Nachfrage ja** | 🟢 rein | 🟠 nur mit echtem Format-Unterschied |
| **Nachfrage nein** | 🟡 klein testen | 🔴 raus |

**Bei jedem Scan die drei Messfehler kontrollieren** (`§6c`): frische Videos verzerren nach unten (nur ab 30 Tagen zählen), ruhende Archivkanäle nach oben (nur Upload ≤120 Tage), themenfremde Großkanäle kippen die Statistik (Relevanzfilter). Der Scanner macht das — ich prüfe die Ausgabe trotzdem auf Plausibilität, besonders Handle-Verwechslungen (Abo-Zahl und Top-Titel gegenlesen).

**3c Konkurrenzdichte:** Nicht Kanäle zählen. Die besten drei anschauen und eine Frage beantworten: **können wir das schlagen oder nur nachmachen?** Nur nachmachen → raus.

## Stufe 4 · Rechnen → 3–4

```
Break-even/Folge     = Kosten ÷ (RPM ÷ 1000)
Nötiger Median/Folge = (Ziel ÷ RPM × 1000) ÷ Folgen pro Monat
```
Mit den Defaults: Break-even **16.450**, nötiger Median **541.000/Folge**.

**Realitätstest:** nötiger Median gegen den **besten aktiven Kanal-Median der Nische**. Liegt er darüber, ist das Ziel dort arithmetisch unerreichbar — dann eine der drei Konsequenzen benennen (Ziel senken · mehr Folgen · zweite Einnahmeebene), nicht weiterhoffen.

## Stufe 5 · Produzierbarkeit → 2

Sechs Fragen je Kandidat (`§8`): konsistente Gesichter? · Fremdschrift im Bild? · Shots pro Minute? · fertiges Bewegtbild vorhanden? · Recherchezeit? · trägt eine KI-Stimme das Thema (Pietät)?

**Ergebnis:** belastbare Kostenschätzung pro Folge. Über dem Deckel → raus, egal wie gut die Nachfrage ist.

## Stufe 6 · Packaging-Beweis → 1 Sieger

Für die letzten zwei (`§9`): **20 Titel** (dauert es >30 Min, ist die Nische zu dünn) · **10 Thumbnail-Konzepte** · **Schaufenster-Test** (versprechen ohne verraten) · **≥3 unterscheidbare Folgen-Formate** · **Backlog-Rechnung 10–30×**.

Der Sieger hat das bessere **Packaging**, nicht das bessere Thema.

## Stufe 7 · Scorecard und Entscheidung

Scorecard (`§11`, 8 Kriterien × Gewicht, max. 100) **nur für die Finalisten** — zur Nachvollziehbarkeit, nicht zur Findung. Unter 55 nicht bauen. Bei Gleichstand gewinnt die günstigere Nische.

Dann `research/nischen-entscheid-<JJJJ-MM-TT>.md` schreiben:

1. **Urteil** — eine Nische, 3–5 Sätze Begründung
2. **Kill-Log** — alle Toten mit Gate und Grund
3. **Scan-Ergebnisse** der Finalisten
4. **Arithmetik** mit Planwert und Konsequenz
5. **Kostenschätzung** pro Folge
6. **Packaging-Belege** (die 20 Titel)
7. **Scorecard**
8. **Stop-Loss:** 20–30 Folgen / 760–1.140 $ / Review bei Folge 10 / max. eine Test-Nische parallel
9. **Offene Risiken** — was ich nicht belegen konnte

Committen und pushen.

## Nach der Entscheidung

Empfehle den **Pilot**: eine Folge, dann A/B-Test (3 Varianten, Sieger nach Wiedergabezeit, bis 14 Tage, kostenlos). Nicht zehn Folgen auf Verdacht.

Wenn ein bestehender Kanal beteiligt ist, die **Portfolio-Regeln** nennen (`§12`): nichts teilen zwischen eigenen Kanälen (Skript-Skelett, Stimme, Template, Musikbett, Thumbnail-Grammatik, Upload-Rhythmus), getrennte Marken-/Abrechnungsstruktur, Beweis-Akte pro Folge, Nischen nicht korrelieren.

---

## Was ich in dieser Skill NICHT tue

- **Keine Nische wegen schwacher CTR verwerfen.** Diagnose-Reihenfolge: Impressionen → CTR → Cold Open → *dann* Nische (`§10`). Der Fehlschluss „Nische schuldig" ist der teuerste im Geschäft.
- **Keine Zahl aus Tool-, SEO- oder Affiliate-Blogs als Schwelle.** `§15` sagt, was nicht funktioniert.
- **Keinen zu kleinen Anfangspool akzeptieren.** Unter ~80 Kandidaten weiche ich die Gates auf statt zu verwerfen — dann liefere ich ein Ergebnis, das gut aussieht und falsch ist. Lieber die Kandidatenerzeugung nachschärfen.
- **Kein Ergebnis ohne Kill-Log.** Eine Empfehlung ohne die dokumentierten Absagen ist nicht überprüfbar.
