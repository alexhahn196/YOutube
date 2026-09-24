#!/usr/bin/env python3
"""Quantitative structure check: per-frame edge-IoU and SSIM between source clip and AI clip (time-aligned).
Usage: qc_metrics.py source.mp4 ai.mp4"""
import cv2, numpy as np, sys
def frames_at(path, times, W=360):
    cap=cv2.VideoCapture(path); out=[]
    for t in times:
        cap.set(cv2.CAP_PROP_POS_MSEC, t*1000); ok,f=cap.read()
        if not ok: out.append(None); continue
        h=int(f.shape[0]*W/f.shape[1]); g=cv2.cvtColor(cv2.resize(f,(W,h),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY); out.append(g)
    return out
def ssim(a,b):
    a=a.astype(np.float64); b=b.astype(np.float64); C1=(0.01*255)**2; C2=(0.03*255)**2
    mu_a=cv2.GaussianBlur(a,(11,11),1.5); mu_b=cv2.GaussianBlur(b,(11,11),1.5)
    sa=cv2.GaussianBlur(a*a,(11,11),1.5)-mu_a**2; sb=cv2.GaussianBlur(b*b,(11,11),1.5)-mu_b**2; sab=cv2.GaussianBlur(a*b,(11,11),1.5)-mu_a*mu_b
    return float((((2*mu_a*mu_b+C1)*(2*sab+C2))/((mu_a**2+mu_b**2+C1)*(sa+sb+C2))).mean())
def edge_iou(a,b):
    ea=cv2.Canny(cv2.GaussianBlur(a,(3,3),0),60,140)>0; eb=cv2.Canny(cv2.GaussianBlur(b,(3,3),0),60,140)>0
    ea=cv2.dilate(ea.astype(np.uint8),np.ones((5,5),np.uint8))>0; eb=cv2.dilate(eb.astype(np.uint8),np.ones((5,5),np.uint8))>0
    return float((ea&eb).sum()/max(1,(ea|eb).sum()))
src,ai=sys.argv[1],sys.argv[2]
import subprocess
d=min(float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',p]).decode()) for p in (src,ai))
times=[i*0.25 for i in range(int(d/0.25))]
A=frames_at(src,times); B=frames_at(ai,times)
rows=[]
for t,a,b in zip(times,A,B):
    if a is None or b is None: continue
    if a.shape!=b.shape: b=cv2.resize(b,(a.shape[1],a.shape[0]))
    # allow small global shift: align by phase correlation
    (dx,dy),_=cv2.phaseCorrelate(np.float32(a),np.float32(b)); M=np.float32([[1,0,-dx],[0,1,-dy]]); b2=cv2.warpAffine(b,M,(a.shape[1],a.shape[0]))
    rows.append((t,ssim(a,b2),edge_iou(a,b2),dx,dy))
s=np.array([r[1] for r in rows]); e=np.array([r[2] for r in rows])
print(f"frames={len(rows)}  SSIM mean={s.mean():.3f} min={s.min():.3f}  edgeIoU mean={e.mean():.3f} min={e.min():.3f}")
for t,ss,ei,dx,dy in rows: print(f"t={t:5.2f}s ssim={ss:.3f} edgeIoU={ei:.3f} shift=({dx:+.1f},{dy:+.1f})" + ("  <-- LOW" if ss<s.mean()-0.08 or ei<e.mean()-0.15 else ""))
