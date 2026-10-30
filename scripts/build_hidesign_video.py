import os, subprocess, numpy as np, wave

UP = "/root/.claude/uploads/2e796f7b-bd6e-58af-aae8-dffd0732b3f2/"
WD = os.path.dirname(os.path.abspath(__file__)) + "/work"
OUT = "/home/user/MzPreloved/videos/hidesign-aberdeen-resell.mp4"
os.makedirs(WD, exist_ok=True); os.makedirs(os.path.dirname(OUT), exist_ok=True)
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
FONT2 = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
FPS = 30

IMG = {k: UP + v for k, v in dict(
    hero="d19f8596-image.jpg", buckle="d0f72bde-image.jpg", angle="4e78fefa-image.jpg",
    open="a1016912-image.jpg", inside="21dfe7cb-image.jpg", side="9ab3f8ef-image.jpg",
    sleeve="2d813235-image.jpg", back="3ce24f35-image.jpg", card="6c609570-image.jpg").items()}

# (image, dur, focus x, focus y (0-1 of original), zoom start, zoom end, headline, subline, sfx)
SEG = [
    ("hero",   2.3, .50, .48, 1.00, 1.12, "Bought in 2008.", "Hidesign Aberdeen briefcase", None),
    ("buckle", 2.1, .50, .40, 1.25, 1.05, "18 years later.", "Still looks like this.", "clink"),
    ("card",   2.5, .30, .78, 1.30, 1.75, "Original guarantee card", "Dated 18/9/08", None),
    ("angle",  2.0, .45, .35, 1.05, 1.25, "Vegetable-tanned leather", "Ages darker, not weaker", "clink"),
    ("open",   2.2, .50, .40, 1.00, 1.15, "Lift the flap", "3 zip pockets underneath", "zip"),
    ("inside", 2.2, .45, .50, 1.10, 1.00, "Organiser + main compartment", None, None),
    ("sleeve", 2.2, .60, .60, 1.00, 1.12, "Removable laptop sleeve", None, None),
    ("side",   2.0, .45, .45, 1.15, 1.00, "Hidesign plate. Smooth zips.", None, "zip"),
    ("back",   2.2, .50, .55, 1.00, 1.10, "Back zip pocket", "Padded shoulder strap", None),
    ("angle",  2.4, .58, .48, 1.40, 1.80, "Honest note:", "light wear on the strap tip", None),
    ("hero",   3.4, .50, .50, 1.15, 1.00, "Yours for less than new.", "DM \"BAG\" to buy  |  MZ Preloved", "ching"),
]

def esc(s):
    p = f"{WD}/t{abs(hash(s))}.txt"
    open(p, "w").write(s); return p

def render(i, seg):
    key, d, fx, fy, z0, z1, h1, h2, _ = seg
    n = int(round(d * FPS))
    # crop the 3:4 photo to a 9:16 window around fx, upscale for smooth zoompan
    cw = 1125
    x0 = int(min(max(fx * 1500 - cw / 2, 0), 1500 - cw))
    cx = (fx * 1500 - x0) / cw
    ease = f"(1-cos(PI*on/{n}))/2"
    z = f"{z0}+({z1}-{z0})*{ease}"
    vf = [f"crop={cw}:2000:{x0}:0", "scale=2160:3840",
          f"zoompan=z='{z}':x='max(0,min(iw-iw/zoom,{cx}*iw-iw/zoom/2))':"
          f"y='max(0,min(ih-ih/zoom,{fy}*ih-ih/zoom/2))':d=1:s=1080x1920:fps={FPS}",
          "eq=contrast=1.05:saturation=1.08",
          # bottom gradient for legibility
          "drawbox=y=ih*0.62:w=iw:h=ih*0.38:color=black@0.35:t=fill"]
    a1 = "if(lt(t,0.12),0,min(1,(t-0.12)/0.18))"
    a2 = "if(lt(t,0.40),0,min(1,(t-0.40)/0.18))"
    y1 = "h*0.70-if(lt(t,0.30),(0.30-t)*120,0)"
    vf.append(f"drawtext=fontfile={FONT}:textfile={esc(h1)}:fontsize=78:fontcolor=white:"
              f"shadowcolor=black@0.6:shadowx=3:shadowy=3:x=(w-tw)/2:y='{y1}':alpha='{a1}'")
    if h2:
        vf.append(f"drawtext=fontfile={FONT2}:textfile={esc(h2)}:fontsize=50:fontcolor=0xF3D9A6:"
                  f"shadowcolor=black@0.6:shadowx=2:shadowy=2:x=(w-tw)/2:y=h*0.70+105:alpha='{a2}'")
    vf.append(f"drawtext=fontfile={FONT}:text='MZ PRELOVED':fontsize=34:fontcolor=white@0.85:"
              f"x=(w-tw)/2:y=110:box=1:boxcolor=black@0.35:boxborderw=18")
    if i == len(SEG) - 1:
        vf.append(f"fade=t=out:st={d-0.5}:d=0.5")
    out = f"{WD}/s{i:02d}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", str(FPS),
                    "-i", IMG[key], "-vf", ",".join(vf), "-frames:v", str(n),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out],
                   check=True)
    return out

# ---------------- audio ----------------
SR = 44100
rng = np.random.default_rng(7)

def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / r)

def whoosh(d=0.35):
    n = int(d * SR); x = rng.standard_normal(n)
    # sweep lowpass via cumulative one-pole with varying coefficient
    k = np.linspace(0.02, 0.35, n) ** 1.5; y = np.zeros(n); s = 0
    for i in range(n): s += k[i] * (x[i] - s); y[i] = s
    w = np.sin(np.pi * np.arange(n) / n) ** 2
    return 0.9 * y * w / (np.abs(y).max() + 1e-9)

def pop():
    n = int(0.08 * SR); t = np.arange(n) / SR
    return 0.45 * np.sin(2 * np.pi * (900 - 4000 * t) * t) * env(n, .001, .02)

def clink():
    n = int(0.6 * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(2400, 1), (3710, .6), (5230, .35), (1580, .4)])
    return 0.35 * s * env(n, .001, .12)

def zipper():
    n = int(0.45 * SR); y = np.zeros(n)
    for c in np.linspace(0, n - 400, 38).astype(int):
        y[c:c + 300] += rng.standard_normal(300) * np.exp(-np.arange(300) / 40)
    return 0.35 * y * np.sin(np.pi * np.arange(n) / n)

def ching():
    n = int(1.4 * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    for off, f in [(0, 1318.5), (0.09, 1975.5)]:
        o = int(off * SR); tt = t[: n - o]
        s = sum(a * np.sin(2 * np.pi * f * m * tt) for m, a in [(1, 1), (2.01, .4), (3.03, .2)])
        out[o:] += s * env(n - o, .001, .35)
    return 0.3 * out

def beat(total):
    n = int(total * SR); y = np.zeros(n); bpm = 100; spb = 60 / bpm
    kick_n = int(.25 * SR); kt = np.arange(kick_n) / SR
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-kt * 30)) * kt) * env(kick_n, .002, .12)
    hat_n = int(.05 * SR); hat = np.diff(rng.standard_normal(hat_n + 1)) * env(hat_n, .001, .015) * .12
    snr_n = int(.2 * SR); snare = rng.standard_normal(snr_n) * env(snr_n, .001, .06) * .18
    # warm pad: Dm7 -> Gmaj7 -> Cmaj7 -> Am7
    chords = [[146.8, 174.6, 220, 261.6], [196, 246.9, 293.7, 370], [130.8, 164.8, 196, 246.9], [110, 130.8, 164.8, 196]]
    bar = 4 * spb; t = np.arange(n) / SR
    for b in range(int(total / bar) + 1):
        s0 = int(b * bar * SR); s1 = min(n, int((b + 1) * bar * SR))
        if s0 >= n: break
        tt = t[s0:s1] - t[s0]; ch = chords[b % 4]
        pad = sum(np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt) for f in ch)
        y[s0:s1] += .035 * pad * np.minimum(1, tt / .3) * np.minimum(1, (bar - tt) / .3)
    beat_i = 0; tb = 0.0
    while tb < total:
        i = int(tb * SR)
        def add(x, at):
            e = min(n, at + len(x)); y[at:e] += x[: e - at]
        if beat_i % 2 == 0: add(.6 * kick, i)
        else: add(snare, i)
        add(hat, i); add(hat * .7, int((tb + spb / 2) * SR))
        beat_i += 1; tb += spb
    return y

def build_audio(total):
    y = beat(total) * 0.8
    y *= np.minimum(1, np.arange(len(y)) / (0.3 * SR))
    fade = int(0.8 * SR); y[-fade:] *= np.linspace(1, 0, fade)
    def add(x, at):
        i = int(at * SR); e = min(len(y), i + len(x)); y[i:e] += x[: e - i]
    t = 0
    for i, seg in enumerate(SEG):
        if i > 0: add(whoosh(), t - 0.18)
        add(pop(), t + 0.12)
        if seg[7]: add(pop() * .7, t + 0.40)
        if seg[8] == "clink": add(clink(), t + 0.25)
        if seg[8] == "zip": add(zipper(), t + 0.2)
        if seg[8] == "ching": add(ching(), t + 0.55)
        t += seg[1]
    y = np.tanh(y * 1.2) * 0.85
    p = f"{WD}/audio.wav"
    with wave.open(p, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    return p

if __name__ == "__main__":
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        clips = list(ex.map(lambda a: render(*a), enumerate(SEG)))
    total = sum(s[1] for s in SEG)
    lst = f"{WD}/list.txt"
    open(lst, "w").write("".join(f"file '{c}'\n" for c in clips))
    wav = build_audio(total)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", OUT], check=True)
    print(OUT, total)
