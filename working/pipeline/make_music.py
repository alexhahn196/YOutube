#!/usr/bin/env python3
"""Procedural, royalty-free ambient piano bed (numpy only). Usage: make_music.py out.wav [duration_s=30] [seed=7]"""
import numpy as np, sys, wave, struct
out = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0; SEED = int(sys.argv[3]) if len(sys.argv) > 3 else 7
SR = 48000; rng = np.random.default_rng(SEED)
N = int(DUR * SR); t = np.arange(N) / SR
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)
# progression (8 bars, 3.75 s each): Dmaj7 - A/C# - Bm7 - Gmaj7  x2  (warm, elegant)
BAR = 3.75
chords = [[62, 66, 69, 73], [61, 64, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66]] * 2
def env(n, a, r):
    e = np.ones(n); A = int(a * SR); R = int(r * SR)
    e[:A] = np.linspace(0, 1, A) ** 2; e[-R:] *= np.linspace(1, 0, R) ** 1.5; return e
def pad_note(f, n):
    x = np.zeros(n); tt = np.arange(n) / SR
    for det, g in ((-0.15, 0.5), (0.0, 1.0), (0.18, 0.5)):
        fr = f * 2 ** (det / 100)
        x += g * (np.sin(2 * np.pi * fr * tt) + 0.25 * np.sin(2 * np.pi * 2 * fr * tt) + 0.08 * np.sin(2 * np.pi * 3 * fr * tt))
    x *= 1 + 0.03 * np.sin(2 * np.pi * 0.2 * tt + rng.uniform(0, 6.28))  # slow shimmer
    return x / 3
def piano_note(f, n, vel):
    tt = np.arange(n) / SR; x = np.zeros(n)
    for k, g, d in ((1, 1.0, 1.6), (2, 0.45, 1.0), (3, 0.22, 0.7), (4, 0.10, 0.5), (5, 0.05, 0.35)):
        fk = f * k * (1 + 0.0004 * k * k)  # slight inharmonicity
        x += g * np.sin(2 * np.pi * fk * tt) * np.exp(-tt / d)
    x *= (1 - np.exp(-tt * 400))  # fast attack
    return vel * x / 1.8
L = np.zeros(N); R = np.zeros(N)
# --- pad + sub bass ---
for i, ch in enumerate(chords):
    s = int(i * BAR * SR); e = min(N, int((i + 1) * BAR * SR) + int(1.2 * SR)); n = e - s
    seg = np.zeros(n)
    for m in ch: seg += pad_note(midi(m), n)
    seg += 0.9 * np.sin(2 * np.pi * midi(ch[0] - 12) * np.arange(n) / SR) * 0.6  # sub root
    seg *= env(n, 1.2, 1.2) * 0.16
    pan = 0.5 + 0.08 * np.sin(i)
    L[s:e] += seg * (1 - pan) * 1.2; R[s:e] += seg * pan * 1.2
# --- sparse piano arpeggio, gentle rhythm on chord tones an octave up ---
pattern = [0.0, 1.5, 2.25, 3.0]  # beats-ish offsets inside a bar (seconds)
for i, ch in enumerate(chords):
    tones = [m + 12 for m in ch] + [ch[0] + 24]
    for j, off in enumerate(pattern):
        if rng.random() < 0.82:
            m = tones[(i + j * 2) % len(tones)]
            s = max(0, int((i * BAR + off + rng.uniform(-0.02, 0.02)) * SR)); n = min(N - s, int(3.5 * SR))
            if n <= 0: continue
            vel = 0.55 + 0.25 * rng.random() - (0.15 if j else 0)
            note = piano_note(midi(m), n, vel) * 0.22
            pan = 0.35 + 0.3 * (m - 60) / 30
            L[s:s + n] += note * (1 - pan); R[s:s + n] += note * pan
# --- reverb: synthetic stereo IR (exp-decaying noise, low-passed) via FFT convolution ---
def ir(seed, T=2.8):
    r = np.random.default_rng(seed); n = int(T * SR); tt = np.arange(n) / SR
    x = r.standard_normal(n) * np.exp(-tt / (T / 4.5)); x[:int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
    k = np.exp(-np.arange(0, 200) / 40.0); x = np.convolve(x, k / k.sum(), mode='same')  # darken tail
    return x / np.abs(x).sum() * 6
def conv(x, h):
    n = len(x) + len(h) - 1; nf = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, nf) * np.fft.rfft(h, nf), nf)[:len(x)]
wetL = conv(L, ir(11)); wetR = conv(R, ir(12))
L = 0.72 * L + 0.42 * wetL; R = 0.72 * R + 0.42 * wetR
# --- gentle low-pass (one-pole) + master fades matching the video (0.5 s in, ends with the 0.6 s fade-out) ---
def lp(x, fc=6500):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    # vectorised one-pole via lfilter-free recurrence in chunks (numpy trick using cumulative product is unstable; use loop over blocks)
    b = 1 - a; out = np.empty_like(x); prev = 0.0
    for i in range(0, len(x), 4096):
        blk = x[i:i + 4096]; res = np.empty_like(blk)
        for j in range(len(blk)):
            prev = b * blk[j] + a * prev; res[j] = prev
        out[i:i + 4096] = res
    return out
L = lp(L); R = lp(R)
fade = np.ones(N); fi = int(1.5 * SR); fo = int(3.2 * SR)
fade[:fi] = np.linspace(0, 1, fi) ** 1.5; fade[-fo:] *= np.linspace(1, 0, fo) ** 1.2
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max()); L /= peak / 0.5; R /= peak / 0.5
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    inter = np.empty(2 * N, dtype=np.int16); inter[0::2] = (L * 32767).astype(np.int16); inter[1::2] = (R * 32767).astype(np.int16)
    w.writeframes(inter.tobytes())
print('wrote', out, f'{DUR}s')
