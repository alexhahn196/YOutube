#!/usr/bin/env python3
"""Shorts-Trichter (User-Entscheid 21.07.2026): 9:16-Short aus fertigem 16:9-Master schneiden.

Center-Crop auf 9:16; Captions, SIGNAL-Watermark und 3-Sek-Endcard laufen als EINE
eingebrannte ASS-Spur (der imageio-ffmpeg-Build hat kein drawtext, aber libass).
Schaufenster-Regel gilt: Cut endet IMMER auf Cliffhanger, nie auf dem Verdict.

Nutzung:
  python3 make_short.py <master.mp4> <folge.srt> <t0> <t1> <out.mp4> [end1] [end2]
"""
import re, subprocess, sys, tempfile, os
import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()

ASS_HEAD = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,4,1,2,60,60,340,1
Style: Mark,DejaVu Sans,44,&H00D8FFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,6,0,1,3,0,8,40,40,100,1
Style: End1,DejaVu Sans,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,5,2,5,40,40,0,1
Style: End2,DejaVu Sans,54,&H00D8E035,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,4,1,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def parse_ts(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def ass_ts(t):
    cs = int(round((t - int(t)) * 100))
    t = int(t)
    return f"{t//3600}:{t%3600//60:02d}:{t%60:02d}.{cs:02d}"


def srt_events(src, t0, t1):
    events = []
    for b in open(src).read().strip().split("\n\n"):
        lines = b.strip().split("\n")
        if len(lines) < 3:
            continue
        m = re.match(r"(\S+) --> (\S+)", lines[1])
        if not m:
            continue
        a, e = parse_ts(m.group(1)), parse_ts(m.group(2))
        if e <= t0 or a >= t1:
            continue
        txt = "\\N".join(l.strip() for l in lines[2:])
        events.append((max(0, a - t0), min(t1 - t0, e - t0), txt))
    return events


def main():
    master, srt, t0, t1, out = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    end1 = sys.argv[6] if len(sys.argv) > 6 else "Signal, or noise?"
    end2 = sys.argv[7] if len(sys.argv) > 7 else "Full investigation → SIGNAL"
    precrop = int(sys.argv[8]) if len(sys.argv) > 8 else 0  # px oben+unten wegcroppen (eingebrannte Letterbox)
    seg = t1 - t0
    total = seg + 3.0

    ev = [f"Dialogue: 1,{ass_ts(0)},{ass_ts(total)},Mark,,0,0,0,,SIGNAL"]
    for a, e, txt in srt_events(srt, t0, t1):
        ev.append(f"Dialogue: 0,{ass_ts(a)},{ass_ts(e)},Caption,,0,0,0,,{txt}")
    # Endcard: dunkles Panel + zwei Zeilen, mittig
    ev.append(f"Dialogue: 2,{ass_ts(seg)},{ass_ts(total)},End1,,0,0,0,,{{\\fad(220,0)\\pos(540,880)}}{end1}")
    ev.append(f"Dialogue: 2,{ass_ts(seg)},{ass_ts(total)},End2,,0,0,0,,{{\\fad(220,0)\\pos(540,1010)}}{end2}")

    tmpdir = os.path.dirname(os.path.abspath(out)) or "."
    tmp = tempfile.NamedTemporaryFile("w", suffix=".ass", delete=False, dir=tmpdir)
    tmp.write(ASS_HEAD + "\n".join(ev) + "\n"); tmp.close()
    ass_esc = os.path.basename(tmp.name)  # relativer Pfad, im cwd des Aufrufs unten

    pre = f"crop=iw:ih-{2*precrop}:0:{precrop}," if precrop else ""
    vf = (f"{pre}crop=ih*9/16:ih:(iw-ow)/2:0,scale=1080:1920,setsar=1,"
          f"tpad=stop_mode=clone:stop_duration=3,ass={ass_esc}")
    cmd = [FF, "-y", "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", os.path.abspath(master),
           "-vf", vf, "-af", f"apad=pad_dur=3,afade=t=out:st={total-0.6:.2f}:d=0.6",
           "-t", f"{total:.3f}", "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
           os.path.abspath(out)]
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=tmpdir)
    os.unlink(tmp.name)
    if r.returncode:
        print(r.stderr[-1200:]); sys.exit(1)
    print(f"OK {out} ({total:.1f}s)")


if __name__ == "__main__":
    main()
