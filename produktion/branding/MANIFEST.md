# SIGNAL — Kanal-Branding

## Assets (Upload-fertig)
- `avatar_full.png` — **Kanal-Avatar** (800×800). Bildmarke Ringplanet (Saturn: geschummerte Sphäre + Cyan-Rim + 3D-Ring + Sterne), textlos → liest sich bis 48px im Feed. YouTube: Anpassen → Branding → Bild.
- `avatar_wordmark.png` — Glyph + „SIGNAL"-Wortmarke (800×800), für größere Verwendungen (Website, Presse, Endcard).
- `mark_only.png` — nur der Glyph, transparent (800×800) → **Video-Wasserzeichen** (YouTube: Branding → Video-Wasserzeichen).
- `banner.jpg` — **Kanal-Banner** (2560×1440, <6 MB). Alles Wichtige in der Safe-Area 1546×423. YouTube: Anpassen → Branding → Bannerbild.

## Pipeline (reproduzierbar)
- `make_brand.py` — zeichnet Avatar/Wortmarke/Wasserzeichen (Ringplanet-Marke, reines Pillow, supersampled).
- `make_banner.py` — Banner: Higgsfield-Hintergrund (Letterbox beschnitten) + Center-Scrim + Wortmarke/Tagline/Format-Zeile/Signal-Noise-Bar.

## Quellen
- Banner-Hintergrund: Higgsfield `nano_banana_2`, 16:9, 2k (2752×1536).
  - Gewählt (B): `52a69e8f-9815-4bb4-bf86-3299e3ffcf10`
  - Alternative (A): `f6d7981a-ff86-43aa-a918-afb2606d1c31`
  - `plates/*.png` und `banner.png` (groß) per .gitignore ausgeschlossen.
- Fonts: Anton (Wortmarke), DejaVu Mono (Tagline/Format) — nach scratchpad/fonts geladen.

## Brand-Konstanten
- Cyan `#2EE0E8` (Signal) · Amber `#F2B24C` (Noise) · Ink `#E9EFF7` · Near-black `#05070B`
- Tagline: „THE EVIDENCE BEHIND SPACE'S BIGGEST CLAIMS"
- Format-Zeile: „CLAIM · EVIDENCE · VERDICT"
