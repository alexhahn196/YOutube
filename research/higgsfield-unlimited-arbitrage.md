# Higgsfield-Unlimited: was geht wirklich, und was es bringt

> Frage: „Skripte vorschreiben, dann einen Unlimited-Plan für einen Tag kaufen — wie viele Videos bei welchen Kosten?"
> Erhoben 31.07.2026 direkt aus `show_plans_and_credits` + `models_explore`. Durchsatzrechner: `produktion/pipeline/unlim_durchsatz.py`

---

## 1. Der erste Haken: **es gibt keinen Tages-Plan**

Ein Day-Pass existiert nicht. Was es gibt, ist kein eigenes Produkt, sondern eine **Beigabe zum ULTRA-Jahreskauf**:

| Paket | Enthaltene Unlimited-Modelle | Laufzeit |
|---|---|---|
| **7-Day Unlimited** | Nano Banana Pro (1K/2K) · Nano Banana 2 (1K/2K) · **Kling 3.0 (720p/5s)** | 7 Tage ab Kauf |
| **365-Day Unlimited** | Seedream 5.0 Lite · Flux.2 Pro (1K) · Seedream 4.5 (2K/4K) · Nano Banana · Kling O1 Image · GPT Image | 12 Monate |
| Free Gens | Soul V2 & Cinema — 10.000 Generierungen (Jahresplan) | — |

**Preis: ULTRA annual 99 € statt 129 €** (23 % Rabatt), dazu 3.000 Credits pro Monat.

### 🔴 „Buy until: **July 31**"

Das Angebot läuft laut Plan-Daten **heute** aus. Wer es will, entscheidet heute.

### Das entscheidende Detail an den Modell-Listen

Im **365-Day**-Paket ist **kein einziges Video-Modell** — es sind alles Bildmodelle. Das einzige unbegrenzte Video-Modell steckt im **7-Day**-Paket und ist auf eine feste Konfiguration festgenagelt: **Kling 3.0, 720p, 5 Sekunden.** Kein 1080p, kein 4K, keine längeren Clips.

---

## 2. Der zweite Haken: 720p

Unser Standard ist **1080p/std**, bei Hero-Shots **4K/high** — Folge 1 wurde ausdrücklich auf 4K umgestellt („schärferes Ausgangsmaterial", `produktion/folge-01-v4/README.md`). 720p liegt zwei Stufen darunter.

**Mildernd:** Der Upscale-Weg ist in unserer Pipeline schon drin — F2 hat Reuse-Shots per lanczos hochgerechnet. 720p → 1080p ist machbar. Es bleibt aber ein Downgrade, und für einen 4K-Master ist es keins, das man freiwillig wählt. Für eine Zwei-Stunden-Sleep-Doku, die nachts am Handy läuft, ist es dagegen völlig ausreichend.

---

## 3. Der dritte Haken — und der ist der wichtigste für deinen Plan

Die Fußnote zu jedem Unlimited-Eintrag lautet: **„Available for 7 days after purchase on web."**

**Auf *web*.** Nicht „über die API". Und die API sagt heute:

```
unlim: { available: false, remaining: null, expires_at: null }
unlim_trial_in_mcp_active: false
```

Die Video-Modelle tragen im MCP zwar `supports_unlim: true` — der Mechanismus ist also gebaut. Ob unser gekauftes Kontingent die Konfiguration `kling3_0 / 720p / 5s` **über die API** deckt, steht aber erst nach dem Kauf fest.

> ### Genau daran hängt dein „Skripte vorschreiben"-Plan.
> Ohne API-Zugang zum Kontingent müsste jeder Clip im Browser einzeln angelegt werden. **16.000 Clips klickt niemand.** Mit API-Zugang läuft es unbeaufsichtigt durch.

**Sofort prüfbar, ein einziger Aufruf nach dem Kauf:** `models_explore` mit `unlim: true` — das `unlim`-Block zeigt `available` und `remaining`, die „Unlim configs"-Zeile listet die tatsächlich gedeckten Konfigurationen. Antwort in Sekunden, bevor irgendein Skript startet.

---

## 4. Die Zahlen — wenn es über die API läuft

Bei Unlimited ist der Preis nicht mehr die Grenze. **Der Durchsatz ist es.** Und der ist hart begrenzt: Ultra erlaubt **8 parallele Video- und 8 parallele Bild-Generierungen**.

Rechnung: 8 Slots × (60 / Minuten je Generierung) × **60 % Effizienz** (Queue, Fehlschläge, Re-Rolls).

### 7 Tage, Skript läuft durch (24 h/Tag)

| Dauer je Generierung | Clips/Stunde | **Clips im Fenster** | Material |
|---:|---:|---:|---:|
| 2 Min | 144 | 24.192 | 33,6 h |
| **3 Min** | **96** | **16.128** | **22,4 h** |
| 5 Min | 58 | 9.677 | 13,4 h |

**Bilder: 576/Stunde → 96.768 Bilder** (Generierung ~30 s — sechsmal schneller als Video)

### Und wie viele Videos werden daraus?

| Format | Clips/Video | @2 Min | **@3 Min** | @5 Min | Kredit-Gegenwert je Video |
|---|---:|---:|---:|---:|---:|
| SIGNAL 13 Min (8 % Deckung) | 13 | 1.909 | **1.273** | 764 | 247 Cr = 12 € |
| Story 20 Min (100 % Deckung) | 244 | 99 | **66** | 40 | 4.762 Cr = **226 €** |
| Sleep-Doku 2 h (50 % Deckung) | 720 | 34 | **22** | 13 | 14.040 Cr = **667 €** |
| **Sleep-Doku 2 h (Standbild-Weg)** | 0 (900 Bilder) | 108 | **108** | 108 | 3.600 Cr = **171 €** |

### Ein Tag, 12 Stunden beaufsichtigt

1.152 Clips bzw. 6.912 Bilder → **5 Story-Videos · 2 Sleep-Dokus (50 %) · 8 Sleep-Dokus (Standbild-Weg)**

## 📌 Der Gegenwert

| | Gegenwert in Credits | Preis |
|---|---:|---:|
| 66 Story-Videos à 20 Min | ~14.900 € | **99 €** |
| 22 Sleep-Dokus à 2 h | ~14.700 € | **99 €** |
| 108 Sleep-Dokus (Standbild-Weg) | ~18.500 € | **99 €** |

**Faktor 150.** Die Arbitrage ist echt und groß.

---

## 5. Der Punkt, der die ganze Rechnung dreht

### Für SIGNAL, wie es heute läuft, ist Unlimited **wertlos**.

Wir brauchen **13 Clips pro Folge = 247 Cr = 12 €**. Die 3.000 Credits/Monat des Ultra-Plans decken davon zwölf Folgen — dreimal mehr, als wir produzieren. **Unlimited löst ein Problem, das wir nicht haben.**

### Der eigentliche Hebel ist der Standbild-Weg

Die stärkste Zahl der Tabelle ist die letzte Zeile, und sie hängt **gar nicht am Video-Modell**:

- Nano Banana Pro 2K steht in **beiden** Unlimited-Paketen (7-Day *und* 365-Day) — der belastbarste Teil des Angebots
- Bildgenerierung ist **sechsmal schneller** als Video (30 s gegen 3 Min)
- Eine Zwei-Stunden-Sleep-Doku braucht bei 8 s Standzeit pro Bild **900 Bilder** — und Kamerafahrten macht ffmpeg lokal für 0 €
- Genau so bauen die Kanäle der Sleep-Nische ihre Videos

**In 7 Tagen sind 96.768 Bilder möglich. Das ist Material für über 100 zweistündige Videos.**

---

## 6. ⛔ Und jetzt der Einwand, der aus unseren eigenen Daten kommt

**Wer 108 Sleep-Dokus in einer Woche produziert, baut genau den Kanal, der in unseren Messungen stirbt.**

Muster 2 aus `research/nische-sleep-doku-de-analyse.md`, unabhängig bestätigt durch M1 in `research/konkurrenz-muster.md`:

| Kanal | Kadenz | Median |
|---|---:|---:|
| @Erdarchiv | **2,4/Monat** | **72.956** |
| @Das_Stille_Archiv | 2,7/Monat | 8.962 |
| @antike.chroniken | 13,8/Monat | 958 |
| @WissenschaftundSchlaf | **38,1/Monat** (192 Videos in 8 Mon) | **661** |
| @Physik_Traum | 28,5/Monat | 183 |

Der Zusammenhang ist eindeutig und in zwei unabhängigen Märkten reproduziert: **Masse produziert tote Mediane.** Ein Material-Berg verführt zu genau dieser Kadenz.

### Der richtige Gebrauch ist deshalb nicht Masse, sondern **Vorrat**

Bei 2–3 Videos/Monat über 12 Monate: **24–36 Videos** × 900 Bilder = **21.600–32.400 Bilder**.

Das passt in 7 Tage locker (96.768 möglich) — und ein Drittel davon passt in **einen einzigen Tag**. Der Unlimited-Kauf finanziert dann ein Jahr saubere Produktion bei richtiger Kadenz, statt eine Woche Slop.

---

## 7. Was ich empfehle

| Wenn… | dann… |
|---|---|
| **SIGNAL/Space bleibt der einzige Kanal** | **Nicht kaufen.** 3.000 Cr/Monat sind bereits dreifache Deckung |
| **Sleep-Doku wird wirklich angegangen** | **Kaufen — heute, sonst weg.** Aber als Vorratsbeschaffung für 12 Monate, nicht als Massen-Upload |
| **Story-Format (Nebula-Machart) wird getestet** | Kaufen und die 7 Tage für einen Pilot nutzen — 5 Videos an einem Tag ist genug für ein Urteil |

### Ein Argument, das unabhängig vom Unlimited-Teil zählt

ULTRA annual kostet **99 € für 12 × 3.000 = 36.000 Credits im Jahr**. Beim Top-up-Kurs (2.000 Cr = 95 €) kosten 36.000 Cr **1.710 €**.

**Der Plan allein ist Faktor 17 günstiger als Credits einzeln zu kaufen.** Das Unlimited-Paket ist die Zugabe, nicht der Grund.

⚠️ **Vorher im Konto prüfen:** Unser Guthaben liegt bei **200,9 Cr** bei aktivem Ultra-Plan. Wenn Ultra 3.000 Cr/Monat gutschreibt, müsste da mehr stehen. Entweder ist die Monatsmenge verbraucht (F1–F4 haben ~3.500 Cr gezogen, plus 2.000er-Topup) oder unser Ultra ist eine andere Variante. **Das gehört geklärt, bevor 99 € fließen** — sonst kauft man womöglich, was man schon hat.

---

## 8. Was an dieser Rechnung unsicher ist

1. **Die Generierungsdauer ist angenommen, nicht gemessen** (2/3/5 Min für Kling 3.0 720p/5s). Sie bestimmt den Durchsatz linear — bei 8 Min statt 3 halbiert sich alles.
2. **Der Effizienzfaktor 0,6 ist gesetzt.** Er soll Queue-Wartezeit, Fehlschläge und Re-Rolls abdecken. Unsere F4-Produktion hatte zwei 429-Rate-Limit-Fehlversuche bei nur 13 Jobs — bei 16.000 Jobs ist mit deutlich mehr zu rechnen.
3. **Fair-Use-Drosselung ist wahrscheinlich und nicht eingerechnet.** 96.768 Generierungen in 7 Tagen ist eine Größenordnung, bei der Anbieter üblicherweise begrenzen. Plane mit einem Bruchteil und prüfe nach den ersten Stunden den Ist-Durchsatz, statt auf die Modellzahl zu bauen.
4. **Ob die API das Kontingent ausgeben darf, ist offen** (§3). Ohne API ist der ganze Plan Handarbeit.
5. **„Buy until: July 31" ist der Wert aus der Plan-Antwort von heute.** Ob das Angebot morgen wirklich weg ist, kann ich nicht garantieren.

---

## CHANGELOG
- **31.07.2026** — Prüfung der Unlimited-Pläne für den „Skripte vorschreiben, dann Unlimited kaufen"-Plan. Befunde: **kein Tages-Plan** — 7-Day Unlimited ist eine Beigabe zum ULTRA-Jahreskauf (99 €, „Buy until: July 31"); das **einzige** unbegrenzte Video-Modell ist Kling 3.0 fest auf **720p/5s**; das 365-Day-Paket enthält ausschließlich Bildmodelle. Durchsatz ist die echte Grenze (8 parallele Slots): 7 Tage → 16.128 Clips = 66 Story-Videos oder 22 Sleep-Dokus, Gegenwert ~14.900 € für 99 € (**Faktor 150**). Stärkster Hebel ist der **Standbild-Weg** (96.768 Bilder = 100+ zweistündige Videos), weil Nano Banana Pro in beiden Paketen steht und 6× schneller ist. **Gegen-Befund aus eigenen Daten:** Kadenz korreliert negativ mit Median (38,1/Mon → 661 Views gegen 2,4/Mon → 72.956) — richtiger Gebrauch ist Vorrat für 12 Monate, nicht Masse. Offen: ob die API das Kontingent ausgeben darf („on web"-Fußnote, `unlim.available: false`), und warum das Guthaben bei aktivem Ultra nur 200,9 Cr beträgt. Rechner: `produktion/pipeline/unlim_durchsatz.py`.
