# SIGNAL — Folge 1: 3I/ATLAS — Higgsfield-Prompt-Sheet (Visuals)

> Gehört zu `scripts/episode-01-3IATLAS-v2.md` (faktenkorrigiert, Verdict = MITTEL/„Leans Noise").
> Zweck: produktionsreife Shot-Liste. Jeder Shot ist an einen Skript-Beat gekoppelt.
> **Trennung Quelle:** `[HF]` = Higgsfield-KI · `[NASA]` = echte gemeinfreie Footage (Premium-Hebel, unser Differenzierer) · `[CC]` = in CapCut gebaut (HUD/Label/Meter/Text).
> **Regel:** Teleskope, JWST/HST-Realbilder, reale Missionen → **[NASA] echt**. Objekt selbst, Kosmos-Beauty, Konzept, Bahn → **[HF] KI**. Marken-Overlays → **[CC]**.

---

## 0. SIGNAL — Style Bible (GESPERRT — in jedem Prompt gleich)

Damit alle Folgen im Feed sofort als „SIGNAL" erkennbar sind, hängt an **jeden** Higgsfield-Bild-Prompt derselbe Style-Block:

**STYLE-LOCK (ans Ende jedes [HF]-Bild-Prompts kopieren):**
```
cinematic space documentary, deep-space black background, cold blue-teal palette with a single CYAN accent light, high dynamic range, volumetric light, subtle film grain, photoreal, 8k, anamorphic, shallow depth cues, NASA/JWST plate aesthetic, no text, no logos, no watermark, 16:9
```

**Farb-/Look-Regeln:**
- Basis: Deep-Space-Schwarz + kühles Blau/Teal. **Genau EIN** Akzent: **Cyan** (Signal-Farbe). Kein Bunt-Chaos.
- Licht: 1 harte Hauptquelle (Sonne/Stern) + weiches Fill. Immer klarer Kontrast Objekt ↔ Schwarz.
- Kamera: langsam, schwer, „Mission-Control"-ruhig. Keine hektischen Moves.
- Keine Menschen, keine Gesichter (faceless-Kanal). Kein Text im Bild (Text kommt in CapCut).

**GLOBAL NEGATIVE PROMPT (immer mitgeben):**
```
text, letters, captions, watermark, logo, ui, low quality, blurry, jpeg artifacts, oversaturated, rainbow colors, cartoon, childish, cluttered, human face, people, distorted planet, extra moons, fake constellations, lens dirt overload
```

**Seitenverhältnis:** 16:9, 3840×2160 (4K master) wo möglich, sonst 1920×1080.

---

## 1. Modell-Cheat-Sheet (welches Higgsfield-Modell wofür)

| Job | Modell (Higgsfield) | Warum |
|---|---|---|
| **Start-Standbild** (Objekt, Kosmos, Konzept) — höchste Detailtreue | `nano_banana_pro` | schärfste, konsistenteste Stills; gut für Wiedererkennungs-Look |
| Standbild schnell / Varianten-Masse | `z_image` oder `image_auto` | schnelle Iteration, günstig |
| **Bild→Video** (Beauty-Kosmos, langsamer Push, Parallax) | `Seedance 2.0` | ruhige, filmische Kamerafahrten aus Standbild |
| Bild→Video mit stärkerer Eigenbewegung (Gas, Jets, Staub) | `Kling v3.0` | dynamischere Physik-Anmutung |
| **Text→Video Hero-Shot** (wenn kein Startbild nötig, max. Kino) | `Veo 3` | bester Prompt-Gehorsam + Kohärenz für 1–2 Signature-Shots |
| Budget-Bild→Video | `Wan 2.7` | günstig für Füll-Shots |

**Workflow pro [HF]-Shot:** 1) Standbild mit `nano_banana_pro` (Bild-Prompt unten). → 2) Standbild als Startframe in `Seedance 2.0`/`Kling v3.0` mit dem **Motion-Prompt** animieren. → 3) In CapCut mit HUD/Label/Meter overlayen.

---

## 2. Marken-Overlay-Kit (CapCut, EINMAL bauen, über ALLES legen)  [CC]

Nicht in Higgsfield — das ist die feste CapCut-Vorlage (unser stärkster Wiedererkennungshebel):
- **HUD-Rahmen:** dezente Ecken-Readouts, ein Signatur-Reticle mittig-schwach, oben rechts eine **„SIGNAL STRENGTH"-Leiste**. Cyan auf Schwarz, ~15 % Deckkraft, damit es nie das Bild erschlägt.
- **Segment-Label-Karten:** `THE CLAIM` / `THE EVIDENCE` / `THE VERDICT` — gleiche Schrift, Cyan-Akzent, kurze Einblend-Animation.
- **Intro-Sting (3 s):** Logo-Animation + Audio-Logo. Jede Folge identisch.
- **Verdict-Meter:** Halbkreis-Skala `SIGNAL ↔ NOISE` mit 5 Stufen: *Confirmed Signal · Leans Signal · Unresolved · Leans Noise · Mostly Noise*. **Zeiger diese Folge: „Leans Noise"** (klar Noise-Seite, NICHT am Anschlag).
- **Untertitel:** feste Marken-Schrift, Cyan-Akzentwort.
- **Quellen-Bauchbinden:** bei jedem Fakt kurz Quelle klein einblenden (Vertrauens-Marke) — z. B. „JWST · Aug 2025", „Green Bank · 18 Dec 2025".

---

## 3. Shot-Liste (an die Skript-Beats gekoppelt)

Format je Shot: **ID · Timecode · Quelle · Beat** → **BILD-Prompt** / **MOTION-Prompt** / **Overlay**.

### COLD OPEN / HOOK (0:00–0:35)

**S01 · 0:00–0:12 · [HF] · „etwas fällt durch unser System, das nicht von hier ist"**
- BILD (`nano_banana_pro`): `Extreme wide shot of deep interstellar space, a single faint blurry point of light slightly off-center, faint dust and distant stars, sense of vast emptiness, one cold cyan glint on the object` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `very slow forward push toward the faint point of light, subtle parallax on foreground dust, near-still, weighty and quiet, 8s`.
- Overlay [CC]: HUD leise einblenden; SIGNAL STRENGTH beginnt zu „scannen".

**S02 · 0:12–0:25 · [HF] · Reveal: das Objekt, kalter Kometenschimmer + Andeutung Anti-Tail**
- BILD (`nano_banana_pro`): `A dark, elongated icy interstellar object drifting, faint cyan coma, a thin faint dust plume pointing slightly TOWARD the distant bright sun (anti-tail hint), Sun as small hard light source far right, cold and alien` + STYLE-LOCK.
- MOTION (`Kling v3.0`): `slow drift left-to-right, faint coma shimmer, dust plume gently streaming toward the sun, subtle rotation, 8s`.
- Overlay [CC]: Ecken-Readouts „INTERSTELLAR · e>6".

**S03 · 0:25–0:35 · [HF] · Aufbau „alien technology?" → Übergang in Sting**
- BILD (`nano_banana_pro`): `Same object seen closer, ambiguous surface — could read as rock or as something engineered, hard rim light in cyan, deep shadow, unsettling, question-mark mood, no clear machine parts` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `slow ominous dolly-in, shadow creeps across surface, 6s`.
- Overlay [CC]: kurz Text-Flash (in CapCut) „ALIEN?" → hart auf **INTRO STING**.

**S04 · 0:35–0:38 · [CC] · INTRO STING / LOGO (3 s).** Feste Vorlage, kein HF.

---

### SEGMENT 1 — THE CLAIM (0:38–4:00)

**S05 · 0:38–0:45 · [CC] + [HF-BG] · Label „THE CLAIM" + Schlagzeilen-Collage**
- BILD (`z_image`, nur Hintergrund): `dark cyan-tinted abstract space background, subtle data-grid texture, empty center for headline cards` + STYLE-LOCK.
- Overlay [CC]: `THE CLAIM`-Karte; Fake-neutrale „Headline"-Karten (selbst gebaut, keine echten fremden Logos): „Is it ALIEN?", „3rd Interstellar Visitor", „Broke Every Rule".

**S06 · 0:45–1:20 · [HF] · Die drei interstellaren Besucher (Kontext ʻOumuamua / Borisov / ATLAS)**
- BILD (`nano_banana_pro`): `A triptych-style cosmic lineup: far left a small dark elongated rocky sliver (Oumuamua), center a small fuzzy comet with short tail (Borisov), right the new object glowing cold cyan and clearly the strangest, deep space, consistent scale cues` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `slow lateral truck revealing the three in sequence, gentle push settling on the right object, 8s`.
- Overlay [CC]: kleine Labels „1I ʻOumuamua 2017 · 2I Borisov 2019 · 3I/ATLAS 2025".

**S07 · 1:20–2:00 · [HF] · Hyperbolische, ungebundene Bahn (das Schlüsselbild „open path")**
- BILD (`nano_banana_pro`): `Diagram-real hybrid: the Sun at center with faint planetary orbit ellipses, and ONE dramatic open hyperbolic trajectory slicing through and exiting, glowing cyan, clearly not a closed loop, dark space, elegant orbital-mechanics look` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `camera slowly orbits the plane, the cyan hyperbola draws itself in one pass and continues off-frame, 8s`.
- Overlay [CC]: „ECCENTRICITY 6.14 — HIGHEST EVER" (Bauchbinde, Quelle klein).

**S08 · 2:00–2:50 · [HF] · Avi Loeb / die „22 Anomalien"-Idee (ohne Gesicht)**
- BILD (`nano_banana_pro`): `A dark observatory desk mood, a glowing cyan analyst screen showing an abstract list of 22 faint anomaly markers and a 0–10 scale with a marker on 4, no readable text, no person, cold and clinical` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `slow push toward the screen, the 0–10 scale marker settles on 4, 7s`.
- Overlay [CC]: Text „SCALE 0–10 · rated 4 = anomalous, most likely natural" (Korrektur K6 sichtbar machen).

**S09 · 2:50–4:00 · [HF] · Teaser der 3 Oddities (Anti-Tail / inside-out Chemie / Metall)**
- BILD A Anti-Tail (`nano_banana_pro`): `comet with tail pointing the WRONG way, toward the sun, cyan dust` + STYLE-LOCK.
- BILD B Chemie (`nano_banana_pro`): `cutaway of a frozen comet nucleus, cross-section showing CO2-dominant ices, only a thin water layer, cold blue, molecular-cloud vibe, abstract not labeled` + STYLE-LOCK.
- BILD C Metall (`nano_banana_pro`): `faint metallic vapor glow around the nucleus, cold nickel-cyan shimmer, hint of industrial-looking spectral lines as abstract light streaks` + STYLE-LOCK.
- MOTION: je 4–5 s langsamer Push (`Seedance 2.0`), schneller Schnitt-Rhythmus in CapCut.
- Overlay [CC]: Mid-Video-Abo-Ask am Spannungs-Peak (Skript-Zeile „Subscribe; we're following…").

**MID-ROLL 1 (~4:00).**

---

### SEGMENT 2 — THE EVIDENCE (4:00–~12:00)

**S10 · 4:00–4:10 · [CC] + [HF-BG] · Label „THE EVIDENCE" (nüchterner, daten-getriebener Look-Wechsel)**
- BILD (`z_image`): `cleaner, more clinical deep-space background, faint data grid, cooler and more sober than Segment 1` + STYLE-LOCK.
- Overlay [CC]: `THE EVIDENCE`; HUD wird „präziser" (mehr Readouts).

**S11 · 4:10–5:20 · [HF] · Herkunft: galaktische Thick Disk, Relikt > 7,6 Mrd. Jahre**
- BILD (`nano_banana_pro`): `Grand view of the Milky Way seen edge-on, highlighting the older, puffed-up THICK DISK population in warm-old tones vs the thin bright disk, one cyan trajectory arriving from the ancient region toward us, epic and old` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `slow majestic pull-back revealing the galaxy edge-on, cyan path traces from thick disk inward, 8s`.
- Overlay [CC]: „>7.6 billion years — likely older than the Sun · Hopkins et al. 2025" (Korrektur K8).

**S12 · 5:20–6:30 · [HF] · Bahn-Chronologie: Perihel 29.10.2025 · Erdannäherung 19.12. · Jupiter 03/2026**
- BILD (`nano_banana_pro`): `Solar-system orbital view, the cyan hyperbola passing between Earth and Mars orbits at perihelion, then a marked closest-Earth point, then a Jupiter flyby, clean orbital-mechanics aesthetic, Sun hard light center` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `the object animates along the cyan path hitting each marked node in sequence, calm, 10s (kann geteilt werden)`.
- Overlay [CC]: Timeline-Marker „Perihelion 29 Oct 2025 · Closest Earth 19 Dec 2025 (no maneuver) · Jupiter Mar 2026" (Korrektur K9+K2).

**S13 · 6:30–7:30 · [HF] · Der „rückwärtige" Anti-Tail + Präzedenzfall**
- BILD (`nano_banana_pro`): `Clear hero shot of the comet with a distinct ANTI-TAIL of large heavy dust grains drifting off the sunlit side toward the Sun, physically plausible, cyan-lit, alongside a faint ghost of a second precedent comet for comparison` + STYLE-LOCK.
- MOTION (`Kling v3.0`): `heavy dust grains slowly stream from the sunlit side toward the sun, tail shape holds, 8s`.
- Overlay [CC]: „Anti-tail: also seen in C/2014 UN271 (2021) — ordinary physics · Wright & Keto" (Korrektur K5).

**S14 · 7:30–9:00 · [HF] · Inside-out-Chemie & die AUFLÖSUNG beim Aufwärmen (Kern-Beat!)**
- BILD A prä-perihel (`nano_banana_pro`): `frozen comet far from the sun, mostly CO2 ice sublimating as faint cold jets, very little water vapor, deep-frozen blue` + STYLE-LOCK.
- BILD B post-perihel (`nano_banana_pro`): `same comet now close to the sun and fully active, water vapor surging ~40x brighter, methane jets appearing, a normal vigorous coma, warmer active glow but keep cyan accent` + STYLE-LOCK.
- MOTION (`Kling v3.0`): A→B als Zeitraffer-Aufwärmung: `the frozen quiet comet ignites into a full active coma as it nears the sun, water vapor blooms, 8s`.
- Overlay [CC]: Split „JWST Aug 2025: 87% CO₂ / ~4% H₂O" → „Dec 2025: H₂O ×40, CH₄ appears, CO₂/H₂O collapses" (Korrektur K3). **Das ist der wichtigste Beweis-Beat — hier Zeit lassen.**

**S15 · 9:00–9:50 · [HF] · Das „fehlende Eisen" erscheint post-perihel**
- BILD (`nano_banana_pro`): `abstract spectral visualization around the nucleus: first only nickel-cyan emission lines, then iron lines appearing alongside as it warms, light-streak spectral aesthetic, not labeled` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `iron spectral lines fade in next to the nickel lines, ratio balancing out, 6s`.
- Overlay [CC]: „Post-perihelion: Fe I appears · Ni/Fe ≈ comet Tempel 1" (Korrektur K4).

**S16 · 9:50–11:00 · [HF] · Die 3 stärkeren Anomalien (Steelman — ehrlich benennen)**
- BILD A Wow!-Richtung (`nano_banana_pro`): `star map with the arrival direction of the object 9 degrees from the famous Wow! signal direction, two faint cyan markers close together on a dark sky sphere` + STYLE-LOCK.
- BILD B transversaler Schub (`nano_banana_pro`): `the comet with a subtle SIDEWAYS thrust vector visualized as a faint cyan arrow not pointing straight away from the sun, uneven venting jets` + STYLE-LOCK.
- BILD C 3-Jet-Symmetrie (`nano_banana_pro`): `nucleus emitting three roughly symmetric jets ~120 degrees apart, cold cyan, striking geometry` + STYLE-LOCK.
- MOTION: je 4 s (`Kling v3.0` für Jets/venting).
- Overlay [CC]: je Anomalie ein kurzer „…and its natural explanation" Konter (Korrektur K7). Kommentar-Trigger-Moment.

**S17 · 11:00–12:00 · [NASA] + [HF] · Die Radio-Suchen (STÄRKSTER BELEG) — Green Bank & Allen Array**
- **[NASA/echt] Green Bank Telescope:** reale gemeinfreie GBT-Aufnahme (NRAO/NSF public domain) — Nacht-Himmel, riesige Schüssel. Premium-Vertrauens-Shot.
- **[NASA/echt] Allen Telescope Array:** reales gemeinfreies ATA-Bild (SETI Institute Pressematerial / gemeinfrei prüfen) — Feld aus Antennen.
- **[HF] Verbindungsschuss:** `nano_banana_pro`: `a radio telescope dish pointed at the faint distant object, thin cyan listening-beam reaching across 270 million km toward it, silence visualized, no signal returning` + STYLE-LOCK. MOTION (`Seedance 2.0`): `beam reaches out, scans, returns nothing, 8s`.
- Overlay [CC]: „Green Bank · 18 Dec 2025 · nothing above 100 mW (weaker than a cell phone)" + „Allen Array · 74M hits → all human/satellite → 0 from object" (Korrektur K1). **Bauchbinden mit Messdatum = Vertrauens-Peak.**

**S18 · 12:00–12:20 · [HF] · Loebs „most likely natural" / Konsens**
- BILD (`nano_banana_pro`): `the 0–10 analyst scale again, marker firmly on 4, cool cyan, calm clinical resolution` + STYLE-LOCK.
- Overlay [CC]: „Loeb: rated 4 = 'most likely natural' — not a reversal · Consensus: natural, unusual comet".

**MID-ROLL 2 (optional bei längerer Fassung).**

---

### SEGMENT 3 — THE VERDICT (12:20–~14:00)

**S19 · 12:20–12:30 · [CC] · Label „THE VERDICT" + Meter fährt auf „Leans Noise"**
- BILD [HF-BG] (`z_image`): `dark cyan verdict-screen background, empty for the meter graphic` + STYLE-LOCK.
- Overlay [CC]: **Verdict-Meter fährt sichtbar auf „Leans Noise"** (klar Noise-Seite, kurz vor Anschlag). Zeiger-Rest-Abstand = die offenen Punkte.

**S20 · 12:30–13:20 · [HF] · Verdict-Voiceover-Bett (ehrliche Auflösung)**
- BILD (`nano_banana_pro`): `the object now seen leaving, receding toward deep space, still cold and strange but clearly a natural comet with an active coma, dignified, the Sun behind it, a sense of 'most likely, not case-closed'` + STYLE-LOCK.
- MOTION (`Seedance 2.0`): `slow pull-back as the comet recedes, coma trailing, calm and final, 10s`.
- Overlay [CC]: dezent die 4 PRO-Punkte antippen; dann kurz die 2 offenen (transversaler Schub, Wow!-9°) → hält die Kommentar-Frage offen.

**S21 · 13:20–13:50 · [HF] · Payoff-Beat „not aliens ≠ not amazing" (Relikt älter als die Sonne)**
- BILD (`nano_banana_pro`): `awe shot: the ancient interstellar comet against the vast Milky Way, emphasis on deep time, a relic older than the Sun, humbling scale, cyan accent` + STYLE-LOCK.
- MOTION (`Seedance 2.0` oder Veo 3 als Hero): `slow reverent push, galaxy behind, 8s`.
- Overlay [CC]: „A relic older than our Sun — passing through once, forever.".

**S22 · 13:50–14:00 · [NASA/HF] · Ausblick Vera Rubin (Cliffhanger für die Serie)**
- **[NASA/echt]** reales gemeinfreies Vera-C.-Rubin-Observatorium-Bild (NSF/DOE/Rubin Obs · public domain) — falls verfügbar.
- **[HF]** Alternativ: `nano_banana_pro`: `a large modern survey observatory dome under a star-blazing sky, cyan glow, sense of 'the next discovery is coming'` + STYLE-LOCK.
- Overlay [CC]: „Rubin will find more interstellar visitors — subscribe, we track them all.".

---

### OUTRO / CTA (14:00–~14:30)

**S23 · [CC] + [HF-BG] · Endcard: Verdict-Frage + Abo + nächstes Objekt**
- BILD [HF-BG] (`z_image`): `clean SIGNAL end-card cosmic background, space for two video thumbnails and a subscribe button` + STYLE-LOCK.
- Overlay [CC]: Pinned-Frage „Natural comet or something engineered? SIGNAL or NOISE? Which interstellar object next?" + Abo-Button + Teaser nächste Folge („Did JWST find the first sign of alien life?").

---

## 4. NASA/ESA-Footage-Einkaufsliste (gemeinfrei — VOR Produktion sichern)

Diese echten Assets heben uns von reinem KI-Slop ab (Vertrauens-/Premium-Hebel). Immer Lizenz prüfen (NASA-Bilder i. d. R. public domain; ESA/Rubin/NRAO je Quelle prüfen):
- **HST / JWST** Objekt- & Kometen-Realaufnahmen (NASA/ESA/STScI) — für „echt gemessen"-Momente in S14/S15.
- **Green Bank Telescope** (NRAO/NSF) — S17.
- **Allen Telescope Array** (SETI Institute) — S17 (Lizenz prüfen).
- **Vera C. Rubin Observatory** (NSF/DOE) — S22.
- **Milchstraßen-Panorama / Thick-Disk** (ESO/NASA) — S11.
- Generische NASA-Kometen-/Tiefraum-B-Roll als Zwischenschnitte.

> **Wichtig:** Fremde YouTube-Thumbnails/News-Logos NICHT verwenden (IP). „Schlagzeilen" in S05 selbst als neutrale Karten bauen.

---

## 5. Export- & Konsistenz-Specs
- **Master:** 16:9, 4K (3840×2160) wo möglich, 24–30 fps, H.264/H.265.
- **Style-Lock** an JEDEN HF-Bild-Prompt anhängen (Abschnitt 0) → Serien-Look.
- **Eine feste TTS-Stimme** (SIGNAL-Analyst) über alles — nie wechseln.
- **HUD-Overlay + Meter + Labels** aus der EINEN CapCut-Vorlage — nie neu bauen.
- Pro Shot 2–3 Higgsfield-Varianten ziehen, beste wählen; Seeds/Prompt der Gewinner notieren (Wiederverwendung Folge 2ff).

---

## 6. Pilot-Render-Log (Look-Kalibrierung)

**S02 — Standbild (`nano_banana_pro`, 4K, 16:9, SIGNAL-Style-Lock):**
- Variante 1 (GEWÄHLT für S02, klarer Reveal): Job `7efb7219-4ba9-4cf3-8d71-b1145d86d4f8` · 5504×3072
- Variante 2 (empfohlen als S03-Asset, düstere Silhouette): Job `e2316c46-cd5d-4b87-bbd8-7ccf8d0d613d` · 5504×3072
- Ergebnis: Style-Lock funktioniert — Deep-Space-Schwarz, kühles Blau-Teal, EIN Cyan-Akzent, photoreale NASA-Plate-Anmutung, kein Text. **Look ist kalibriert → Serien-Standard.**

**S02 — Motion-Test (`Seedance 2.0`, 1080p, 6s, `mode=std`, stumm):**
- Job `5a033b7c-4cc1-4b4e-9981-b8eaa5ebc18d` · Startframe = Variante 1
- Motion-Prompt bewährt (langsamer Drift, Koma-Schimmer, Anti-Tail zur Sonne). Hinweis: `std`-Queue war langsam (~15 Min) — für Massen-Shots ggf. `mode=fast` (720p) für Vorschau, Finals in `std`.

> **Reproduzierbarkeit:** Assets nicht im Repo (4K-PNGs ~20 MB). Über die Job-IDs jederzeit in Higgsfield abrufbar (`job_display`). Gewinner-Seeds/IDs hier gepflegt für Folge 2ff.

## 7. Nächster Schritt (Vorschlag)
Look ist kalibriert. Optionen: (a) **restliche Hero-Shots** von Segment 1 (S06 Triptychon, S07 Bahn) rendern, um den Serien-Look über mehrere Motive zu bestätigen; oder (b) direkt **S02 in 4K final** + HUD-Overlay-Vorlage in CapCut bauen. Empfehlung: erst (a) — 2–3 weitere Motive testen, dann Batch-Produktion.
