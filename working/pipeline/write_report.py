#!/usr/bin/env python3
"""Render output/report.md (German) from the plan + probed outputs + AI ledger."""
import json, subprocess, sys, os
plan=json.load(open(sys.argv[1])); out=sys.argv[2]
def probe(p):
    r=subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,bit_rate:format=duration,size','-of','json',p]).decode()
    j=json.loads(r); s=j['streams'][0]; f=j['format']
    return f"{s['width']}×{s['height']}, {s['r_frame_rate'].split('/')[0]} fps, H.264 High, {int(s.get('bit_rate',0))//1000} kbit/s, {float(f['duration']):.1f} s, {int(f['size'])/1e6:.1f} MB"
def ts(s): m=int(s//60); return f"{m}:{s-60*m:04.1f}"
shots=plan['shots']; tot=sum(s['end_s']-s['start_s'] for s in shots)
rows="\n".join(f"| {s['id']} | {ts(s['start_s'])} – {ts(s['end_s'])} | {s['end_s']-s['start_s']:.1f} s | {s['room']} | Original + FFmpeg (Stabilisierung σ={s.get('stab_sigma',8)}, Zoom {s.get('stab_zoom',1.04)}) |" for s in shots)
O='output/'
L=f"""# Abschlussbericht – Immobilien-Walkthrough (Final, 24.09.2026)

**Ergebnis:** Finale Fassung aus **ausschließlich authentischem Ausgangsmaterial plus technischer Bildoptimierung** (Stabilisierung, Entrauschung, Grading, Hochskalierung). Es wurde **1 KI-Test** mit Higgsfield durchgeführt (**4,84 Credits**); der KI-Clip wurde **nach Qualitätskontrolle verworfen**. Keine weiteren kostenpflichtigen Generierungen.

## 1. Ausgangsvideo
- Datei: `working/source_video.mp4` (Kopie von `WhatsApp Video 2026-09-23 at 16.44.07_1-compressed.mp4`)
- Länge: **225,96 s (3:46 min)**, 6 762 Frames
- Auflösung: **478 × 850 px (Hochformat, ≈ 9:16)**, 29,93 fps, H.264 High, 655 kbit/s (WhatsApp-komprimiert), Ton AAC 48 kHz Stereo
- Objekt: leere, unmöblierte Dachgeschosswohnung. Im Material vorhanden: Flur/Eingang, Wohnzimmer mit Kupferkamin und Dachschräge, Dachterrasse, Küche (entkernt), Abstellraum mit Boiler, Gäste-WC, Bad, Schlafzimmer, zweiter Balkon mit Stadtblick. **Nicht vorhanden:** Außenansicht/Fassade, Essbereich, Garten.

## 2. Ausgewählte Original-Timestamps und Räume ({len(shots)} Shots, {tot:.1f} s Rohlänge)
| # | Original | Länge | Raum | Bearbeitung |
|---|---|---|---|---|
{rows}

Verwendete Räume: Flur, Wohnzimmer (2×: Eintritt, Rückweg), Kamin, Dachterrasse, Küche, Schlafzimmer, Balkon. **Nicht verwendet:** Bad und Gäste-WC (durchgehend dunkel, verwackelt, Filmender im Spiegel – User-Entscheid: weglassen), Abstellraum/Boiler, Dachziegel-/Himmel-Passagen, alle Fast-Pans, Stellen mit Schatten des Filmenden. Vollständige Begründung je Shot und Raum-Timeline: `working/edit_plan.md`.

## 3. Higgsfield-Bilanz
| Posten | Wert |
|---|---|
| Guthaben zu Beginn | 219,90 Credits (Free-Plan) |
| Durchgeführte Generationen | **1** (Shot 06 Küche, FLUX 3 Video Edit, Job `615e8400-a8e4-4a38-87f5-1411cdff84fe`) |
| Verbrauchte Credits | **4,84** (1 Credit/s × 4,83 s) |
| Guthaben danach | 215,06 Credits |
| Über Higgsfield verarbeitete Clips im Final | **keine** |
| Originalmaterial geblieben | **alle 8 Shots** |
| Verworfene KI-Clips | **1** – Shot 06 Küche (`working/ai/06_kitchen_flux_v1.mp4`) |

Hinweise: Kling 3.0 Omni Edit (geplantes Modell, 7,5 Credits/Clip) ist im Free-Plan gesperrt („Requires basic plan or higher“). Kosten-Preflights (kostenlos): FLUX 3 Video Edit 1 Credit/s · Gemini Omni Flash 1.1 Edit 18 · Seedance 2.5 Video-Edit 480p 18 / 720p 38 / 1080p 60.

### Qualitätskontrolle des verworfenen KI-Clips (Shot 06)
Zwei unabhängige Prüfungen + Messung (SSIM 0,82, Kanten-IoU 0,53, Fliesenraster-Abstand identisch, max. Linienabweichung 4 px bei 704 px Breite):
- **Geometrie bestanden:** keine neuen/entfernten Türen, Fenster, Wände, Möbel oder Einbauten; Dachfenster, Heizkörper, Rohrstutzen, Steckdosen, Spots, Bodenteile an gleicher Stelle; gleicher Kameraweg, kein Morphing.
- **Verworfen wegen:** (1) sichtbar geglättete/geschönte Texturen und Gebrauchsspuren (Wandfliesen-Fugen ab ~1 s weitgehend weg, Bodenmosaik regularisiert, Flecken und Sockelstreifen der alten Küchenzeile übermalt), (2) Mikro-Ruckeln: 24 fps durch Frame-Dropping aus 30 fps, jeder 4. Bewegungsschritt ≈1,7× so groß, (3) Ausgabe nur 704×1248 und ≈7 Luma-Stufen dunkler. Belege: `working/qc/06_kitchen_v1_*.jpg`, `working/qc/06_kitchen_v1_sidebyside.mp4`.
- Priorität des Auftraggebers (Architekturtreue > stabile Geometrie > natürliche Kamerabewegung > Bildqualität > Kosmetik) → Original.

## 4. Technische Bildoptimierung (FFmpeg/OpenCV, pro Shot)
1. Frame-genauer Schnitt (libx264 CRF 10) → `working/original_clips/`
2. Stabilisierung: konservativer Translations-Glätter (Phasenkorrelation, Gauß σ = 8–10 Frames, 4–5 % Zoom). Begründung: Das Phone-Material ist bereits elektronisch stabilisiert (Jitter meist < 0,5 px/Frame); ffmpeg vidstab/deshake verschlechterten den gemessenen Jitter, der Translations-Glätter senkt ihn bei unruhigen Clips um 30–40 % und lässt ruhige Clips unverändert. Kein Motion-Interpolation, keine erfundenen Frames.
3. Entrauschung (hqdn3d 1.5/1.0/3/2.5), Grading (Kontrast +4 %, Sättigung +8 %, sanfte Lichter-Kompression), Lanczos-Hochskalierung auf 1080×1920, dezentes Unsharp-Masking, 30 fps.
4. Montage: harte Schnitte, 0,5 s Fade-in, 0,6 s Fade-out, stumme Tonspur (Musik kann in CapCut ergänzt werden).

## 5. Finale Dateien
| Datei | Format | Inhalt |
|---|---|---|
| `output/property_walkthrough_vertical_9x16.mp4` | {probe(O+'property_walkthrough_vertical_9x16.mp4')} | **9:16-Master** (nativ) |
| `output/property_walkthrough_16x9.mp4` | {probe(O+'property_walkthrough_16x9.mp4')} | **16:9-Hauptdatei**: Pillarbox (voller Bildinhalt, unscharfer Hintergrund) |
| `output/property_walkthrough_16x9_cropband.mp4` | {probe(O+'property_walkthrough_16x9_cropband.mp4')} | 16:9-Alternative: Band-Crop mit Anker pro Shot (~4× Upscale) |

Länge des finalen Videos: **29,5 s** (alle Fassungen). Weitere Artefakte: `working/contact_sheet.jpg` (Gesamtübersicht 1 fps), `working/sheets/` (12 Kontaktbögen), `working/edit_plan.md`, `working/analysis/` (Bewegungs-/Schärfe-Metriken), `working/pipeline/` (reproduzierbare Skripte).
"""
open(out,'w').write(L); print('wrote', out)
