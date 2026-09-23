#!/usr/bin/env python3
"""Build side-by-side QC sheets: source clip (left) vs AI clip (right) at N evenly spaced time points.
Usage: qc_compare.py source.mp4 ai.mp4 out_prefix [n=5]  -> out_prefix_k.jpg (one per time point) and out_prefix_all.jpg"""
import subprocess, sys, os
src, ai, out = sys.argv[1], sys.argv[2], sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 5
def dur(p): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]).decode().strip())
ds, da = dur(src), dur(ai)
d = min(ds, da)
pts = [d * (i + 0.5) / n for i in range(n)]
files = []
for k, t in enumerate(pts):
    f = f"{out}_{k+1}.jpg"
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',f"{t:.3f}",'-i',src,'-ss',f"{t:.3f}",'-i',ai,
        '-filter_complex', f"[0:v]scale=-2:960:flags=lanczos,drawtext=text='ORIGINAL t={t:.2f}s':x=10:y=10:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6[a];[1:v]scale=-2:960:flags=lanczos,drawtext=text='AI t={t:.2f}s':x=10:y=10:fontsize=26:fontcolor=white:box=1:boxcolor=black@0.6[b];[a][b]hstack",
        '-frames:v','1','-q:v','3',f], check=True)
    files.append(f)
# one overview: all pairs stacked vertically (scaled down)
inputs = []; [inputs.extend(['-i', f]) for f in files]
fc = ''.join(f"[{i}:v]scale=-2:480[s{i}];" for i in range(n)) + ''.join(f"[s{i}]" for i in range(n)) + f"vstack=inputs={n}"
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',*inputs,'-filter_complex',fc,'-frames:v','1','-q:v','4',f"{out}_all.jpg"], check=True)
print('\n'.join(files + [f"{out}_all.jpg"]))
