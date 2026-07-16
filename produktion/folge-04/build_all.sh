#!/bin/bash
# F4 Build-Kette: wartet auf warmup, dann assemble -> mix -> overlays -> composite -> subs
cd /home/user/YOutube/produktion/folge-04
# auf Warmup warten (max 30 min)
for i in $(seq 1 180); do
  if grep -q "WARMUP DONE" warmup.log 2>/dev/null; then break; fi
  sleep 10
done
echo "=== ASSEMBLE ==="
python3 assemble_4k_f4.py || exit 1
echo "=== MIX ==="
python3 mix_f4.py || exit 1
echo "=== OVERLAYS ==="
python3 make_overlays_4k_f4.py || exit 1
echo "=== COMPOSITE ==="
python3 composite_4k_f4.py || exit 1
echo "=== SUBS ==="
python3 build_subs_f4.py || exit 1
echo "=== BUILD_ALL DONE ==="
