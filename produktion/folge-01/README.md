# Produktion Folge 01 — 3I/ATLAS (visueller Master, stumm)

Reproduzierbare Render-Pipeline für den **stummen visuellen Master** von Folge 1.
Ton/Sprache (ElevenLabs) + Musik + HUD/Bauchbinden/Untertitel kommen in CapCut darüber.

## Dateien
- **`render-manifest.json`** — die Single Source of Truth: 18 Shots (C01–C21), je mit
  Bild-Prompt, Motion-Prompt, `image_job` (nano_banana_pro) und `video_job` (Seedance 2.0).
  Über die Job-IDs sind alle Assets jederzeit in Higgsfield abrufbar (kein Re-Render nötig).
- **`download.py`** — lädt die gerenderten Clips per `url_map.json` (job→URL) nach `clips/<id>.mp4`.
- **`assemble.py`** — Zwei-Pass-Montage: normalisiert jeden Clip auf 1080p/30fps CFR mit
  kurzen Ein-/Ausblenden, fügt die Segment-Titelkarten (SIGNAL / THE CLAIM / THE EVIDENCE /
  THE VERDICT) ein und concatet verlustfrei zum Master.

## Ergebnis
- **`signal_ep01_master.mp4`** — 23 Segmente (18 Shots + 5 Titelkarten), ~120 s, 1080p, stumm.
- Look: SIGNAL-Hausstil (Deep-Space-Schwarz, kühles Blau-Teal, EIN Cyan-Akzent, NASA-Plate-Anmutung).
- Die Medien selbst liegen NICHT im Repo (per `.gitignore` ausgeschlossen, regenerierbar über Job-IDs).

## Wichtige Lehren aus dem ersten Durchlauf
- **Seedance-Rate-Limit:** max. ~3–5 Video-Jobs pro kurzem Zeitfenster, sonst HTTP 429.
  → in Gruppen à ~3 feuern, kurze Pausen dazwischen.
- **ffmpeg (imageio-ffmpeg-Build):** `drawtext`-Filter fehlt → Titelkarten via Pillow (PNG);
  `xfade` scheitert an der Framerate → stattdessen Ein-/Ausblenden pro Clip + concat-demuxer.
- **Bild→Video:** Seedance nimmt die Bild-`job_id` direkt als `start_image` (kein lokaler Upload nötig).

## Vertonung (ElevenLabs, per API)
- **`elevenlabs_pipeline.py`** — Voice Design (erzeugt die einzigartige „SIGNAL Analyst"-Stimme aus
  einem Text-Prompt) + Text-to-Speech. Liest den API-Key aus `.eleven_key` (NIE committen).
  Stimme: **Voice-ID `7ATeax5x9LSXQT93oICL`** (Modell `eleven_multilingual_v2`,
  Settings Stability 0.45 / Similarity 0.75 / Style 0.10 / Speaker-Boost an).
- **VO-Skript:** `scripts/episode-01-3IATLAS-VO.md` (5 Segmente, ~12 Min gesprochen).
- **Musik:** 3 Betten über die ElevenLabs Music-API (mysteriös → analytisch → auflösend),
  je zur Segment-Länge; Prompts ohne Film-/Künstlerreferenzen (ToS-Filter).
- **`final_assemble.py`** — timt die 18 Shots per **Boomerang-Loop** auf die VO-Segmentlängen,
  fügt Titelkarten ein, mischt VO (voll) + Musik (leise, gefadet) und muxt →
  **`signal_ep01_FINAL.mp4`** (12:07, 1080p, AAC-Stereo).

## Finish-Layer (HIER gebaut, kein CapCut noetig)
- **`build_subs.py`** — ElevenLabs **Forced Alignment** (`/v1/forced-alignment`) auf die
  bestehenden `vo_seg*.mp3` → exakte Wort-Zeiten → `subtitles.ass` (294 Cues) + `bauchbinden.json`
  (13 Quellen-Bauchbinden, Zeitpunkte per Anchor-Phrasen automatisch gefunden).
- **`make_overlays.py`** — rendert die SIGNAL-Overlays als PNG (Pillow): persistentes **HUD**
  (Ecken, SIGNAL-Wortmarke + Signal-Strength-Bar, Reticle, Tracking-Tag), **Verdict-Meter**
  (Zeiger auf „Leans Noise"), 13 **Bauchbinden-Karten** (Quelle + Messdatum je Fakt).
- **`composite.py`** — legt HUD (immer), Bauchbinden + Meter (zeitgesteuert, mit Fades) drueber
  und **brennt die Untertitel** (libass `subtitles`-Filter) ein → `signal_ep01_MASTER_final.mp4`.
  Audio wird kopiert (der gemischte Ducking-Ton bleibt).

## Noch offen (optional)
- Mehr B-Roll-Shots, damit die Shot-Holds im Evidence-Teil kürzer werden (aktuell ~47 s/Shot).
- Echte NASA/GBT/ATA-Footage in S17/S22 gegen die KI-Platzhalter tauschen (Vertrauens-/Premium-Hebel).
- Thumbnail + Titel/Beschreibung + Pinned-Comment fuer den Upload.
