"""Generates out/audio.wav: a 120 BPM bed plus SFX synced to out/cues.json (written by render.mjs)."""
import json, wave, numpy as np
from pathlib import Path

SR, TOTAL, BEAT = 48000, 46.0, 0.5
DROP = (27.0, 28.6)  # music cuts out for "So who protects the hobby here?" then lands on "US."
out = Path(__file__).parent / "out"
rng = np.random.default_rng(7)
mix = np.zeros(int(SR * TOTAL))

def add(sig, at, gain=1.0):
    i = int(at * SR)
    if i < 0: sig, i = sig[-i:], 0
    if i >= len(mix): return
    sig = sig[: len(mix) - i]
    mix[i : i + len(sig)] += sig * gain

def t_(d): return np.arange(int(d * SR)) / SR

def lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    a = np.broadcast_to(a, x.shape)
    for i in range(len(x)):
        acc += a[i] * (x[i] - acc); y[i] = acc
    return y

def kick(d=0.35, f0=150, f1=42):
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def noise(d): return rng.standard_normal(int(d * SR))

def hat():
    n = noise(0.05); return (n - lowpass(n, 0.3)) * np.exp(-t_(0.05) * 90)

def tone(freq, d, harmonics=(1,), decay=0.0):
    t = t_(d); s = sum(np.sin(2 * np.pi * freq * h * t) / h for h in harmonics)
    return s * (np.exp(-t * decay) if decay else 1)

def env(sig, a=0.01, r=0.05):
    n = len(sig); e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    e[:ai] = np.linspace(0, 1, ai); e[n - ri:] *= np.linspace(1, 0, ri)
    return sig * e

def muted(at): return DROP[0] <= at < DROP[1]

# progression: Am F C G, one chord per bar (4 beats)
roots = [55.0, 43.65, 65.41, 49.0]
chords = [[220, 261.6, 329.6], [174.6, 220, 261.6], [196, 261.6, 329.6], [196, 246.9, 293.7]]
nbeats = int(TOTAL / BEAT)
for b in range(nbeats):
    at = b * BEAT
    if muted(at): continue
    bar = (b // 4) % 4
    add(kick(), at, 0.9)
    add(hat(), at + BEAT / 2, 0.25)
    if b % 2: add(env(noise(0.12) * np.exp(-t_(0.12) * 25)), at, 0.18)  # snare-ish on 2 & 4
    for k in range(2):  # 8th-note bass
        add(env(tone(roots[bar], BEAT / 2, (1, 2, 3, 4)) * 0.5, 0.005, 0.04), at + k * BEAT / 2, 0.35)
    if b % 4 == 0:
        d = min(4 * BEAT, DROP[0] - at) if at < DROP[0] else 4 * BEAT
        if d > 0.1:
            add(env(sum(tone(f, d, (1, 2)) for f in chords[bar]) / 3, 0.4, 0.4), at, 0.12)

# riser into the drop
d = DROP[1] - DROP[0]; t = t_(d)
add(np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / d) ** 2) / SR) * (t / d) ** 2, DROP[0], 0.25)
add(lowpass(noise(d), 0.02 + 0.3 * (t / d)) * (t / d) ** 2, DROP[0], 0.8)

def layer(*sigs):
    out = np.zeros(max(len(x) for x in sigs))
    for x in sigs: out[: len(x)] += x
    return out

def whoosh():
    d = 0.35; t = t_(d); a = 0.02 + 0.25 * np.sin(np.pi * t / d)
    return lowpass(noise(d), a) * np.sin(np.pi * t / d) ** 2 * 1.6
def hit(): return layer(kick(0.4, 220, 40), lowpass(noise(0.15), 0.4) * np.exp(-t_(0.15) * 30) * 0.5)
def stamp(): return layer(kick(0.5, 120, 35) * 1.3, lowpass(noise(0.25), 0.6) * np.exp(-t_(0.25) * 22))
def tick(): return tone(1800, 0.04, (1,), 120)
def pop():
    t = t_(0.12); return np.sin(2 * np.pi * np.cumsum(500 + 700 * t / 0.12) / SR) * np.exp(-t * 30)
def scan():
    t = t_(1.2); return np.sin(2 * np.pi * np.cumsum(600 + 300 * np.sin(t * 9)) / SR) * 0.3 * np.sin(np.pi * t / 1.2)
def rise():
    t = t_(1.0); return np.sin(2 * np.pi * np.cumsum(180 + 700 * t) / SR) * t * 0.6
def boom():
    t = t_(1.6); return layer(np.sin(2 * np.pi * 38 * t) * np.exp(-t * 2.5) * 1.4, kick(0.6, 200, 35), lowpass(noise(1.6), 0.08) * np.exp(-t * 3))

sfx = dict(whoosh=(whoosh, .45), hit=(hit, .7), stamp=(stamp, .8), tick=(tick, .35),
           pop=(pop, .45), scan=(scan, .5), rise=(rise, .5), boom=(boom, 1.0))
for at, kind in json.loads((out / "cues.json").read_text()):
    fn, g = sfx[kind]; add(fn(), at - (0.15 if kind == "whoosh" else 0), g)

fade = int(0.8 * SR); mix[-fade:] *= np.linspace(1, 0, fade)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) * 0.89
pcm = (np.repeat(mix[:, None], 2, axis=1) * 32767).astype("<i2")
with wave.open(str(out / "audio.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("wrote", out / "audio.wav")
