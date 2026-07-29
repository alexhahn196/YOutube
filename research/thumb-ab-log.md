# Thumbnail-A/B-Log (CTR-Datenbank — Playbook §13 A/B-Pflicht + §14 Feedback-Loop)

> Pro Upload JEDE getestete Variante eintragen. 48 h nach Premiere Zwischenstand, 7 Tage nach Premiere Gewinner + Learning abschließen (§14). Auch Verlierer sind Daten — nie löschen.
>
> **Ziel nach 5–6 Folgen:** eigene CTR-Muster statt Konkurrenz-Proxys. Welche Anomalie-Typen ziehen? Wörter-Anzahl? Hell vs. dunkler? Diegetischer Text?

## Format je Eintrag
| Feld | Inhalt |
|---|---|
| Hypothese | Warum sollte DIESE Variante gewinnen? (vorher festlegen — sonst ist es kein Test) |
| CTR 48 h / 7 d | aus YouTube „Testen & Vergleichen" (Anteil der Impressionen, den YT der Variante gab + CTR) |
| Learning | 1 Satz. Fließt in die nächste Thumb-Produktion ein. |

---

## Retrofit-Aktion 29.07.2026 — alle Alt-Thumbs gemessen und ersetzt
Anlass: Longform-CTR **1,06 %** bei gesundem Band 4–6 %. Messung der **live laufenden** Thumbnails gegen §13b:

| live | Luminanz (Ziel ≥120) | Fast-Schwarz (Ziel ≤25 %) | Befund |
|---|---|---|---|
| F1 `master_01_ALIEN` | **41** | **68 %** | im Feed praktisch ein schwarzes Quadrat |
| F2 `master_f2_SIGNSOFLIFE` | 86 | 35 % | zu dunkel |
| F3 `master_f3_TURNEDAROUND` | 103 | 31 % | zu dunkel |

Alle drei durch v2-Muster ersetzt (`produktion/pipeline/make_thumb.py`): Split-Screen, helles Vollflächen-Banner mit schwarzer Frage, Helligkeit wird jetzt **maschinell nachgezogen**, bis das Ziel steht. Kosten: 0 € / 0 Credits.

## F1 — 3I/ATLAS (live seit 14.07., Retrofit 29.07.)
| Variante | Datei | Hypothese | CTR 48 h | CTR 7 d | Gewinner? | Learning |
|---|---|---|---|---|---|---|
| v1 (ersetzt) | folge-01-v4/thumbnail/master_01_ALIEN.jpg | — (vor §13 entstanden; Autopsie: **41/255 Luminanz, 68 % Fast-Schwarz**, Verdict im Bild) | 2,22 % @ 90 Impr. | — | ⛔ ersetzt | Negativ-Referenz: dunkel + Verdict im Schaufenster = 0-Klick-Beleg (§13) |
| **v2 A „WHERE'S IT FROM?"** | folge-01-v4/thumbnail/v2master_f1.jpg | Objekt + Bahn durchs Sonnensystem; Frage statt Verdict; Luminanz 122/7 % | | | | |
| v2 B „WHY IS IT HERE?" | folge-01-v4/thumbnail/v2variantB_f1.jpg | Seiten getauscht — testet, ob die Bahn als Blickfang schlägt; 123/7 % | | | | |
| v2 C (roter Kreis) | folge-01-v4/thumbnail/v2variantC_f1_mark.jpg | Konkurrenz-Mechanik testen | — | — | ⛔ nicht einsetzen | **Bau-Test 29.07.:** Motiv füllt schon die Bildhälfte → Kreis markiert das Offensichtliche und wirkt im Feed wie ein zufälliges rotes Oval. §13.7 präzisiert |

## F2 — K2-18b (Premiere Sa 18.07.2026)
| Variante | Datei | Hypothese | CTR 48 h | CTR 7 d | Gewinner? | Learning |
|---|---|---|---|---|---|---|
| Master „SIGNS OF LIFE?" (ersetzt) | folge-02/thumbnail/master_f2_SIGNSOFLIFE.jpg | Ozeanwelt + Gas-Plume-Anomalie | **2,7 % @ 73 Impr. (Tag 1)**, danach 0 % @ 57 Impr. | | ⛔ ersetzt | Autopsie: 86/255 Luminanz, 35 % Fast-Schwarz |
| **v2 A „IS IT ALIVE?"** | folge-02/thumbnail/v2master_f2.jpg | K2-18b (korrekte Hycean-Darstellung) + JWST als Autoritäts-Anker; 123/21 % | | | | |
| v2 B „WHAT DID WEBB SEE?" | folge-02/thumbnail/v2variantB_f2.jpg | Molekül als Beweisstück statt Instrument — testet Objekt vs. Autorität; 123/19 % | | | | |
| Challenger „IS IT ALIVE?" | folge-02/thumbnail/cand_v2_ISITALIVE.jpg | Größerer Planet + grüne Plume = stärkere Anomalie (Bauch-Favorit) | | | | |
| Challenger „LIFE? / Webb's strangest find" | folge-02/thumbnail/cand_v3_LIFE.jpg | Ein-Wort-Wucht + Autoritäts-Anker | | | | |

## F3 — Voyager (Premiere Sa 25.07.2026)
| Variante | Datei | Hypothese | CTR 48 h | CTR 7 d | Gewinner? | Learning |
|---|---|---|---|---|---|---|
| Master „TURNED AROUND?" (ersetzt) | folge-03/thumbnail/master_f3_TURNEDAROUND.jpg | | 0 % @ 41 Impr. | | ⛔ ersetzt | Autopsie: 103/255 Luminanz, 31 % Fast-Schwarz |
| **v2 A „DID IT TURN AROUND?"** | folge-03/thumbnail/v2master_f3.jpg | Sonde + Golden Record (ikonisch, gold = Farbkontrast im Feed); greift den Titel-Claim direkt als Frage auf; 121/18 % | | | | |
| v2 B „WHAT IS IT SENDING?" | folge-03/thumbnail/v2variantB_f3.jpg | Oszilloskop-Welle = das, was die Folge liefert; testet Neugier-Lücke gegen Claim-Ride; 122/9 % | | | | |
| v2 C (roter Kreis) | folge-03/thumbnail/v2variantC_f3_mark.jpg | Einziger sauberer Marker-Test: **identischer Crop wie A**, einziger Unterschied ist der Kreis. Gewinnt er, kippt §13.7 — verliert er, ist die Frage beantwortet | | | | |

## F4 — Wow!-Signal (Premiere Sa 01.08.2026)
| Variante | Datei | Hypothese | CTR 48 h | CTR 7 d | Gewinner? | Learning |
|---|---|---|---|---|---|---|
| v1 „SIX CHARACTERS" (verworfen) | folge-04/thumbnail/master_f4_SIXCHARACTERS.jpg | Printout-Makro — las sich im Feed nicht als Space-Content | — | — | ⛔ nie live | vor Upload durch v2 ersetzt |
| **v2 A „72 SECONDS"** | folge-04/thumbnail/v2master_f4_72SECONDS.jpg | Sternfeld + echter Printout mit Ehmans Kreis; 134/22 % | | | | |
| v2 B „WHO SENT IT?" | folge-04/thumbnail/v2variantB_f4_WHOSENTIT.jpg | Frage statt Zahl — testet Neugier gegen Zeit-Anker | | | | |
