#!/usr/bin/env python3
"""Render working/edit_plan.md from the plan JSON (German)."""
import json, sys
plan = json.load(open(sys.argv[1])); out = sys.argv[2]
def ts(s): m=int(s//60); return f"{m}:{s-60*m:04.1f}"
L = ["# Schnittplan – Immobilien-Walkthrough (~30 s)", "",
     f"Quelle: `{plan['source']}` (Hochformat 478×850, 29,93 fps, 225,9 s = 3:46 min, WhatsApp-komprimiert). Ausgabe: 1080×1920 (9:16, nativ) und 1920×1080 (16:9, Crop-Band bzw. Pillarbox-Variante), 30 fps, H.264.", "",
     f"Gesamtlänge geplant: **{sum(s['end_s']-s['start_s'] for s in plan['shots']):.1f} s** ({len(plan['shots'])} Shots, Übergänge: {'harte Schnitte' if not plan.get('xfade_s') else 'Mini-Dissolve ' + str(plan['xfade_s']) + ' s'}, 0,5 s Fade-in/0,6 s Fade-out).", "",
     "| # | Original-Timestamp | Länge | Raum | Kamera | Warum ausgewählt | KI (Higgsfield) empfohlen? | 16:9-Crop-Anker |", "|---|---|---|---|---|---|---|---|"]
for s in plan['shots']:
    L.append(f"| {s['id']} | {ts(s['start_s'])} – {ts(s['end_s'])} | {s['end_s']-s['start_s']:.1f} s | {s['room']} | {s.get('camera','')} | {s.get('why','')} | {('ja (empfohlen) – ' if s.get('ai_recommended') else 'nein – ') + s.get('ai_note','')} **Ergebnis: Original verwendet** | {s.get('crop16x9_center_pct',50)} % |")
L += ["", "## Aussortiert (Beispiele)", ""]
for r in plan.get('rejected', []): L.append(f"- {r}")
L += ["", "## Raum-Timeline des Originals (Konsens aus 3 unabhängigen Sichtungen)", "", "| von | bis | Raum / Inhalt |", "|---|---|---|"]
for t in plan.get('room_timeline', []): L.append(f"| {ts(t['start_s'])} | {ts(t['end_s'])} | {t['room']}{(' – ' + t['notes']) if t.get('notes') else ''} |")
L += ["", "## Hinweise", ""] + [f"- {n}" for n in plan.get('notes', [])]
open(out, 'w').write('\n'.join(L) + '\n'); print('wrote', out)
