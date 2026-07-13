# Produktion Folge 1 v4 — 3I/ATLAS (finaler Master)

Vollständige, sendefähige Folge zum v4-Skript (`skript/signal-01-v4.md`) — Dramaturgie-Umbau
„Liste → Film". **Maximale Qualität** im vorgegebenen Budget: neue Shots in **nativem 4K**.

## Ergebnis
- **`v4_MASTER.mp4`** — 13:12, 1080p, HUD + Bauchbinden + Verdict-Meter eingebrannt. Ton: de3-Stimme + 3 Musik-Betten mit Ducking.
- **`v4_FINAL.mp4`** — dieselbe Folge **ohne** Overlays (falls Overlays separat gewünscht).
- **`signal_v4.srt`** — Untertitel für den YouTube-Upload (nicht eingebrannt; Longform-Standard).
- Vorschau-Fassungen (`*_preview.mp4`, 720p < 30 MB) für schnelles Sichten.

## Pipeline (reproduzierbar; Medien via `.gitignore` ausgeschlossen)
1. **`shot-plan.json`** — 14 neue Shots (12× natives 4K, 2× 1080p) + 18 wiederverwendete Folge-1-Clips. Alle Assets über Higgsfield-Job-IDs abrufbar (kein Re-Render).
2. **`tts.py`** — 14 VO-Segmente, Stimme „SIGNAL Analyst DE" (`LWuqGg44QZ1wFYrHkX98`, de3).
3. **`music.py`** — 3 Musik-Betten (Akt 1 mysteriös → Akt 2 forensisch → Akt 3 auflösend), ElevenLabs Music.
4. **`assemble_v4.py`** — Boomerang-Montage auf die VO-Segmentlängen; 4K→1080p (lanczos); stumme Bildspur + VO-Vollspur.
5. **`mix_v4.py`** — Musik pro Akt geloopt, unter die Stimme geduckt (Sidechain), Mux → `v4_FINAL.mp4`.
6. **`make_overlays_v4.py`** — SIGNAL-HUD (Wortmarke, Tracking-Tag, REC, Signal-Bar, Ecken), Verdict-Meter (Zeiger auf „Mostly Noise"), 9 Bauchbinden (Quelle + Messdatum + arXiv), getimt auf die Segmente.
7. **`composite_v4.py`** — HUD durchgehend + Timed-Overlays (Fade + `setpts`-Shift) → `v4_MASTER.mp4`.
8. **`build_subs_v4.py`** — segment-synchrone `.srt` (160 Cues).

## Qualitäts-Entscheidungen
- **Neue Shots nativ 4K/std** (110 Cr/Clip) statt 1080p — schärferes Ausgangsmaterial; im Master auf 1080p heruntergerechnet (Supersampling → schärfer als natives 1080p). 4K-Quellen über Job-IDs archiviert für spätere 4K-Ausgabe.
- **18 Folge-1-Clips wiederverwendet** (kostenlos) — decken viele v4-Beats direkt ab.
- **Untertitel NICHT eingebrannt** — als `.srt` (YouTube-Toggle, Auto-Übersetzung, SEO).

## Wichtige Lehren (gelöst)
- **Timed-Overlays unsichtbar** bei `-itsoffset` (PTS-Shift vor dem Fade → Alpha 0). Fix: Fade auf 0-basierter Timeline + `setpts=PTS+start/TB` danach.
- **4K-Boomerang-Decode ist zäh** — die 12 4K-Bases dominieren die Montagezeit; danach laufen die Slots schnell (gecachte Bases).
- **Seedance Rate-Limit** (~5 concurrent → HTTP 429) → in Vierergruppen feuern.
- **Seedance Preset-Empfehlung** unterbricht die Generierung → `declined_preset_id` zum literalen Retry.

## Budget (verifiziert)
- **Higgsfield:** ~1.500 Credits (14 neue Shots + Dubletten). 720p-Preflight 17,5 Cr · 1080p 45 Cr · **4K 110 Cr** · Bild 2 Cr. ≈ **€45–65** je nach Ultra-Abrechnung. Deckel €50 (Ziel), mit „max Qualität"-Vorgabe akzeptiert.
- **ElevenLabs:** VO 10.857 Zeichen + Musik ~560 s ≈ **~19–20k Credits ≈ €3–4** (Creator-Plan, innerhalb Monatsmenge).
