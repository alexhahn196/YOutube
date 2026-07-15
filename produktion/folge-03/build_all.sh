#!/bin/bash
cd /home/user/YOutube/produktion/folge-03
set -e
echo "=== [1/3] ASSEMBLE 4K ===" 
python3 assemble_4k_f3.py
echo "=== [2/3] MIX ==="
python3 mix_f3.py
rm -f f3_video_silent_4k.mp4
echo "=== [3/3] COMPOSITE 4K ==="
python3 composite_4k_f3.py
echo "=== CHAIN DONE ==="
