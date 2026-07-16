#!/bin/bash
# F4 Build-Kette (platzsparsam): assemble -> mix (+del silent) -> overlays -> composite (+del FINAL) -> subs
cd /home/user/YOutube/produktion/folge-04
echo "=== FREE $(df -BM /home/user | tail -1 | awk '{print $4}') ==="
echo "=== ASSEMBLE ==="
python3 assemble_4k_f4.py || { echo BUILD_FEHLER_ASSEMBLE; exit 1; }
echo "=== MIX ==="
python3 mix_f4.py || { echo BUILD_FEHLER_MIX; exit 1; }
rm -f f4_video_silent_4k.mp4 work4k/slot_*.mp4   # Silent + Slots nicht mehr gebraucht
echo "=== FREE nach mix: $(df -BM /home/user | tail -1 | awk '{print $4}') ==="
echo "=== OVERLAYS ==="
python3 make_overlays_4k_f4.py || { echo BUILD_FEHLER_OVERLAYS; exit 1; }
echo "=== COMPOSITE ==="
python3 composite_4k_f4.py || { echo BUILD_FEHLER_COMPOSITE; exit 1; }
rm -f f4_FINAL_4k.mp4   # nach MASTER nicht mehr gebraucht
echo "=== FREE nach composite: $(df -BM /home/user | tail -1 | awk '{print $4}') ==="
echo "=== SUBS ==="
python3 build_subs_f4.py || { echo BUILD_FEHLER_SUBS; exit 1; }
echo "=== BUILD_ALL DONE ==="
