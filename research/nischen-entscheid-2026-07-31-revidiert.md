# Nischen-Entscheid Deutschland — REVIDIERT, 31.07.2026

> **Ersetzt `nischen-entscheid-2026-07-30.md`.** Der Vorgänger beruht auf Messungen eines Scanners mit vier bestätigten Defekten. Er bleibt als Vorgang erhalten, ist aber **als Entscheidungsgrundlage ungültig**.
> **Anlass der Revision:** Sechs-Perspektiven-Audit des Verfahrens (Statistik, Algorithmus, Unternehmer, Recht, Code, Falsifikator), jede Kritik schiedsrichterlich bewertet.

---

## 1. Was am Vorgänger falsch war

| Defekt | Belegt durch | Folge |
|---|---|---|
| **Suchfilter `&sp=CAMSAhAB` liefert 0 Video-Blöcke** | Gegentest: 760 KB Seite, 0 Blöcke; korrekter Filter `&sp=EgIQAQ%3D%3D` → 20 Blöcke | **7 von 11 Scans stillschweigend ruiniert.** Sechs Nischen als „keine Nachfrage" im Kill-Log, die nie gemessen wurden |
| **Relevanzfilter invertiert** | `@Erdarchiv` mit 7 % ausgesperrt; `@KurzgesagtDE` mit 100 % durchgelassen, weil „Dinge Erklärt" das Suchwort *erklärt* enthält | Ein fachfremder 2,65-Mio.-Kanal setzte in **zwei unabhängigen Nischen** denselben Benchmark |
| **Videolänge wurde nie gemessen** | Format ist Teil der Nischendefinition, fehlte im Code | Unsichtbar, dass die Nachfrage des Siegers zu 55 % aus 40-Min-plus-Content besteht |
| **Ein Keyword pro Nische** | „urzeit-doku" → Median 76.544; „urzeit-evolution" → 1.374 | **Faktor 56.** Das Verfahren wählte die Formulierung, nicht die Nische |

**Und ein Verfahrensfehler, der nichts mit dem Code zu tun hatte:** Der Sieger wurde mit `@Erdarchiv` begründet — einem Kanal, den das Instrument im selben Lauf als themenfremd verworfen hatte. Die Handkorrektur war nirgends als solche gekennzeichnet. Ohne die daraus vergebenen 12 Punkte stand es 72:68 statt 84:68, also innerhalb des Rauschens.

---

## 2. Das neue Urteil

### 🏆 **Technik-Katastrophen-Forensik / Bauwerksversagen**

Der Kandidat, den der Vorgänger als **„keine Nachfrage"** abgeschrieben hatte.

| | Bauwerksversagen | Paläontologie (alter Sieger) |
|---|---|---|
| Thema trägt | ✅ **20/60 = 33 %** | ✅ 21/60 = 35 % |
| **Nachfrage-Träger** | ✅ **3** | ❌ **1** |
| Fenster | ⚠️ unentscheidbar (4 aktive) | ✅ offen |
| **Format der Nachfrage** | ✅ **7,6 Min Median, 5 % >40 Min** | ❌ **42,5 Min Median, 55 % >40 Min** |
| Benchmark Top-3 | **85.653** | 13.808 |
| **Nach Winner's-Curse-Abschlag** | **42.826** | 6.904 |

**Die Träger** (mit Konfidenzintervall und Kadenz):
- `@MDRInvestigativ` — 230.000 Abos, Median **243.635** [135.950–436.614], 3,0/Mon
- `@RickRieck` — 100.000 Abos, Median **85.653** [51.423–142.667], 0,3/Mon
- `@Megabauten` — 133.000 Abos, Median **77.360** [44.695–133.896], 2,8/Mon

### Warum das entscheidet — und es sind nicht die Punkte

Nach Punkten liegt es **78 zu 76** — praktisch gleichauf, und das würde ich nicht zur Begründung nehmen. Entschieden hat ein Gate, nicht eine Summe:

> **Die Paläontologie-Nachfrage gehört zu einem Format, das wir nicht bauen.** 55 % der Nachfrage liegt über 40 Minuten, der Median bei 42,5 Minuten — das ist Sleep- und Longplay-Content. Wir bauen 13–15-Minuten-Dokus. Eine Nachfrage, die man mit dem eigenen Format nicht bedient, ist für uns keine Nachfrage.

Dazu kommt: Der einzige Paläo-Träger `@Erdarchiv` erscheint **auch** als einziger Träger im Tiefsee-Scan (49,3 Min Median, 65 % über 40 Min). Es ist ein allgemeiner Erdgeschichte-Kanal — Paläontologie und Tiefsee sind also nicht zwei Kandidaten, sondern dasselbe Revier desselben Kanals im Longplay-Format.

Bauwerksversagen hat dagegen **drei voneinander unabhängige Träger** in unserem Längenband.

---

## 3. Vollständige Neumessung (alle mit 3 Keywords)

| Nische | Urteil | Thema | Träger | Fenster | Format Median | Benchmark ÷2 |
|---|---|---|---|---|---|---|
| **🏆 Bauwerksversagen** | tragfähig, Fenster ungemessen | 33 % | **3** | unentscheidbar | **7,6 Min** | **42.826** |
| Paläontologie | unbesetzt m. Nachfrage | 35 % | 1 | offen | 42,5 Min ⚠️ | 6.904 |
| Tiefsee | unbesetzt m. Nachfrage | ✅ | 1 (Erdarchiv) | offen | 49,3 Min ⚠️ | — |
| Schiffsunglücke | unbesetzt m. Nachfrage | ✅ | 1 | unentscheidbar | 14,9 Min | — |
| Zugunglücke | unbesetzt m. Nachfrage | 25 % | 1 (NDR 97k) | unentscheidbar | 2,2 Min | 9.593 |
| Industrieunfälle | unbesetzt m. Nachfrage | 25 % | 1 (Terra X 132k) | unentscheidbar | — | 4.834 |

**Fünf von sechs neu gemessenen Kandidaten waren im Vorgänger als „keine Nachfrage" abgeschrieben.** Alle fünf tragen Nachfrage. Der einzige Grund für die Absage war ein falscher URL-Parameter.

*Einzelbelege: Eschede 1.394.604 Views (29:03) · Supervulkan 2.160.070 · MDR Investigativ Median 243.635.*

---

## 4. Die Arithmetik — jetzt mit Katalogfaktor und Abschlag

```
Nötiger Median = (Ziel ÷ RPM × 1000) ÷ (Folgen × Katalogfaktor)
               = (10.000 ÷ 2,00 × 1000) ÷ (8 × 2,0) = 312.500
```

| Szenario | Median | AdSense/Monat |
|---|---:|---:|
| Nötig für 10.000 $ | 312.500 | 10.000 $ |
| **Bauwerksversagen, abgeschlagen** | **42.826** | **1.370 $** |
| Bauwerksversagen, unabgeschlagen | 85.653 | 2.741 $ |
| Break-even | 19.000 | 608 $ |

**Realistisch: 1.400–2.700 $/Monat.** Immer noch nicht 10.000 $ — aber **fünf- bis zwölffach** über dem alten Sieger (220–550 $).

### Und die Zahl, die der Trichter hätte vorwegnehmen müssen

Der neue **Machbarkeits-Vorcheck** (jetzt Stufe 0b) rechnet in zehn Minuten:

> Terra X, der stärkste deutsche Doku-Kanal, hat Median 132.000.
> 132.000 × 8 Folgen × 2,0 Katalog × 2,00 $/1000 = **4.224 $/Monat.**

**Das ist die Decke des deutschen Doku-Markts** — für den Marktführer mit Rundfunkgebühren im Rücken. Das 10.000-$-Ziel war vor dem ersten Kandidaten unerreichbar, und drei Arbeitstage Trichter haben daran nichts geändert. Genau dafür gibt es den Vorcheck jetzt.

### Konsequenz — eine muss gewählt werden

1. **Ziel auf 2.000–3.000 $/Monat senken.** Dann passt Bauwerksversagen. ← *empfohlen*
2. **Sprachmarkt wechseln:** englisch produzieren, Deutsch als MLA-Tonspur. Die einzige Variante, in der 10.000 $ arithmetisch möglich bleiben. *(Ersetzt die alte Konsequenz „mehr Folgen" — die widersprach der Kadenz-Regel und erhöhte das Slop-Risiko.)*
3. **Zweite Einnahmeebene.** Bei Technik-Forensik realistischer als bei Paläontologie: B2B-Umfeld, Ingenieur-Publikum, Sponsoring denkbar.

---

## 5. Override-Protokoll

*Nach Audit-Befund verpflichtend: jede Handkorrektur eines Maschinenurteils wird protokolliert.*

| Feld | Maschinenwert | Handwert | Begründung |
|---|---|---|---|
| Paläo „Fenster" (Vorgänger) | `false`, Erdarchiv als themenfremd verworfen | „✅ verifizierter Durchbrecher", 12 Punkte | **Unzulässig gewesen.** Nicht als Override gekennzeichnet, entscheidungstragend. In dieser Fassung zurückgenommen — v2 schließt Erdarchiv korrekt ein, ohne Handkorrektur |
| Sieger-Wahl (diese Fassung) | 78 zu 76 Punkte = gleichauf | Bauwerksversagen | Entschieden am **Format-Gate** (7,6 gegen 42,5 Min Median), nicht an der Punktsumme. Offen ausgewiesen |

---

## 6. Stop-Loss und nächster Schritt

**Pilot: eine Folge Bauwerksversagen.** Kandidaten mit Deutschland-Anker und vorhandener Berichtslage: Einsturz der Kölner Stadtarchivs (2009), Hochhausbrand-Statik, Brücken-Sperrungen (Rahmede), Loveparade-Statik (2010, ⚠️ Opfer — Pietät prüfen).

Zu messen: Ist-Kosten gegen Schätzung · Ist-Arbeitszeit · Reibung im Material · CTR und 30-Sekunden-Rate.

**Grenzen, vorab festgelegt:** 20–30 Folgen **oder** 3–6 Monate · Deckel **760–1.140 $** · Review bei Folge 10 · maximal eine Test-Nische parallel · **Kadenz aus dem Ist-Wert**, nicht aus der Absicht.

**Diagnose-Reihenfolge bei schwachen Zahlen:** Impressionen → CTR → Cold Open → *dann* Nische.

---

## 7. Offene Risiken

1. **Das Fenster von Bauwerksversagen ist ungemessen** (nur 4 aktive Kanäle, Schwelle 5). Es gibt keinen Beleg, dass ein Neueinsteiger durchkommt — aber auch keinen Gegenbeleg. Das ist die wichtigste offene Frage und nur durch den Pilot beantwortbar.
2. **Die Schwellenwerte sind weiterhin gesetzt, nicht kalibriert.** 50.000 Median, 100.000 Hit, 5 aktive Kanäle, 25-%-Quote — plausibel, aber nicht aus Daten abgeleitet. Kalibrierung gegen die eigene 17-Kanal-Basis steht aus.
3. **Das Ziel ist auch mit dem neuen Sieger gerissen.** 1.400–2.700 $ statt 10.000 $. Ohne die Wahl einer Konsequenz aus §4 baust du wissentlich auf ein Viertel des Ziels.
4. **MDR Investigativ ist öffentlich-rechtlich.** Zwei der drei Träger sind Einzelkanäle (RickRieck, Megabauten) — das ist besser als bei den anderen Kandidaten, aber der stärkste Träger muss nicht profitabel sein.
5. **Vier Kandidaten des Vorgängers sind noch nicht neu gemessen** (DDR-Alltag, Firmengeschichte, historische Katastrophen, Flugunfall). Sie starben an Treffermengen von 3–6, was unter der neuen Mindestgrenze von 12 als **ungemessen** gilt. Sie gehören nicht ins Kill-Log.

---

## CHANGELOG
- **31.07.2026** — Revision nach Sechs-Perspektiven-Audit. Vier Instrumentendefekte behoben (Suchfilter, Relevanzfilter, fehlende Längenmessung, ein Keyword), alle Kandidaten mit 3 Keywords neu gemessen. **Sieger gewechselt:** Bauwerksversagen (vorher als „keine Nachfrage" abgeschrieben) statt Paläontologie. Entscheidend war das Format-Gate: die Paläo-Nachfrage besteht zu 55 % aus 40-Min-plus-Content. Arithmetik mit Katalogfaktor 2,0× und Winner's-Curse-Abschlag neu gerechnet: realistisch 1.400–2.700 $/Monat. Machbarkeits-Vorcheck (Stufe 0b) eingeführt, der die Marktdecke von ~4.224 $ in zehn Minuten sichtbar macht.
