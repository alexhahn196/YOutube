#!/usr/bin/env python3
"""
Stilmessung — misst den Bildstil von Videomaterial maschinell und vergleicht
Kandidatenbilder dagegen.

Gebaut für die Storikon-Stilspezifikation (bewertungen/storikon-stilspezifikation.md),
aber allgemein verwendbar — auch für die eigenen SIGNAL-Master.

Unterbefehle:
  inventar   <videos...>                  A0  ffprobe-Bestandsaufnahme
  schnitte   <video> [--schwelle 27]      A1  PySceneDetect ContentDetector
  frames     <video> --out DIR            A2  mittleren Frame je Shot ziehen
  messen     <frame-dir> --out JSON       A3  sechs Stilgrößen, Median + Spanne
  bewegung   <video> --out JSON           A4  ORB-Homographie + optischer Fluss
  reuse      <frame-dir> --out JSON       A5  pHash-Dubletten + Ausschnitt-Erkennung
  vergleich  <kand-dir> --ref JSON        C2  Abweichung Kandidat zu Referenz

Alle Unterbefehle schreiben JSON und drucken eine Kurzfassung.
"""
import argparse, json, os, subprocess, sys, glob, itertools
import numpy as np
import cv2


# ---------------------------------------------------------------- A0 Inventar
def ffprobe(pfad):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", pfad],
        capture_output=True, text=True)
    if r.returncode != 0:
        return {"datei": pfad, "fehler": r.stderr.strip()[:300]}
    d = json.loads(r.stdout)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    if v is None:
        return {"datei": pfad, "fehler": "kein Videostream"}
    w, h = int(v["width"]), int(v["height"])
    num, den = (v.get("r_frame_rate", "0/1").split("/") + ["1"])[:2]
    fps = float(num) / float(den) if float(den) else 0.0
    dauer = float(d["format"].get("duration", 0.0))
    # Seitenverhaeltnis auf gaenginge Formate runden
    ar = w / h if h else 0
    if abs(ar - 16/9) < 0.05:   form, label = "16:9", "Langform"
    elif abs(ar - 9/16) < 0.05: form, label = "9:16", "Short"
    elif abs(ar - 1.0) < 0.05:  form, label = "1:1", "quadratisch"
    else:                       form, label = f"{ar:.3f}:1", "sonstiges"
    return {"datei": os.path.basename(pfad), "pfad": pfad,
            "dauer_s": round(dauer, 2), "breite": w, "hoehe": h,
            "seitenverhaeltnis": form, "einordnung": label,
            "fps": round(fps, 3), "codec": v.get("codec_name"),
            "groesse_mb": round(os.path.getsize(pfad) / 1e6, 1)}


# ---------------------------------------------------------------- A1 Schnitte
def schnitte(video, schwelle=27.0):
    from scenedetect import open_video, SceneManager
    from scenedetect.detectors import ContentDetector
    vid = open_video(video)
    sm = SceneManager()
    sm.add_detector(ContentDetector(threshold=schwelle))
    sm.detect_scenes(vid, show_progress=False)
    liste = sm.get_scene_list()
    shots = [{"nr": i + 1,
              "start_s": round(a.get_seconds(), 3),
              "ende_s": round(b.get_seconds(), 3),
              "dauer_s": round(b.get_seconds() - a.get_seconds(), 3)}
             for i, (a, b) in enumerate(liste)]
    return shots


def histogramm(dauern):
    h = {}
    for d in dauern:
        k = int(d)
        h[k] = h.get(k, 0) + 1
    return {f"{k}-{k+1}s": h[k] for k in sorted(h)}


# ---------------------------------------------------------------- A2 Frames
def mittelframes(video, shots, out_dir):
    """Mittleren Frame je Shot — nicht den ersten, dort sitzt Bewegungsunschaerfe."""
    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    raus = []
    for s in shots:
        mitte = (s["start_s"] + s["ende_s"]) / 2.0
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(mitte * fps))
        ok, img = cap.read()
        if not ok:
            continue
        p = os.path.join(out_dir, "shot_%04d.png" % s["nr"])
        cv2.imwrite(p, img)
        raus.append(p)
    cap.release()
    return raus


def randframes(video, shots, out_dir):
    """Ersten und letzten Frame je Shot — Grundlage fuer A4."""
    os.makedirs(out_dir, exist_ok=True)
    cap = cv2.VideoCapture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    paare = []
    for s in shots:
        got = {}
        for tag, t in (("a", s["start_s"] + 0.15), ("b", s["ende_s"] - 0.15)):
            if t <= 0 or t <= s["start_s"]:
                t = s["start_s"] + 0.05
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
            ok, img = cap.read()
            if ok:
                p = os.path.join(out_dir, "shot_%04d_%s.png" % (s["nr"], tag))
                cv2.imwrite(p, img)
                got[tag] = p
        if len(got) == 2:
            paare.append((s["nr"], got["a"], got["b"]))
    cap.release()
    return paare


# ---------------------------------------------------------------- A3 Messen
def messe_frame(pfad, k=6, maske=None, normpx=None):
    """maske = (y1, y2): Zeilenband wird ENTFERNT, nicht geschwaerzt.
    Gebraucht fuer eingebrannte Untertitel — Schwaerzen wuerde kuenstliche
    Schwarzpixel in Palette und Helligkeitsstatistik einschleusen.

    normpx = Zielpixelzahl (z.B. 2_000_000): Bild wird unter Wahrung des
    Seitenverhaeltnisses darauf skaliert. ZWINGEND, sobald Bilder
    unterschiedlicher Groesse verglichen werden — Laplace-Varianz und
    Kantendichte haengen direkt an der Aufloesung."""
    bgr = cv2.imread(pfad)
    if bgr is None:
        return None
    if maske:
        y1, y2 = maske
        y1, y2 = max(0, y1), min(bgr.shape[0], y2)
        if y2 > y1:
            bgr = np.delete(bgr, np.s_[y1:y2], axis=0)
    if normpx:
        h0, w0 = bgr.shape[:2]
        f = (normpx / (w0 * h0)) ** 0.5
        bgr = cv2.resize(bgr, (max(1, int(w0 * f)), max(1, int(h0 * f))),
                         interpolation=cv2.INTER_AREA if f < 1 else cv2.INTER_CUBIC)
    # fuer k-means und Statistik verkleinern, Kantenmasse auf normierter Groesse
    klein = cv2.resize(bgr, (320, int(320 * bgr.shape[0] / bgr.shape[1]))) if bgr.shape[1] > 320 else bgr
    hsv = cv2.cvtColor(klein, cv2.COLOR_BGR2HSV)
    grau_o = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    # dominante Farben per k-means
    daten = klein.reshape(-1, 3).astype(np.float32)
    krit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
    _, labels, centers = cv2.kmeans(daten, k, None, krit, 3, cv2.KMEANS_PP_CENTERS)
    zaehl = np.bincount(labels.flatten(), minlength=k).astype(float)
    anteil = zaehl / zaehl.sum()
    ordn = np.argsort(-anteil)
    farben = [{"hex": "#%02X%02X%02X" % (int(centers[i][2]), int(centers[i][1]), int(centers[i][0])),
               "rgb": [int(centers[i][2]), int(centers[i][1]), int(centers[i][0])],
               "anteil": round(float(anteil[i]), 4)} for i in ordn]

    v = hsv[:, :, 2].astype(float) / 255 * 100      # Helligkeit in %
    s = hsv[:, :, 1].astype(float) / 255 * 100      # Saettigung in %
    lap = cv2.Laplacian(grau_o, cv2.CV_64F).var()   # Detailschaerfe
    kanten = cv2.Canny(grau_o, 80, 160)
    h = kanten.shape[0]
    return {
        "datei": os.path.basename(pfad),
        "farben": farben,
        "hell_median": round(float(np.median(v)), 2),
        "hell_p10": round(float(np.percentile(v, 10)), 2),
        "hell_p90": round(float(np.percentile(v, 90)), 2),
        "satt_median": round(float(np.median(s)), 2),
        "satt_p10": round(float(np.percentile(s, 10)), 2),
        "satt_p90": round(float(np.percentile(s, 90)), 2),
        "kontrastumfang": round(float(np.percentile(v, 95) - np.percentile(v, 5)), 2),
        "laplace_varianz": round(float(lap), 2),
        "kantendichte_oben": round(float((kanten[:h // 2] > 0).mean()), 5),
        "kantendichte_unten": round(float((kanten[h // 2:] > 0).mean()), 5),
    }


def aggregiere(einzel):
    def sp(feld):
        w = [e[feld] for e in einzel if e and feld in e]
        if not w:
            return None
        return {"median": round(float(np.median(w)), 2),
                "p10": round(float(np.percentile(w, 10)), 2),
                "p90": round(float(np.percentile(w, 90)), 2),
                "min": round(float(np.min(w)), 2), "max": round(float(np.max(w)), 2)}
    # Palette ueber alle Frames: alle dominanten Farben erneut clustern
    alle = np.array([f["rgb"] for e in einzel if e for f in e["farben"]], dtype=np.float32)
    gew = np.array([f["anteil"] for e in einzel if e for f in e["farben"]], dtype=np.float32)
    palette = []
    if len(alle) >= 6:
        krit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1.0)
        _, lab, cen = cv2.kmeans(alle, 6, None, krit, 5, cv2.KMEANS_PP_CENTERS)
        lab = lab.flatten()
        for i in range(6):
            m = lab == i
            if not m.any():
                continue
            palette.append({"hex": "#%02X%02X%02X" % tuple(int(x) for x in cen[i]),
                            "rgb": [int(x) for x in cen[i]],
                            "gewicht": round(float(gew[m].sum() / gew.sum()), 4)})
        palette.sort(key=lambda x: -x["gewicht"])
    return {
        "n_frames": len([e for e in einzel if e]),
        "palette": palette,
        "hell_median": sp("hell_median"), "hell_p10": sp("hell_p10"), "hell_p90": sp("hell_p90"),
        "satt_median": sp("satt_median"),
        "kontrastumfang": sp("kontrastumfang"),
        "laplace_varianz": sp("laplace_varianz"),
        "kantendichte_oben": sp("kantendichte_oben"),
        "kantendichte_unten": sp("kantendichte_unten"),
    }


# ---------------------------------------------------------------- A4 Bewegung
def bewegung(paare):
    orb = cv2.ORB_create(2000)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    raus = []
    for nr, pa, pb in paare:
        a = cv2.imread(pa, cv2.IMREAD_GRAYSCALE)
        b = cv2.imread(pb, cv2.IMREAD_GRAYSCALE)
        if a is None or b is None:
            continue
        ka, da = orb.detectAndCompute(a, None)
        kb, db = orb.detectAndCompute(b, None)
        e = {"shot": nr}
        if da is not None and db is not None and len(ka) >= 10 and len(kb) >= 10:
            m = sorted(bf.match(da, db), key=lambda x: x.distance)[:200]
            if len(m) >= 8:
                src = np.float32([ka[x.queryIdx].pt for x in m]).reshape(-1, 1, 2)
                dst = np.float32([kb[x.trainIdx].pt for x in m]).reshape(-1, 1, 2)
                H, maske = cv2.findHomography(src, dst, cv2.RANSAC, 3.0)
                if H is not None:
                    # Zoom aus dem Skalenanteil, Rotation aus der oberen 2x2
                    zoom = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
                    rot = float(np.degrees(np.arctan2(H[1, 0], H[0, 0])))
                    proj = cv2.perspectiveTransform(src, H)
                    rest = float(np.median(np.linalg.norm(proj - dst, axis=2)))
                    e.update({"zoom": round(zoom, 4),
                              "verschiebung_px": [round(float(H[0, 2]), 1), round(float(H[1, 2]), 1)],
                              "rotation_grad": round(rot, 3),
                              "restfehler_px": round(rest, 2),
                              "inlier_quote": round(float(maske.mean()), 3),
                              "n_matches": len(m)})
        # optischer Fluss als Bewegungsstaerke
        af = cv2.resize(a, (320, 180)); bfm = cv2.resize(b, (320, 180))
        fl = cv2.calcOpticalFlowFarneback(af, bfm, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag = np.linalg.norm(fl, axis=2)
        e["fluss_median_px"] = round(float(np.median(mag)), 3)
        e["fluss_p90_px"] = round(float(np.percentile(mag, 90)), 3)
        raus.append(e)
    return raus


# ---------------------------------------------------------------- A5 Reuse
def reuse(frames, phash_schwelle=8, homo_inlier=0.55):
    import imagehash
    from PIL import Image
    hashes = []
    for p in frames:
        try:
            hashes.append((p, imagehash.phash(Image.open(p)), imagehash.dhash(Image.open(p))))
        except Exception:
            pass
    dubletten = []
    for (p1, ph1, dh1), (p2, ph2, dh2) in itertools.combinations(hashes, 2):
        dp, dd = ph1 - ph2, dh1 - dh2
        if dp <= phash_schwelle and dd <= phash_schwelle + 4:
            dubletten.append({"a": os.path.basename(p1), "b": os.path.basename(p2),
                              "phash_abstand": int(dp), "dhash_abstand": int(dd), "art": "dublette"})
    # Ausschnitte: Homographie mit deutlichem Skalenanteil
    orb = cv2.ORB_create(2000)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    bekannt = {(d["a"], d["b"]) for d in dubletten}
    ausschnitte = []
    for p1, p2 in itertools.combinations(frames, 2):
        if (os.path.basename(p1), os.path.basename(p2)) in bekannt:
            continue
        a = cv2.imread(p1, cv2.IMREAD_GRAYSCALE); b = cv2.imread(p2, cv2.IMREAD_GRAYSCALE)
        if a is None or b is None:
            continue
        ka, da = orb.detectAndCompute(a, None); kb, db = orb.detectAndCompute(b, None)
        if da is None or db is None or len(ka) < 20 or len(kb) < 20:
            continue
        m = sorted(bf.match(da, db), key=lambda x: x.distance)[:200]
        if len(m) < 25:
            continue
        src = np.float32([ka[x.queryIdx].pt for x in m]).reshape(-1, 1, 2)
        dst = np.float32([kb[x.trainIdx].pt for x in m]).reshape(-1, 1, 2)
        H, maske = cv2.findHomography(src, dst, cv2.RANSAC, 4.0)
        if H is None:
            continue
        q = float(maske.mean())
        skala = float(np.sqrt(abs(np.linalg.det(H[:2, :2]))))
        if q >= homo_inlier and 0.15 < skala < 6.0 and abs(skala - 1.0) > 0.12:
            ausschnitte.append({"a": os.path.basename(p1), "b": os.path.basename(p2),
                                "skala": round(skala, 3), "inlier_quote": round(q, 3),
                                "art": "ausschnitt"})
    return {"dubletten": dubletten, "ausschnitte": ausschnitte}


def einzigartige_sekunden(shots, treffer):
    """Verhaeltnis einzigartiger generierter Sekunden zur Gesamtlaufzeit (A5c)."""
    import re
    def nr(name):
        m = re.search(r"shot_(\d+)", name)
        return int(m.group(1)) if m else None
    eltern = {}
    def wurzel(x):
        while eltern.get(x, x) != x:
            x = eltern[x]
        return x
    for t in treffer["dubletten"] + treffer["ausschnitte"]:
        a, b = nr(t["a"]), nr(t["b"])
        if a is None or b is None:
            continue
        eltern.setdefault(a, a); eltern.setdefault(b, b)
        ra, rb = wurzel(a), wurzel(b)
        if ra != rb:
            eltern[max(ra, rb)] = min(ra, rb)
    dauer = {s["nr"]: s["dauer_s"] for s in shots}
    gesamt = sum(dauer.values())
    gesehen, einzig = set(), 0.0
    for n, d in dauer.items():
        w = wurzel(n) if n in eltern else n
        if w not in gesehen:
            gesehen.add(w)
            einzig += d
    return {"laufzeit_s": round(gesamt, 1), "einzigartige_s": round(einzig, 1),
            "verhaeltnis": round(einzig / gesamt, 4) if gesamt else None,
            "gruppen": len(gesehen), "shots": len(dauer)}


# ---------------------------------------------------------------- C2 Vergleich
def palettenabstand(pal_a, pal_b):
    """Mittlerer CIEDE2000-Abstand: je Farbe aus A die naechstliegende aus B."""
    from skimage.color import rgb2lab, deltaE_ciede2000
    if not pal_a or not pal_b:
        return None
    la = rgb2lab(np.array([[c["rgb"] for c in pal_a]], dtype=np.float64) / 255.0)[0]
    lb = rgb2lab(np.array([[c["rgb"] for c in pal_b]], dtype=np.float64) / 255.0)[0]
    ab = []
    for i in range(len(la)):
        d = [float(deltaE_ciede2000(la[i], lb[j])) for j in range(len(lb))]
        ab.append(min(d))
    gew = np.array([c.get("gewicht", c.get("anteil", 1.0)) for c in pal_a], dtype=float)
    gew = gew / gew.sum() if gew.sum() else None
    return {"mittel": round(float(np.mean(ab)), 2),
            "gewichtet": round(float(np.average(ab, weights=gew)), 2) if gew is not None else None,
            "max": round(float(np.max(ab)), 2),
            "je_farbe": [round(x, 2) for x in ab]}


def vergleiche(kandidat_json, ref):
    p = palettenabstand(kandidat_json["palette"], ref["palette"])
    def diff(feld):
        a, b = kandidat_json.get(feld), ref.get(feld)
        if not a or not b:
            return None
        return round(a["median"] - b["median"], 2)
    lap_k = kandidat_json["laplace_varianz"]["median"]
    lap_r = ref["laplace_varianz"]["median"]
    return {
        "palette_ciede2000_mittel": p["mittel"] if p else None,
        "palette_ciede2000_gewichtet": p["gewichtet"] if p else None,
        "hell_median_diff_pp": diff("hell_median"),
        "satt_median_diff_pp": diff("satt_median"),
        "kontrast_diff_pp": diff("kontrastumfang"),
        "laplace_verhaeltnis": round(lap_k / lap_r, 3) if lap_r else None,
    }


def gesamtabweichung(v):
    """Normierte Summe — je kleiner desto naeher an der Vorlage."""
    t = 0.0
    if v["palette_ciede2000_mittel"] is not None: t += v["palette_ciede2000_mittel"] / 15.0
    if v["hell_median_diff_pp"] is not None:      t += abs(v["hell_median_diff_pp"]) / 20.0
    if v["satt_median_diff_pp"] is not None:      t += abs(v["satt_median_diff_pp"]) / 20.0
    if v["kontrast_diff_pp"] is not None:         t += abs(v["kontrast_diff_pp"]) / 20.0
    if v["laplace_verhaeltnis"]:                  t += abs(np.log2(v["laplace_verhaeltnis"]))
    return round(t, 3)


# ---------------------------------------------------------------- CLI
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("inventar");  a.add_argument("videos", nargs="+")
    b = sub.add_parser("schnitte");  b.add_argument("video"); b.add_argument("--schwelle", type=float, default=27.0); b.add_argument("--out")
    c = sub.add_parser("frames");    c.add_argument("video"); c.add_argument("--out", required=True); c.add_argument("--schwelle", type=float, default=27.0)
    d = sub.add_parser("messen");    d.add_argument("frame_dir"); d.add_argument("--out", required=True); d.add_argument("--maske", help="Zeilenband y1:y2 entfernen, z.B. eingebrannte Untertitel"); d.add_argument("--normpx", type=int, help="auf N Pixel normieren, z.B. 2000000")
    e = sub.add_parser("bewegung");  e.add_argument("video"); e.add_argument("--out", required=True); e.add_argument("--schwelle", type=float, default=27.0)
    f = sub.add_parser("reuse");     f.add_argument("frame_dir"); f.add_argument("--out", required=True); f.add_argument("--shots")
    g = sub.add_parser("vergleich"); g.add_argument("kand_dir"); g.add_argument("--ref", required=True); g.add_argument("--out"); g.add_argument("--maske"); g.add_argument("--normpx", type=int)
    x = ap.parse_args()

    if x.cmd == "inventar":
        r = [ffprobe(p) for p in x.videos]
        print(json.dumps(r, indent=2, ensure_ascii=False)); return

    if x.cmd == "schnitte":
        s = schnitte(x.video, x.schwelle)
        dn = [i["dauer_s"] for i in s]
        out = {"video": x.video, "schwelle": x.schwelle, "n_shots": len(s),
               "median_s": round(float(np.median(dn)), 2) if dn else None,
               "mittel_s": round(float(np.mean(dn)), 2) if dn else None,
               "histogramm": histogramm(dn), "shots": s}
        if x.out: json.dump(out, open(x.out, "w"), indent=2)
        print(json.dumps({k: v for k, v in out.items() if k != "shots"}, indent=2, ensure_ascii=False)); return

    if x.cmd == "frames":
        s = schnitte(x.video, x.schwelle)
        m = mittelframes(x.video, s, x.out)
        randframes(x.video, s, x.out + "_rand")
        json.dump(s, open(os.path.join(x.out, "_shots.json"), "w"), indent=2)
        print(f"{len(m)} Mittelframes -> {x.out}"); return

    if x.cmd == "messen":
        fr = sorted(glob.glob(os.path.join(x.frame_dir, "*.png")) + glob.glob(os.path.join(x.frame_dir, "*.jpg")))
        mk = tuple(int(v) for v in x.maske.split(":")) if getattr(x, "maske", None) else None
        einzel = [messe_frame(p, maske=mk, normpx=x.normpx) for p in fr]
        agg = aggregiere(einzel)
        agg["quelle"] = x.frame_dir
        agg["maske"] = list(mk) if mk else None
        agg["normpx"] = x.normpx
        agg["einzelframes"] = [e for e in einzel if e]
        os.makedirs(os.path.dirname(x.out) or ".", exist_ok=True)
        json.dump(agg, open(x.out, "w"), indent=2, ensure_ascii=False)
        print(json.dumps({k: v for k, v in agg.items() if k != "einzelframes"}, indent=2, ensure_ascii=False)); return

    if x.cmd == "bewegung":
        s = schnitte(x.video, x.schwelle)
        d = x.out + "_frames"
        paare = randframes(x.video, s, d)
        r = bewegung(paare)
        zoom = [i["zoom"] for i in r if "zoom" in i]
        rest = [i["restfehler_px"] for i in r if "restfehler_px" in i]
        fl = [i["fluss_median_px"] for i in r]
        out = {"n_shots": len(r),
               "zoom": {"median": round(float(np.median(zoom)), 4), "p10": round(float(np.percentile(zoom, 10)), 4),
                        "p90": round(float(np.percentile(zoom, 90)), 4)} if zoom else None,
               "restfehler_px": {"median": round(float(np.median(rest)), 2),
                                 "p90": round(float(np.percentile(rest, 90)), 2)} if rest else None,
               "fluss_median_px": {"median": round(float(np.median(fl)), 3),
                                   "p90": round(float(np.percentile(fl, 90)), 3)} if fl else None,
               "je_shot": r}
        json.dump(out, open(x.out, "w"), indent=2)
        print(json.dumps({k: v for k, v in out.items() if k != "je_shot"}, indent=2, ensure_ascii=False)); return

    if x.cmd == "reuse":
        fr = sorted(glob.glob(os.path.join(x.frame_dir, "*.png")))
        t = reuse(fr)
        if x.shots:
            t["kennzahl"] = einzigartige_sekunden(json.load(open(x.shots)), t)
        json.dump(t, open(x.out, "w"), indent=2, ensure_ascii=False)
        print(json.dumps({"dubletten": len(t["dubletten"]), "ausschnitte": len(t["ausschnitte"]),
                          "kennzahl": t.get("kennzahl")}, indent=2, ensure_ascii=False)); return

    if x.cmd == "vergleich":
        ref = json.load(open(x.ref))
        rows = []
        for p in sorted(glob.glob(os.path.join(x.kand_dir, "*.png")) + glob.glob(os.path.join(x.kand_dir, "*.jpg"))):
            e = messe_frame(p, maske=tuple(int(v) for v in x.maske.split(":")) if x.maske else None, normpx=x.normpx)
            if not e: continue
            agg = aggregiere([e])
            v = vergleiche(agg, ref)
            v["kandidat"] = os.path.basename(p)
            v["gesamtabweichung"] = gesamtabweichung(v)
            rows.append(v)
        rows.sort(key=lambda r: r["gesamtabweichung"])
        for i, r in enumerate(rows, 1): r["rang"] = i
        if x.out: json.dump(rows, open(x.out, "w"), indent=2, ensure_ascii=False)
        print(json.dumps(rows, indent=2, ensure_ascii=False)); return


if __name__ == "__main__":
    main()
