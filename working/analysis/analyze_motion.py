#!/usr/bin/env python3
"""Per-frame camera-motion / sharpness analysis of the source video.
Outputs metrics_frames.csv, metrics_1s.csv, metrics_half_s.csv and summary.json."""
import cv2, numpy as np, json, sys, csv, math
src, outdir = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src)
fps = cap.get(cv2.CAP_PROP_FPS)
W = 480
prev_gray = None
prev_pts = None
rows = []
i = 0
feat_params = dict(maxCorners=400, qualityLevel=0.01, minDistance=8, blockSize=7)
lk_params = dict(winSize=(21, 21), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
while True:
    ok, frame = cap.read()
    if not ok:
        break
    h, w = frame.shape[:2]
    scale = W / w
    small = cv2.resize(frame, (W, int(round(h * scale))), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    bright = float(gray.mean())
    contrast = float(gray.std())
    dx = dy = rot = sc = 0.0
    ntrack = 0
    diff = 0.0
    if prev_gray is not None:
        diff = float(cv2.absdiff(prev_gray, gray).mean())
        pts = cv2.goodFeaturesToTrack(prev_gray, mask=None, **feat_params)
        if pts is not None and len(pts) >= 12:
            nxt, st, err = cv2.calcOpticalFlowPyrLK(prev_gray, gray, pts, None, **lk_params)
            good_old = pts[st.flatten() == 1]
            good_new = nxt[st.flatten() == 1]
            ntrack = int(len(good_old))
            if ntrack >= 12:
                M, inl = cv2.estimateAffinePartial2D(good_old, good_new, method=cv2.RANSAC, ransacReprojThreshold=2.0)
                if M is not None:
                    dx, dy = float(M[0, 2]), float(M[1, 2])
                    rot = float(math.degrees(math.atan2(M[1, 0], M[0, 0])))
                    sc = float(math.hypot(M[0, 0], M[1, 0]))
                    ntrack = int(inl.sum()) if inl is not None else ntrack
        if ntrack < 12:
            (px, py), resp = cv2.phaseCorrelate(np.float32(prev_gray), np.float32(gray))
            dx, dy, sc = float(px), float(py), 1.0
    rows.append([i, round(i / fps, 3), round(dx, 3), round(dy, 3), round(rot, 4), round(sc, 4), ntrack, round(diff, 3), round(lap, 2), round(bright, 2), round(contrast, 2)])
    prev_gray = gray
    i += 1
cap.release()
hdr = ["frame", "t", "dx", "dy", "rot_deg", "scale", "ntrack", "framediff", "sharpness", "brightness", "contrast"]
with open(f"{outdir}/metrics_frames.csv", "w", newline="") as f:
    cw = csv.writer(f); cw.writerow(hdr); cw.writerows(rows)
arr = np.array([r[1:] for r in rows], dtype=float)  # t,dx,dy,rot,sc,ntrack,diff,sharp,bright,contrast
t, dx, dy, rot, sc, ntrack, diff, sharp, bright, contrast = arr.T
speed = np.hypot(dx, dy)  # px/frame at 480px width
# smooth intent motion (moving average over ~0.5 s) and jitter = residual
k = max(3, int(round(fps * 0.5)) | 1)
kern = np.ones(k) / k
dx_s = np.convolve(dx, kern, mode="same"); dy_s = np.convolve(dy, kern, mode="same")
jit = np.hypot(dx - dx_s, dy - dy_s)
def agg(win):
    out = []
    nb = int(math.ceil(t[-1] / win)) + 1
    for b in range(nb):
        m = (t >= b * win) & (t < (b + 1) * win)
        if m.sum() < 2:
            continue
        out.append({
            "start": round(b * win, 2), "end": round((b + 1) * win, 2),
            "speed_mean": round(float(speed[m].mean()), 2), "speed_max": round(float(speed[m].max()), 2),
            "jitter_mean": round(float(jit[m].mean()), 3), "jitter_p90": round(float(np.percentile(jit[m], 90)), 3),
            "rot_abs_mean": round(float(np.abs(rot[m]).mean()), 3),
            "zoom": round(float(np.prod(sc[m])), 4),  # >1 = camera moving forward / zoom in
            "sharp_mean": round(float(sharp[m].mean()), 1), "sharp_min": round(float(sharp[m].min()), 1),
            "bright": round(float(bright[m].mean()), 1), "contrast": round(float(contrast[m].mean()), 1),
            "framediff": round(float(diff[m].mean()), 2), "ntrack": int(ntrack[m].mean()),
        })
    return out
for win, name in [(1.0, "metrics_1s.csv"), (0.5, "metrics_half_s.csv")]:
    a = agg(win)
    with open(f"{outdir}/{name}", "w", newline="") as f:
        cw = csv.DictWriter(f, fieldnames=list(a[0].keys())); cw.writeheader(); cw.writerows(a)
pct = lambda x: {p: round(float(np.percentile(x, p)), 3) for p in (5, 10, 20, 25, 50, 75, 80, 90, 95)}
summary = {"fps": fps, "frames": len(rows), "duration_s": round(float(t[-1]), 2), "analysis_width_px": W,
           "percentiles": {"speed": pct(speed), "jitter": pct(jit), "sharpness": pct(sharp), "brightness": pct(bright), "framediff": pct(diff)}}
json.dump(summary, open(f"{outdir}/summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
