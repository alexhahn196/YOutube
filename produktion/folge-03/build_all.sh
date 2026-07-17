#!/bin/bash
# F3 Build-Kette (QC-Fix-Re-Render, platzsparsam nach F4-Lesson)
cd /home/user/YOutube/produktion/folge-03
set -e
echo "=== FREE $(df -BM /home/user | tail -1 | awk '{print $4}') ==="
echo "=== [1/3] ASSEMBLE 4K ==="
python3 assemble_4k_f3.py
rm -f work4k/slot_*.mp4
echo "=== [2/3] MIX ==="
python3 mix_f3.py
rm -f f3_video_silent_4k.mp4 work4k/*.wav
echo "=== [3/3] COMPOSITE 4K ==="
python3 composite_4k_f3.py
rm -f f3_FINAL_4k.mp4
echo "=== FREE $(df -BM /home/user | tail -1 | awk '{print $4}') ==="
echo "=== CHAIN DONE ==="
