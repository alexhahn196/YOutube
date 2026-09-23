#!/usr/bin/env python3
"""Conservative translation-only stabilizer: phase-correlation trajectory -> Gaussian smoothing -> sub-pixel warp + fixed zoom.
Usage: stab_translate.py in.mp4 out.mp4 [sigma_frames=8] [zoom=1.04]"""
import cv2, numpy as np, sys, subprocess, os
src, dst = sys.argv[1], sys.argv[2]
sigma = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
zoom = float(sys.argv[4]) if len(sys.argv) > 4 else 1.04
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS)
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(f)
H, W = frames[0].shape[:2]
AW = 480; s = AW / W
def prep(f):
    g = cv2.cvtColor(cv2.resize(f, (AW, int(round(H * s))), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    return np.float32(cv2.GaussianBlur(g, (5, 5), 0))
win = cv2.createHanningWindow((AW, int(round(H * s))), cv2.CV_32F)
prev = prep(frames[0]); dx = [0.0]; dy = [0.0]
for f in frames[1:]:
    g = prep(f)
    (px, py), r = cv2.phaseCorrelate(prev, g, win)
    dx.append(px / s); dy.append(py / s); prev = g
dx = np.array(dx); dy = np.array(dy)
tx = np.cumsum(dx); ty = np.cumsum(dy)           # camera trajectory (full-res px)
k = int(sigma * 4) | 1
g1 = cv2.getGaussianKernel(k, sigma).flatten()
def smooth(a):
    pad = np.pad(a, (k // 2, k // 2), mode='edge')
    return np.convolve(pad, g1, mode='valid')
sx = smooth(tx); sy = smooth(ty)
cx = sx - tx; cy = sy - ty                        # correction to apply
maxshift = (zoom - 1) / 2 * np.array([W, H])
cx = np.clip(cx, -maxshift[0], maxshift[0]); cy = np.clip(cy, -maxshift[1], maxshift[1])
tmp = dst + '.tmp.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(tmp, fourcc, fps, (W, H))
for i, f in enumerate(frames):
    M = np.array([[zoom, 0, (1 - zoom) * W / 2 + cx[i]], [0, zoom, (1 - zoom) * H / 2 + cy[i]]], dtype=np.float64)
    out.write(cv2.warpAffine(f, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT))
out.release()
subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', tmp, '-c:v', 'libx264', '-preset', 'slow', '-crf', '10', '-pix_fmt', 'yuv420p', dst], check=True)
os.remove(tmp)
print(f"{dst}: frames={len(frames)} corr_px max=({np.abs(cx).max():.1f},{np.abs(cy).max():.1f}) mean=({np.abs(cx).mean():.1f},{np.abs(cy).mean():.1f})")
