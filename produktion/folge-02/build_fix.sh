#!/bin/bash
# F2 QC-Fix-Kette: assemble (NY01 statt NV05, C20-Crop-Base vorgelegt) -> mux audio -> composite -> cleanup
cd /home/user/YOutube/produktion/folge-02
echo "=== FREE $(df -BM /home/user | tail -1 | awk '{print $4}') ==="
echo "=== ASSEMBLE ==="
python3 assemble_4k_f2.py || { echo BUILD_FEHLER_ASSEMBLE; exit 1; }
rm -f work4k/slot_*.mp4
echo "=== MUX AUDIO (aus f2_FINAL.mp4) ==="
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
"$FF" -y -i f2_video_silent_4k.mp4 -i f2_FINAL.mp4 -map 0:v -map 1:a -c copy f2_FINAL_4k.mp4 || { echo BUILD_FEHLER_MUX; exit 1; }
rm -f f2_video_silent_4k.mp4
echo "=== COMPOSITE ==="
python3 composite_4k_f2.py || { echo BUILD_FEHLER_COMPOSITE; exit 1; }
rm -f f2_FINAL_4k.mp4
echo "=== FREE $(df -BM /home/user | tail -1 | awk '{print $4}') ==="
echo "=== BUILD_FIX DONE ==="
