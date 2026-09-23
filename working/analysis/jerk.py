import cv2, numpy as np, sys
def trace(path):
    cap=cv2.VideoCapture(path); prev=None; dxs=[]; dys=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        g=cv2.cvtColor(cv2.resize(f,(480,int(f.shape[0]*480/f.shape[1])),interpolation=cv2.INTER_AREA),cv2.COLOR_BGR2GRAY)
        g=cv2.GaussianBlur(g,(5,5),0)
        if prev is not None:
            (dx,dy),r=cv2.phaseCorrelate(np.float32(prev),np.float32(g),cv2.createHanningWindow((g.shape[1],g.shape[0]),cv2.CV_32F))
            dxs.append(dx); dys.append(dy)
        prev=g
    dx=np.array(dxs); dy=np.array(dys)
    jerk=np.hypot(np.diff(dx),np.diff(dy))
    k=15; kern=np.ones(k)/k
    jit=np.hypot(dx-np.convolve(dx,kern,'same'), dy-np.convolve(dy,kern,'same'))
    return jerk.mean(), np.percentile(jerk,90), jit.mean(), np.hypot(dx,dy).mean()
for p in sys.argv[1:]:
    j,j90,jit,sp=trace(p)
    print(f"{p:45s} jerk_mean={j:.3f} jerk_p90={j90:.3f} jitter={jit:.3f} speed={sp:.2f}")
