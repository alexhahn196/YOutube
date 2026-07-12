#!/usr/bin/env python3
"""SIGNAL Ep01 FINAL: re-time visuals to the 12-min VO (boomerang-loop fill),
add title cards, mix VO + 3 music beds (low, faded), mux. Output: signal_ep01_FINAL.mp4"""
import json, os, re, subprocess, math
import imageio_ffmpeg
FF = imageio_ffmpeg.get_ffmpeg_exe()
HERE = os.path.dirname(os.path.abspath(__file__))
CLIPS = os.path.join(HERE, "clips")
WORK = os.path.join(HERE, "final_work"); os.makedirs(WORK, exist_ok=True)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
W, H, FPS = 1920, 1080, 30
TC = 3.0                    # title card seconds
SLOW = 1.5                  # boomerang slowdown (calmer motion)

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FFMPEG ERR:\n", " ".join(cmd)[:300], "\n", r.stderr[-2000:]); raise SystemExit(1)
    return r

def dur(p):
    o = subprocess.run([FF, "-i", p], capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", o)
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3)) if m else 0.0

# ---------- title card ----------
def make_title(name, big, small):
    from PIL import Image, ImageDraw, ImageFont
    png = os.path.join(WORK, name + ".png"); out = os.path.join(WORK, name + ".mp4")
    img = Image.new("RGB", (W, H), (5, 7, 13)); d = ImageDraw.Draw(img)
    fb = ImageFont.truetype(FONT, 116); fs = ImageFont.truetype(FONT, 42)
    bb = d.textbbox((0, 0), big, font=fb)
    d.text(((W-(bb[2]-bb[0]))/2 - bb[0], H/2 - 150 - bb[1]), big, font=fb, fill=(34, 211, 238))
    d.rectangle([(W-560)//2, H//2-18, (W+560)//2, H//2-15], fill=(34, 211, 238))
    sb = d.textbbox((0, 0), small, font=fs)
    d.text(((W-(sb[2]-sb[0]))/2 - sb[0], H/2 + 20 - sb[1]), small, font=fs, fill=(208, 238, 245))
    img.save(png)
    run([FF, "-y", "-loop", "1", "-i", png, "-t", f"{TC}", "-r", str(FPS),
         "-vf", f"scale={W}:{H},setsar=1,fps={FPS},format=yuv420p,"
                f"fade=t=in:st=0:d=0.4,fade=t=out:st={TC-0.4:.2f}:d=0.4",
         "-fps_mode", "cfr", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
         "-pix_fmt", "yuv420p", out])
    return out

# ---------- boomerang base per clip ----------
def boomerang_base(cid):
    src = os.path.join(CLIPS, cid + ".mp4"); base = os.path.join(WORK, f"base_{cid}.mp4")
    if os.path.exists(base): return base
    fc = (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
          f"setsar=1,fps={FPS},format=yuv420p,setpts=PTS-STARTPTS[f];"
          f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,"
          f"setsar=1,fps={FPS},format=yuv420p,reverse,setpts=PTS-STARTPTS[r];"
          f"[f][r]concat=n=2:v=1:a=0,setpts={SLOW}*PTS[bm]")
    run([FF, "-y", "-i", src, "-filter_complex", fc, "-map", "[bm]", "-an",
         "-r", str(FPS), "-fps_mode", "cfr", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-pix_fmt", "yuv420p", base])
    return base

def fill_clip(cid, target, idx):
    base = boomerang_base(cid); bdur = dur(base)
    loops = max(1, math.ceil(target / bdur))
    out = os.path.join(WORK, f"slot_{idx:02d}_{cid}.mp4")
    run([FF, "-y", "-stream_loop", str(loops), "-i", base, "-t", f"{target:.3f}",
         "-r", str(FPS), "-fps_mode", "cfr", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-pix_fmt", "yuv420p", out])
    return out

# ---------- plan ----------
vo = [os.path.join(HERE, f"vo_seg{i}.mp3") for i in range(5)]
D = [dur(p) for p in vo]
LEAD, GAP, TAIL = 0.4, 0.5, 0.4
vslot = [LEAD+D[0]+GAP, D[1]+GAP, D[2]+GAP, D[3]+GAP, D[4]+TAIL]
print("VO durs:", [round(x,1) for x in D], "total", round(sum(D),1))
print("vslots:", [round(x,1) for x in vslot], "total", round(sum(vslot),1))

SEG_CLIPS = [
    ("SIGNAL", "signal or noise - you decide", ["C01", "C02", "C03"]),
    ("THE CLAIM", "what the internet said", ["C04", "C05", "C06", "C07"]),
    ("THE EVIDENCE", "what the telescopes measured", ["C09","C10","C11","C12","C13","C14","C16","C17"]),
    ("THE VERDICT", "leans noise - most likely natural", ["C19", "C20"]),
]
# build ordered video slot list: title + clips per segment, last segment = outro clip + end title
order = []  # (kind, payload, target)
idx = 0
for si in range(4):
    big, small, cids = SEG_CLIPS[si]
    t_title = TC
    per = (vslot[si] - t_title) / len(cids)
    order.append(("title", (f"title_{si}", big, small), t_title))
    for c in cids:
        order.append(("clip", c, per));
# outro: C21 then end title
order.append(("clip", "C21", vslot[4] - TC))
order.append(("title", ("title_end", "SIGNAL", "which object should we investigate next?"), TC))

# ---------- build video slots ----------
vid_files = []
for i, (kind, payload, target) in enumerate(order):
    if kind == "title":
        name, big, small = payload
        f = make_title(name, big, small)
    else:
        f = fill_clip(payload, target, i)
    vid_files.append(f)
    print(f"slot {i}: {kind} {payload if kind=='clip' else payload[1]} -> {target:.1f}s")

# concat video (demuxer copy; same codec params)
listf = os.path.join(WORK, "vlist.txt")
open(listf, "w").write("".join(f"file '{p}'\n" for p in vid_files))
silent = os.path.join(WORK, "video_silent.mp4")
run([FF, "-y", "-f", "concat", "-safe", "0", "-i", listf, "-c", "copy", silent])
print("video_silent:", round(dur(silent), 1), "s")

# ---------- audio ----------
# VO_full: sil, seg0, sil, seg1, ... seg4, sil  (concat filter, force 44100 stereo)
ins = []
def sil(d): return f"anullsrc=r=44100:cl=stereo:d={d}"
parts = []
# We'll pass VO files as inputs and build silence via lavfi in filter graph.
acmd = [FF, "-y"]
for p in vo: acmd += ["-i", p]
fa = []
segn = len(vo)
# create silence + seg chain
lead = f"aevalsrc=0:d={LEAD}:s=44100:c=stereo[sL]"
# simpler: use anullsrc via lavfi inputs
# Build with concat: [sil0][a0][silg][a1]...[a4][silT]
# generate silence sources inside filter
sils = []
fa.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{LEAD},asetpts=PTS-STARTPTS[s0]")
for i in range(segn):
    fa.append(f"[{i}:a]aformat=sample_rates=44100:channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
# gaps
for g in range(segn):  # gap after each seg (last is TAIL)
    gd = TAIL if g == segn-1 else GAP
    fa.append(f"anullsrc=r=44100:cl=stereo,atrim=0:{gd},asetpts=PTS-STARTPTS[g{g}]")
seq = "[s0][a0]" + "".join(f"[g{i-1}][a{i}]" if i>0 else "" for i in range(1,segn))
# build explicit order: s0 a0 g0 a1 g1 a2 g2 a3 g3 a4 g4
concat_labels = "[s0][a0]"
for i in range(1, segn):
    concat_labels += f"[g{i-1}][a{i}]"
concat_labels += f"[g{segn-1}]"
ncat = 2 + (segn-1)*2 + 1  # s0,a0 + (g,a)*4 + gTail
fa.append(f"{concat_labels}concat=n={ncat}:v=0:a=1[vofull]")
vo_full = os.path.join(WORK, "vo_full.wav")
run(acmd + ["-filter_complex", ";".join(fa), "-map", "[vofull]", vo_full])
print("vo_full:", round(dur(vo_full), 1), "s")

# MUSIC full: A(->vslot0+1) B(->vslot2) C(->vslot3+4) with fades, concat
mA_t = vslot[0] + vslot[1]; mB_t = vslot[2]; mC_t = vslot[3] + vslot[4]
mcmd = [FF, "-y", "-i", "musicA.mp3", "-i", "musicB.mp3", "-i", "musicC.mp3"]
mf = [
 f"[0:a]atrim=0:{mA_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=2,afade=t=out:st={mA_t-1.5:.2f}:d=1.5,aformat=sample_rates=44100:channel_layouts=stereo[mA]",
 f"[1:a]atrim=0:{mB_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.5,afade=t=out:st={mB_t-1.5:.2f}:d=1.5,aformat=sample_rates=44100:channel_layouts=stereo[mB]",
 f"[2:a]atrim=0:{mC_t},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=1.5,afade=t=out:st={mC_t-3:.2f}:d=3,aformat=sample_rates=44100:channel_layouts=stereo[mC]",
 "[mA][mB][mC]concat=n=3:v=0:a=1[mus]",
]
mus_full = os.path.join(WORK, "music_full.wav")
run(mcmd + ["-filter_complex", ";".join(mf), "-map", "[mus]", mus_full])
print("music_full:", round(dur(mus_full), 1), "s")

# MIX: VO full + music low, then mux with video (copy)
final = os.path.join(HERE, "signal_ep01_FINAL.mp4")
run([FF, "-y", "-i", silent, "-i", vo_full, "-i", mus_full,
     "-filter_complex",
     # Sidechain ducking: music dips under the voice, rises in pauses (pro doc/podcast standard)
     "[1:a]asplit=2[vomix][vosc];[2:a]volume=0.32[mus0];"
     "[mus0][vosc]sidechaincompress=threshold=0.05:ratio=8:attack=15:release=400[musd];"
     "[vomix][musd]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]",
     "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
     "-movflags", "+faststart", "-shortest", final])
print("FINAL:", final, "|", round(dur(final), 1), "s")
