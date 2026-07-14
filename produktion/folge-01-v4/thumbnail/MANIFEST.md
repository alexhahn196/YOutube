# Thumbnail-Assets — Herkunft & Reproduktion

## Finale Thumbnails (committet, 1280×720 JPEG, YouTube-ready)
- `thumb_01_ALIEN.jpg` — **Haupt-Upload.** Hook „ALIEN?" (Cyan), Subtext „OLDER THAN THE SUN". Plate C02.
- `thumb_02_WRONGWAY.jpg` — B-Test. Hook „WRONG WAY" + Cyan-Pfeil auf die Sonne, Subtext „IT POINTS AT THE SUN". Plate C11.
- `thumb_03_NOTFROMHERE.jpg` — Grusel-Variante. Hook „NOT FROM HERE", Cyan-Reticle auf dem „Auge", Subtext „3I/ATLAS · TRACKED". Frisches Plate.

## Pipeline
- `compose_thumb.py` — spec-getriebener Pillow-Compositor (Scrim, Anton-Headline mit Glow+Stroke, SIGNAL-Wortmarke, Verdict-Meter, Extras: Pfeil/Kreis/Fragezeichen). Rendert 1280×720 JPEG < 2 MB.
- `thumbs.json` — die 3 finalen Specs.

## Quell-Plates
- C02 / C11: Frames aus `../clips/vid_C02.mp4` bzw. `vid_C11.mp4` (ss≈1.2s), wiederverwendet aus Folge-1-Produktion.
- Frisches Plate (Thumb 3): Higgsfield `nano_banana_2`, 16:9, 1376×768.
  - Job A (gewählt): `0a476fed-11b0-494b-93d8-2af753b274c9`
  - Job B (Alternative): `05470936-7ac3-4a2d-9858-2c2d3c2d589b`
  - Kosten: 2 Bilder ≈ 4–8 Cr. `plates/*.png` sind per .gitignore ausgeschlossen (über Job-IDs abrufbar).

## Fonts (nicht committet — nach scratchpad/fonts geladen)
- Anton-Regular.ttf (SIL OFL) — Headline. Quelle: google/fonts `ofl/anton`.
- ArchivoBlack-Regular.ttf (SIL OFL) — Subtext.
- DejaVu Sans Mono — Wortmarke/Meter (systemweit vorhanden).

## Design-Entscheidung
Aus 6 Konzepten (Design-Workflow) über 3 Juror-Lenses (CTR / Mobile / Brand+Honesty) bewertet.
Einstimmiger Sieger: „ALIEN?" (90/93/87). Cyan durchweg (schlägt Amber/Weiß bei 120px). Kein Rot (Tabloid),
kein Overclaim gegen das „Mostly Noise"-Verdict — jede Nicht-Frage-Hook ist eine wahre Aussage.
