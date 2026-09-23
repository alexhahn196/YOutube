# Bericht – Immobilien-Walkthrough (Stand: Vorschau v1, vor Higgsfield-Freigabe)

**Status:** Phasen 1–3 abgeschlossen, Phase 6/7 als FFmpeg-Vorschau gebaut. Phase 4/5 (Higgsfield) wartet auf Freigabe – es wurden **0 kostenpflichtige Generationen** gestartet (nur kostenlose Kosten-Preflights und ein Test-Upload).

## Ausgangsvideo
- Datei: `working/source_video.mp4` (Kopie von `WhatsApp Video 2026-09-23 at 16.44.07_1-compressed.mp4`)
- Länge: **225,96 s (3:46 min)**, 6 762 Frames
- Auflösung: **478 × 850 px (Hochformat, ≈ 9:16)**, 29,93 fps, H.264 High, 655 kbit/s (WhatsApp-komprimiert), Ton AAC 48 kHz Stereo
- Objekt: leere, unmöblierte Dachgeschosswohnung (Flur, Wohnzimmer mit Kupferkamin, Dachterrasse, entkernte Küche, Abstellraum mit Boiler, Gäste-WC, Bad, Schlafzimmer mit eigenem Balkon). Keine Außenansicht/Fassade im Material.

## Ausgewählte Original-Timestamps (8 Shots, 29.2 s)
| # | Original | Länge | Raum | Bearbeitung |
|---|---|---|---|---|
| 01 | 0:04.2 – 0:07.8 | 3.6 s | Flur (Eingangsbereich) | KI geplant (Kling 3.0 Omni Edit std) |
| 02 | 0:16.5 – 0:22.2 | 5.7 s | Wohnzimmer (Eintritt durch die Glastür, Fensterfront, Sonnenstreifen) | Original (FFmpeg-Bearbeitung) |
| 03 | 0:43.8 – 0:46.8 | 3.0 s | Wohnzimmer – Kamin (Kupferkamin unter der Holzdecke) | KI geplant (Kling 3.0 Omni Edit std) |
| 04 | 0:53.4 – 0:57.0 | 3.6 s | Dachterrasse (Austritt aus dem Wohnzimmer) | Original (FFmpeg-Bearbeitung) |
| 05 | 1:32.0 – 1:35.0 | 3.0 s | Wohnzimmer → Flur (zurück am Kamin vorbei, durch die Flurtür) | KI geplant (Kling 3.0 Omni Edit std) |
| 06 | 1:41.0 – 1:45.8 | 4.8 s | Küche (entkernt: alte Wandfliesen, Dachfenster, Heizkörper) | KI geplant (Kling 3.0 Omni Edit std) |
| 07 | 2:56.3 – 2:58.7 | 2.4 s | Schlafzimmer (Dachfenster, Heizkörper, Balkontür) | Original (FFmpeg-Bearbeitung) |
| 08 | 3:11.8 – 3:14.9 | 3.1 s | Balkon am Schlafzimmer (Blick über die Stadt) | Original (FFmpeg-Bearbeitung) |

Nicht verwendet: Bad und Gäste-WC (durchgehend dunkel, verwackelt, Filmender im Spiegel), Abstellraum/Boiler, Dachziegel/Himmel-Passagen, alle Fast-Pans. Details: `working/edit_plan.md`.

## Higgsfield
- Verfügbar über MCP (Guthaben zu Beginn: **219,9 Credits**, Free-Plan). Video-to-Video-Modelle mit Kosten-Preflight (pro Clip ≤ 6 s): Kling 3.0 Omni Edit std **7,5** / pro **10** · FLUX 3 Video Edit **≤ 15** · Gemini Omni Flash 1.1 Edit 720p **18** · Seedance 2.5 Video-Edit 480p **18** / 720p **38** / 1080p **60**.
- Geplant: 4 Generationen (Shots 01, 03, 05, 06) mit Kling std = 30 Credits, Reserve ≤ 15 Credits für konservative Re-Generationen. Noch nicht gestartet.
- Durchgeführte Generationen: **0** · verbrauchte Credits: **0** · verworfene KI-Clips: –

## Finale Videos (Vorschau v1, ohne KI)
- `output/property_walkthrough_vertical_9x16.mp4` – 1080×1920, 30 fps, H.264, **29,5 s**
- `output/property_walkthrough_16x9.mp4` – 1920×1080, 30 fps, H.264, **29,5 s** (16:9-Band-Crop mit Shot-Anker)
- `output/property_walkthrough_16x9_pillarbox.mp4` – 1920×1080, Alternative ohne Bildverlust (unscharfer Hintergrund)
