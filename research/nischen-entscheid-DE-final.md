# Nischen-Entscheid Deutschland — final, 31.07.2026

> Ergebnis des vollständigen Verfahrens nach `NISCHEN-SYSTEM.md`, mit Scanner v2 (post-Audit), alle Kandidaten mit 3–4 Suchbegriffen gemessen.
> Ersetzt beide Vorfassungen (30.07. ungültig, 31.07.-revidiert überholt bei der Fenster-Frage).

---

## 1. Die Antwort in drei Zeilen

**Beste deutsche Nische: Bauwerksversagen / Technik-Katastrophen-Forensik.**
**Geschätzte Einnahmen nach 6 Monaten: 0 $/Monat** — mit 85 % Wahrscheinlichkeit, weil das Partnerprogramm bis dahin nicht erreicht ist. Erwartungswert **71 $ brutto, −233 $ netto**.
**Nach 24 Monaten: Erwartungswert 432 $ brutto, 128 $ netto.**

Das ist keine pessimistische Schätzung, sondern die Rechnung mit echten Vergleichskanälen. Details in §4.

---

## 2. Warum Bauwerksversagen gewinnt

Beste Nachfrage von allem Gemessenen und **das einzige Thema, dessen Nachfrage zu unserem Format passt**.

| Kriterium | Wert | Einordnung |
|---|---|---|
| Thema trägt | **35/80 Treffer ≥100k = 44 %** | Bester Wert aller 14 gemessenen Nischen |
| Nachfrage-Träger | **6** | Kein anderer Kandidat kam über 3 |
| **Format der Nachfrage** | **10,4 Min Median**, nur 12 % über 40 Min | ✅ passt zu 13–15-Min-Doku |
| Fenster | ❌ **eng** — 0 kleine, 0 junge Kanäle bei 14 aktiven | Das Problem, s. §3 |
| Produzierbarkeit | keine Gesichter, keine Fremdschrift, amtliche Berichte | ~30–40 €/Folge |
| Haltbarkeit | Evergreen, Fälle historisch abgeschlossen | 24 Monate+ |

**Träger:** `@MDRInvestigativ` 243.636 · `@frontal` 95.682 · `@RickRieck` 85.655 · `@Megabauten` 77.362 · (plus `@SabinCivil` 452.211 und `@TEDEd` 273.293 — internationale Kanäle, die in der deutschen Suche auftauchen)

---

## 3. Der Befund, der über der Nischenwahl steht

**In keiner einzigen der 14 gemessenen deutschen Nischen kommt ein kleiner oder junger Kanal durch.**

Bei Bauwerksversagen ist die Frage jetzt sauber beantwortet — 14 aktive Kanäle, also über der Messschwelle, und darunter **null** unter 50.000 Abos mit einem 100k-Video und **null** unter 18 Monaten mit starkem Median. Der Views-pro-Abo-Median liegt bei **0,06**: Diese Kanäle leben von ihrer Abonnentenbasis, nicht von Empfehlungen an neue Zuschauer.

Wer die Nachfrage bedient, ist immer dieselbe Gruppe: **MDR, ZDF frontal, Terra X, Quarks, SRF, WDR, BR** — öffentlich-rechtlich, aus Rundfunkbeiträgen finanziert, ohne Notwendigkeit, profitabel zu sein. Dazu große internationale Kanäle (TED-Ed 22,8 Mio., SabinCivil 6,97 Mio.), die in deutschen Suchergebnissen mitranken.

Das ist kein Nischenproblem. Das ist die Struktur des deutschen Markts.

---

## 4. Die 6-Monats-Rechnung — und woher die Zahlen kommen

Das Arithmetik-Gate des Systems rechnet den **eingeschwungenen** Zustand. Den erreicht ein neuer Kanal nach 18–36 Monaten. Für Monat 6 braucht es ein Ramp-Modell (`analyse/ramp_modell.py`).

**Die Anker sind echte deutsche Doku-Kanäle aus unseren Scans** — keine Annahmen:

| Kanal | Alter | Abos | Median |
|---|---:|---:|---:|
| @EliasRichtersDokus | 3,4 Mon | 2.820 | **3.936** |
| @DieDunkleAktee | 5,5 Mon | 2.390 | **15.787** |
| @Erdarchiv | 10,8 Mon | 16.500 | 72.916 ← Ausbrecher |
| @WeltderFabeln | 13,8 Mon | 2.830 | 1.723 |
| @Evolution-X | 14,2 Mon | 3.740 | 2.423 |
| @f3rlas | 36,7 Mon | 7.510 | 13.799 |
| @LostReichIndustries | 92,6 Mon | 1.300 | 451 |

**Lesart: Sechs von sieben bleiben auch nach über einem Jahr im niedrigen vierstelligen Median.** Einer bricht aus.

### Monat 6 · 8 Folgen/Monat · RPM 2,00 $ · 304 $ Kosten/Monat

| Szenario | Wahrsch. | Views/Mon | Abos kum. | Partnerprogramm | Brutto | Netto |
|---|---:|---:|---:|:--:|---:|---:|
| Fehlschlag | 35 % | 4.800 | 29 | ❌ | 0 $ | −304 $ |
| Unteres Quartil | 30 % | 18.000 | 108 | ❌ | 0 $ | −304 $ |
| Median | 20 % | 48.000 | 288 | ❌ | 0 $ | −304 $ |
| Guter Lauf | 11 % | 168.000 | 1.008 | ✅ | 336 $ | +32 $ |
| Ausbrecher | 4 % | 420.000 | 2.520 | ✅ | 840 $ | +536 $ |

> ### 📌 **Erwartungswert Monat 6: 71 $ brutto · −233 $ netto**
> ### **Wahrscheinlichkeit, dass die Einnahmen exakt 0 $ sind: 85 %**

**Der Grund ist nicht die Reichweite, sondern die Abo-Schwelle.** Watch-Stunden werden schon im Median-Szenario erreicht (3.200/Monat gegen 4.000/Jahr nötig). Aber 1.000 Abonnenten braucht bei 2 Abos pro 1.000 Views rund **8–10 Monate**. Vorher fließt kein Cent, egal wie viele Views da sind.

### Die längeren Horizonte

| | Erwartungswert brutto | netto | P(0 $) |
|---|---:|---:|---:|
| Monat 6 | 71 $ | −233 $ | 85 % |
| Monat 12 | 212 $ | −92 $ | 65 % |
| Monat 24 | 432 $ | **+128 $** | 35 % |

**Break-even im Erwartungswert liegt zwischen Monat 12 und 24.** Kumuliert bis Monat 24 sind rund **−4.000 bis −5.000 $** vorzufinanzieren, bevor der Kanal im Mittel schwarze Zahlen schreibt.

---

## 5. Was das für die Entscheidung heißt

**Bauwerksversagen ist die beste deutsche Nische, die das Verfahren finden kann.** Das Verfahren hat funktioniert — es hat gemessen, korrigiert, den eigenen Sieger gekippt und am Ende eine klare Antwort geliefert.

Die Antwort lautet: **Lohnt sich unter diesen Bedingungen nicht.** Nicht wegen der Nische, sondern weil drei Faktoren zusammenkommen:

1. **Kein Eintrittsfenster** in irgendeiner gemessenen deutschen Nische
2. **RPM 2,00 $** — das untere Viertel eines kleinen Sprachmarkts
3. **Abo-Schwelle** verzögert jede Einnahme um 8–10 Monate

### Drei Wege, und nur einer ändert die Größenordnung

| Weg | Monat-6-Erwartung | Anmerkung |
|---|---|---|
| **A · Deutsch, wie geplant** | ~0 $ | Break-even im Mittel nach 12–24 Mon. Vorfinanzierung 4.000–5.000 $ |
| **B · Ziel senken auf 300–500 $/Monat** | ~0 $, ab Monat 18 realistisch | Ehrlich erreichbar, aber ein Nebenverdienst |
| **C · Englisch produzieren, Deutsch als Tonspur** | ~0 $ (Abo-Schwelle bleibt) | **Ändert die Decke**: ~4× Markt, RPM 2,31 statt 2,00, das deutsche Publikum bleibt erreicht |

**Empfehlung: C.** Dieselbe Nische — Technik-Katastrophen-Forensik funktioniert auf Englisch mindestens so gut, das Quellenmaterial (NTSB, CSB, NIST) ist ohnehin englisch, und die deutschen Fälle (Eschede, Köln, Rahmede) sind international kaum erzählt und damit eher wertvoller. Deutsch kommt als Auto-Dubbing-Spur dazu.

Falls du bei Deutsch bleibst: **A ist gangbar, aber als Aufbauprojekt mit 4.000–5.000 $ Vorfinanzierung**, nicht als Einnahmequelle im ersten Jahr. Dann gilt Weg B als Zielsetzung.

---

## 6. Wenn gestartet wird — die ersten Schritte

**Pilot: eine Folge.** Kandidaten mit Deutschland-Anker und vorhandener Berichtslage: Einsturz des Kölner Stadtarchivs (2009) · Rahmedetalbrücke · Eschede (1998) · Bad Aibling (2016). ⚠️ Loveparade (2010) wegen lebender Angehöriger nicht als Folge 1–10.

**Zu messen:** Ist-Kosten gegen 30–40 € · Ist-Arbeitszeit · CTR und 30-Sekunden-Rate · Reibung im Material.

**Stop-Loss:** 20–30 Folgen oder 3–6 Monate · Deckel 760–1.140 $ · Review bei Folge 10 · Kadenz aus dem **Ist-Wert**, nicht der Absicht.

**Format-Unterschied ist Pflicht** (Fenster ist eng): Was können MDR und ZDF strukturell nicht? Sie machen keine Serien über *einen* Fehlertyp über viele Fälle hinweg, keine Vergleichsformate, keine Folgen unter 10 Minuten. Da liegt der Platz.

---

## 7. Offene Risiken

1. **Der Benchmark ist kontaminiert.** TED-Ed (22,8 Mio.) und SabinCivil (6,97 Mio.) sind englischsprachige Kanäle in der deutschen Suche. Sie treiben den Benchmark auf 273.293 — für einen deutschen Kanal ist das kein erreichbarer Vergleichswert. Der realistische deutsche Benchmark sind MDR/Megabauten/RickRieck: **77.000–244.000**.
2. **Das Ramp-Modell ist ein Modell.** Sieben Ankerkanäle, keine Kohortenstudie. Die Szenario-Wahrscheinlichkeiten (35/30/20/11/4 %) sind gesetzt, nicht gemessen.
3. **Die Schwellenwerte des Scanners sind weiterhin nicht kalibriert** gegen die eigene 17-Kanal-Basis.
4. **Vier Kandidaten der ersten Fassung sind nie neu gemessen** (DDR-Alltag, Firmengeschichte, historische Katastrophen, Flugunfall). Sie gelten als **ungemessen**, nicht als abgelehnt.
5. **Die Abo-Schwelle ist die härteste Annahme.** 2 Abos pro 1.000 Views stammt aus dem eigenen Playbook. Läge der Wert bei 5, verkürzte sich die Nullphase deutlich.

---

## CHANGELOG
- **31.07.2026** — Finale Fassung. Fenster-Frage für Bauwerksversagen mit 4 Keywords und 30 Kanälen aufgelöst: **eng** (0 klein, 0 jung bei 14 aktiven, Views/Abo-Median 0,06). Ramp-Modell `analyse/ramp_modell.py` ergänzt, verankert an sieben echten deutschen Doku-Kanälen. **Antwort auf die 6-Monats-Frage: 0 $ mit 85 % Wahrscheinlichkeit, Erwartungswert 71 $ brutto / −233 $ netto.** Break-even im Mittel zwischen Monat 12 und 24. Empfehlung: dieselbe Nische auf Englisch mit deutscher Tonspur.
