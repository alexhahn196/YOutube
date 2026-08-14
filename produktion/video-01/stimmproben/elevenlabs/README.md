# Stimmproben ElevenLabs — Stand: vorbereitet, noch nicht erzeugt

**Status:** Der Generator steht und laeuft auf Knopfdruck. Erzeugt ist noch nichts —
es fehlen zwei Dinge vom User (siehe *Was fehlt*).

---

## Was fehlt

1. **API-Key.** Noch nicht uebergeben. Ablage danach in `.eleven_key` neben diesem
   README oder als `ELEVEN_API_KEY` — die Datei ist ueber `.gitignore` gesperrt und
   wird nie geloggt.
2. **Testtext + `aussprache.md`.** Der im Auftrag genannte Pfad
   `produktion/video-01/aussprache.md` existiert in diesem Repo (`alexhahn196/YOutube`)
   nicht — auf keinem Branch, auch nicht in der Historie. Auch die Tempo-Vorgabe passt
   nicht zu diesem Kanal:

   | Quelle | gemessenes Tempo |
   |---|---|
   | Vorgabe aus dem ersten Stimmentest | **219 WPM** |
   | SIGNAL F1 (`skript/signal-01-v4-VO.md`, 2.000 Woerter / 13:12) | 151,5 WPM |
   | SIGNAL F2–F4 | 150–165 WPM |

   219 WPM ist also nicht das Tempo dieses Kanals. Der erste Stimmentest gehoert
   hoechstwahrscheinlich zu einem anderen Projekt (Namensschema `video-01` statt
   `folge-01` wie hier ueberall sonst).

---

## Aufbau, sobald der Text da ist

| Datei | Inhalt |
|---|---|
| `gen_samples.py` | Generator: 4 Stimmen x 2 Tempi, Tempo-Kalibrierung, Messung, Kostenerfassung |
| `config.json` | Stimmenauswahl (2 m / 2 w) + Textdatei — wird beim Lauf angelegt |
| `testtext.txt` | der Testtext (identisch zum ersten Anbieter) |
| `aussprache.pls` | aus `aussprache.md` erzeugtes W3C-Lexikon fuer das Woerterbuch |
| `messwerte.json` | pro Probe: speed-Faktor, Dauer, erreichtes WPM, abgerechnete Zeichen |
| `*.mp3` | die Proben (ueber `.gitignore` ausgeschlossen wie alle Medien im Repo) |

---

## Antworten auf die beiden Rueckfragen (aus der Doku, ohne Key pruefbar)

### 1. Woerterbuch-Funktion fuer Aussprache — ja

ElevenLabs hat **Pronunciation Dictionaries**. Anlegen per
`POST /v1/pronunciation-dictionaries/add-from-file` (multipart: `name`, `file`,
optional `description`, `workspace_access`). Die Antwort liefert `id` +
`version_id`; beides zusammen haengt man an jede TTS-Anfrage:

```json
"pronunciation_dictionary_locators": [
  {"pronunciation_dictionary_id": "...", "version_id": "..."}
]
```

Maximal **3 Woerterbuecher pro Anfrage**. Dateiformat ist das W3C-Lexikon `.pls`
(alternativ `.txt`). Zwei Regeltypen:

- **Alias** — ersetzt das geschriebene Wort durch eine andere Schreibweise, die
  gesprochen wird (`<alias>United Nations</alias>`). Funktioniert modelluebergreifend.
- **Phoneme** — exakte Lautschrift, IPA oder CMU-Arpabet (`<phoneme>AE P AH L</phoneme>`).

**Der Haken, der die Modellwahl bestimmt:** Phonem-Regeln greifen nur bei
`eleven_flash_v2` / `eleven_turbo_v2` / `eleven_english_sts_v2`. Bei
`eleven_multilingual_v2` — dem Modell, das laut Doku „most stable on long-form
generations" ist und das wir in F1 benutzt haben — wirken **nur Alias-Regeln**.
`eleven_v3` nimmt stattdessen IPA direkt im Text zwischen Schraegstrichen
(`/ˌbaɪoʊˈkemɪstri/`) und erreicht dabei laut Doku 80–90 % Konsistenz.

Praktische Folge: fuer eine deutsche Spur ist der Phonem-Weg versperrt (die
Phonem-faehigen Modelle sind englisch), es bleibt der Alias-Weg — Woerter werden
lautnah umgeschrieben statt in Lautschrift gesetzt. `gen_samples.py` erkennt beides:
steht die Aussprache in `/.../` oder `[...]`, wird eine Phonem-Regel gebaut, sonst
eine Alias-Regel.

Weitere Eigenheiten: Suche ist **case-sensitive**, und es gilt **first match wins** —
nur die erste passende Regel greift.

### 2. Einstellungen fuer Betonung und Tempo

| Parameter | Bereich | Wirkung |
|---|---|---|
| `speed` | 0,7–1,2 (Standard 1,0) | einziger echter Tempo-Regler; Extremwerte kosten Qualitaet |
| `stability` | 0–1 (Standard 0,5) | niedriger = mehr emotionale Bandbreite, hoeher = gleichfoermiger. Bei `eleven_v3` nur drei Stufen (Creative / Natural / Robust) |
| `style` | 0–1 (Standard 0) | verstaerkt den Stil der Stimme, erhoeht die Latenz |
| `similarity_boost` | 0–1 (Standard 0,75) | Naehe zur Originalstimme |
| `use_speaker_boost` | bool | Aehnlichkeit zum Sprecher |
| `<break time="1.5s" />` | max. 3 s | harte Pause; **nicht** in `eleven_v3`; zu viele Tags destabilisieren |
| Ellipsen `...`, Grossschreibung, Interpunktion | — | Pausen und Betonung, wirkt in allen Modellen |
| `[whispers]`, `[curious]` … | — | Audio-Tags, nur `eleven_v3` |
| `previous_text` / `next_text` | — | Kontext, damit Satzmelodie ueber Segmentgrenzen passt |
| `seed` | 0–4294967295 | reproduzierbare Generierung — wichtig, damit A/B-Vergleiche nicht am Zufall haengen |

**Geplante Wahl** (uebernimmt die in F1 bewaehrten Werte, damit die Proben zum
Kanal passen): Modell `eleven_multilingual_v2`, `stability` 0,45 · `similarity_boost`
0,75 · `style` 0,10 · `use_speaker_boost` an. Variiert wird ausschliesslich `speed`,
damit die zwei Tempi pro Stimme sich **nur** im Tempo unterscheiden.

**Warum kein WPM-Feld:** ElevenLabs kennt keine Wort-pro-Minute-Vorgabe. `gen_samples.py`
faehrt deshalb pro Stimme einen Kalibrierlauf bei `speed=1.0`, misst das erreichte
Tempo und rechnet den noetigen Faktor aus (`ziel / gemessen`, geklemmt auf 0,7–1,2).
Trifft der Kalibrierlauf ein Ziel schon, wird er wiederverwendet statt neu bezahlt.

**Wie das Tempo gemessen wird:** ueber
`POST /v1/text-to-speech/{voice_id}/with-timestamps`. Die Antwort enthaelt neben dem
Audio ein Alignment mit Start- und Endzeit jedes Zeichens; die letzte Endzeit ist die
Netto-Sprechdauer. Das ist exakt — kein Schaetzen ueber Dateigroesse, und in diesem
Container ist ohnehin kein ffmpeg/ffprobe vorhanden.

**Wie die Kosten gemessen werden:** `GET /v1/user/subscription` vor und nach dem Lauf;
die Differenz von `character_count` ist der real abgerechnete Verbrauch, nicht meine
Schaetzung. Zur Einordnung die Tarife (Stand 2026): Starter 6 $ / 20.000 Zeichen,
Creator 22 $ / 220.000, Pro 99 $ / 440.000, Scale 299 $ / 1.980.000, Business 990 $ /
5.980.000. Abrechnung fuer Multilingual v2 und v3 ca. 0,10 $ je 1.000 Zeichen,
Flash/Turbo ca. 0,05 $ — Flash haelt die Haelfte, kann aber kein stabiles Long-form.

---

## Gegenueberstellung der Anbieter

Wird gefuellt, sobald die Proben laufen. Die Spalten des ersten Anbieters kann ich
nicht selbst fuellen — die Messwerte des ersten Stimmentests liegen nicht in diesem
Repo.

| | Anbieter 1 (erster Test) | ElevenLabs |
|---|---|---|
| Stimmen (2 m / 2 w) | — | offen |
| Modell | — | `eleven_multilingual_v2` |
| Einstellungen | — | stability 0,45 · similarity 0,75 · style 0,10 · speaker-boost an · speed variabel |
| Tempo schnell (gemessen) | 219 WPM (Vorgabe) | offen |
| Tempo langsam (gemessen) | — | offen |
| Aussprache-Woerterbuch | — | ja, `.pls`, max. 3 pro Anfrage |
| Kosten | — | offen (Zeichen aus `character_count`-Differenz) |
