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

## Noch offen (bewusst, kommt später)
- ElevenLabs-Voiceover (feste SIGNAL-Stimme) + Hintergrundmusik.
- CapCut-Finish: HUD-Overlay, Bauchbinden mit Messdatum/Quelle, Verdict-Meter (Zeiger „Leans Noise"),
  Untertitel (brauchen VO-Timing), und Shots auf die Erzähl-Länge dehnen (Ziel 15–20 Min).
- Echte NASA/GBT/ATA-Footage in S17/S22 gegen die KI-Platzhalter tauschen (Vertrauens-/Premium-Hebel).
