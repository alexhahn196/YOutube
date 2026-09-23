#!/usr/bin/env python3
"""Build the real-estate walkthrough from a plan JSON.
Steps: accurate cut of original clips -> (optional) translation-only stabilization -> grade + lanczos upscale to 1080x1920@30
       -> assemble 9:16 master -> 16:9 crop variant (per-shot anchor) and 16:9 pillarbox variant.
AI clips (Higgsfield) can replace the enhanced 9:16 clip per shot via plan.shots[i].ai_clip (only if approved by QC).
Usage: build_walkthrough.py plan.json [--stage cut|enhance|assemble|all]"""
import json, subprocess, sys, os, shutil, math, csv
plan = json.load(open(sys.argv[1]))
stage = sys.argv[sys.argv.index('--stage') + 1] if '--stage' in sys.argv else 'all'
SRC = plan['source']
ROOT = plan.get('root', '.')
ORIG = os.path.join(ROOT, 'working/original_clips'); ENH = os.path.join(ROOT, 'working/enhanced'); OUT = os.path.join(ROOT, 'output')
for d in (ORIG, ENH, OUT): os.makedirs(d, exist_ok=True)
XF = plan.get('xfade_s', 0.2)
GRADE = plan.get('grade', "hqdn3d=1.5:1.0:3:2.5,eq=contrast=1.04:brightness=0.01:saturation=1.08")
SHARP = plan.get('sharpen', "unsharp=5:5:0.4:5:5:0.0")
def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(' '.join(cmd)); print(r.stderr[-2000:]); sys.exit(1)
def ff(*args): run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *args])
def dur(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path]).decode().strip())
shots = plan['shots']
# ---------- cut ----------
if stage in ('cut', 'all'):
    for s in shots:
        s['orig'] = os.path.join(ORIG, f"{s['id']}_{s['name']}.mp4")
        ff('-ss', str(s['start_s']), '-to', str(s['end_s']), '-i', SRC, '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', '10', '-pix_fmt', 'yuv420p', s['orig'])
        print('cut', s['orig'], f"{dur(s['orig']):.2f}s")
# ---------- enhance ----------
if stage in ('enhance', 'all'):
    for s in shots:
        s['orig'] = os.path.join(ORIG, f"{s['id']}_{s['name']}.mp4")
        base = s['orig']
        if s.get('stabilize', True):
            stab = os.path.join(ENH, f"{s['id']}_{s['name']}_stab.mp4")
            run(['python3', os.path.join(ROOT, 'working/analysis/stab_translate.py'), base, stab, str(s.get('stab_sigma', 8)), str(s.get('stab_zoom', 1.04))])
            base = stab
        s['enh'] = os.path.join(ENH, f"{s['id']}_{s['name']}_9x16.mp4")
        ff('-i', base, '-vf', f"{GRADE},scale=1080:1920:flags=lanczos,{SHARP},fps=30", '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', s['enh'])
        print('enhanced', s['enh'])
# ---------- assemble ----------
def assemble(clips, out, w, h):
    """xfade chain with XF seconds dissolve; fade from/to black; silent stereo track."""
    n = len(clips); durs = [dur(c) for c in clips]
    inputs = []; [inputs.extend(['-i', c]) for c in clips]
    fc = []
    for i in range(n):
        fc.append(f"[{i}:v]scale={w}:{h}:flags=lanczos,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v{i}]")
    if n == 1:
        last = 'v0'; total = durs[0]
    elif XF <= 0:
        fc.append(''.join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[vx]")
        last = 'vx'; total = sum(durs)
    else:
        prev = 'v0'; offset = 0.0
        for i in range(1, n):
            offset += durs[i - 1] - XF
            tag = f"x{i}" if i < n - 1 else 'vx'
            fc.append(f"[{prev}][v{i}]xfade=transition=fade:duration={XF}:offset={offset:.3f}[{tag}]")
            prev = tag
        last = 'vx'; total = offset + durs[-1]
    fc.append(f"[{last}]fade=t=in:st=0:d=0.5,fade=t=out:st={total - 0.6:.3f}:d=0.6[vout]")
    ff(*inputs, '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=48000', '-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', f'{n}:a', '-shortest',
       '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-level', '4.1', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', out)
    return total
if stage in ('assemble', 'all'):
    for s in shots:
        s['enh'] = os.path.join(ENH, f"{s['id']}_{s['name']}_9x16.mp4")
        s['final_src'] = s.get('ai_clip') or s['enh']
    # 9:16 master
    m916 = os.path.join(OUT, plan.get('out_9x16', 'property_walkthrough_vertical_9x16.mp4'))
    t = assemble([s['final_src'] for s in shots], m916, 1080, 1920)
    print('9:16 master', m916, f"{t:.2f}s")
    # 16:9 crop variant: per-shot vertical anchor
    crops = []
    for s in shots:
        c = os.path.join(ENH, f"{s['id']}_{s['name']}_16x9crop.mp4")
        pct = float(s.get('crop16x9_center_pct', 50)) / 100.0
        ff('-i', s['final_src'], '-vf', f"scale=1080:1920:flags=lanczos,crop=1080:608:0:'clip((1920-608)*{pct:.3f},0,1920-608)',scale=1920:1080:flags=lanczos,unsharp=5:5:0.3:5:5:0.0", '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-pix_fmt', 'yuv420p', c)
        crops.append(c)
    m169 = os.path.join(OUT, plan.get('out_16x9', 'property_walkthrough_16x9.mp4'))
    t = assemble(crops, m169, 1920, 1080)
    print('16:9 crop master', m169, f"{t:.2f}s")
    # 16:9 pillarbox alternative from the 9:16 master
    p169 = os.path.join(OUT, plan.get('out_16x9_pillar', 'property_walkthrough_16x9_pillarbox.mp4'))
    ff('-i', m916, '-filter_complex', "[0:v]split=2[bg][fg];[bg]scale=1920:1080:flags=bicubic,gblur=sigma=45,eq=brightness=-0.28:saturation=0.55[bgb];[fg]scale=-2:1080:flags=lanczos[fgs];[bgb][fgs]overlay=(W-w)/2:0,format=yuv420p[v]",
       '-map', '[v]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'copy', '-movflags', '+faststart', p169)
    print('16:9 pillarbox', p169)
json.dump(plan, open(sys.argv[1].replace('.json', '.resolved.json'), 'w'), indent=1, ensure_ascii=False)
