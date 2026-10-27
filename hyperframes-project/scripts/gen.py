"""Writes compositions/captions.html and the SFX <audio> tags into index.html."""
import re, sys
from pathlib import Path

proj = Path(sys.argv[1])

# (start, end, text) — *word* is highlighted in coral
G = [
    (0.10, 1.40, "Video yang awak tengok ni,"),
    (1.43, 2.75, "saya tak edit langsung."),
    (2.79, 4.10, "Tak buka *CapCut,*"),
    (4.15, 5.15, "tak buka *Canva,*"),
    (5.20, 6.08, "saya cuma suruh"),
    (6.11, 7.50, "*Claude* dan dia siapkan"),
    (7.52, 9.00, "dalam beberapa minit."),
    (9.03, 11.00, "Nama tool dia *HyperFrames.*"),
    (11.03, 12.26, "Ia tool open source"),
    (12.28, 13.28, "dari *HeyGen.*"),
    (13.31, 14.47, "Kita bagi arahan *Claude*"),
    (14.49, 15.89, "tukar jadi video animasi"),
    (15.91, 17.22, "lengkap dengan teks,"),
    (17.24, 18.64, "transisi dan muzik."),
    (18.67, 19.90, "Caranya senang je,"),
    (19.92, 21.10, "tiga langkah."),
    (21.15, 22.14, "*Pertama,*"),
    (22.16, 23.25, "buka *Claude,*"),
    (23.27, 24.42, "pergi ke connector,"),
    (24.44, 25.42, "cari *HyperFrames*"),
    (25.44, 27.00, "dan tekan *add.*"),
    (27.03, 28.64, "Pastikan dia dah connect."),
    (28.68, 29.57, "Tapi kalau nak"),
    (29.59, 30.70, "cara lagi senang,"),
    (30.72, 32.11, "type je dalam chat *Claude,*"),
    (32.13, 33.38, "install *HyperFrames.*"),
    (33.40, 34.33, "*Claude* akan tunjukkan"),
    (34.35, 35.22, "cara connect terus,"),
    (35.24, 35.90, "siap."),
    (35.92, 37.22, "*Kedua,* bagi arahan,"),
    (37.24, 38.34, "cakap je macam biasa."),
    (38.36, 38.92, "Contohnya,"),
    (38.94, 40.13, "buat video 10 saat,"),
    (40.15, 40.94, "format menegak."),
    (40.96, 41.88, "Tajuk fade in,"),
    (41.90, 42.67, "latar biru,"),
    (42.69, 43.38, "ada muzik."),
    # 43.40–46.10 is the big serif card in step2
    (46.12, 46.85, "*Ketiga,*"),
    (46.87, 48.34, "tunggu sekejap."),
    (48.36, 49.35, "*Claude* akan tulis"),
    (49.37, 50.13, "dan render video"),
    (50.15, 50.90, "tu terus jadi *MP4.*"),
    (50.92, 51.57, "Tak puas hati,"),
    (51.59, 52.34, "suruh je ubah."),
    (52.36, 53.17, "tukar warna,"),
    (53.19, 54.09, "tambah teks,"),
    (54.11, 55.01, "laju sikit,"),
    (55.03, 56.02, "semua boleh."),
    (56.04, 56.91, "Boleh guna untuk"),
    (56.93, 57.74, "intro produk,"),
    (57.76, 58.82, "slide beranimasi,"),
    (58.84, 59.81, "video explainer"),
    (59.83, 61.02, "atau content *TikTok.*"),
    (61.04, 62.10, "Senang je kan?"),
    (62.12, 63.73, "Cuba sekarang dan *follow*"),
    (63.75, 65.80, "untuk lebih banyak tips *AI.*"),
]

groups_html, js = [], []
for gi, (s, e, text) in enumerate(G):
    words = text.split()
    total = sum(len(w.strip("*")) + 2 for w in words)
    span_t = (e - s) * 0.92
    t = s
    spans = []
    for wi, w in enumerate(words):
        hl = w.startswith("*")
        clean = w.strip("*")
        cls = "w hl" if hl else "w"
        spans.append(f'<span id="c{gi}w{wi}" class="{cls}">{clean}</span>')
        js.append(f'  lit("#c{gi}w{wi}", {t:.2f});')
        t += span_t * (len(clean) + 2) / total
    gid = f"cg{gi}"
    groups_html.append(
        f'    <div id="{gid}" class="cap clip" data-start="{s:.2f}" data-duration="{e - s:.2f}">'
        f'<div class="pill" id="{gid}p">{" ".join(spans)}</div></div>'
    )
    js.append(f'  show("#{gid}p", {s:.2f}, {e:.2f});')

html = f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cap {{
      position: absolute; left: 0; right: 0; top: 1236px;
      display: flex; justify-content: center; overflow: visible;
    }}
    .pill {{
      display: inline-block; max-width: 920px; text-align: center;
      background: rgba(42, 31, 28, 0.82); border-radius: 18px;
      padding: 12px 26px 16px;
      font-family: "Montserrat", sans-serif; font-weight: 800; font-size: 54px;
      line-height: 1.15; color: #fff; letter-spacing: -0.005em;
    }}
    .w {{ opacity: 0.5; }}
    .hl {{ color: #ff9670; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(groups_html)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    const show = (sel, s, e) => {{
      tl.fromTo(sel, {{ opacity: 0, y: 14, scale: 0.94 }}, {{ opacity: 1, y: 0, scale: 1, duration: 0.16, ease: "back.out(2)" }}, s);
      tl.to(sel, {{ opacity: 0, duration: 0.1, ease: "power2.in" }}, e - 0.1);
    }};
    const lit = (sel, t) => tl.to(sel, {{ opacity: 1, duration: 0.08 }}, t);
{chr(10).join(js)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""
(proj / "compositions/captions.html").write_text(html)

# SFX cues: (time, file, volume)
SFX = [
    (2.05, "whoosh-short", 0.35), (2.79, "pop", 0.45), (4.15, "click", 0.5), (4.3, "pop", 0.4),
    (6.11, "pop", 0.4), (7.55, "chime", 0.25), (9.03, "whoosh-short", 0.4), (11.03, "pop", 0.4),
    (12.28, "pop", 0.35), (13.45, "pop", 0.35), (14.2, "click", 0.4), (15.1, "click", 0.4),
    (16.4, "pop", 0.3), (17.3, "pop", 0.3), (18.67, "whoosh-short", 0.35), (19.92, "click", 0.4),
    (21.12, "whoosh-short", 0.45), (23.25, "click", 0.45), (24.45, "typing", 0.3), (25.8, "click", 0.5),
    (26.4, "pop", 0.4), (27.05, "chime", 0.25), (28.68, "whoosh-short", 0.35), (32.13, "typing", 0.3),
    (33.0, "click", 0.45), (33.6, "pop", 0.35), (35.25, "chime", 0.3), (35.92, "whoosh-short", 0.4),
    (38.4, "pop", 0.35), (39.2, "click", 0.35), (40.2, "click", 0.35), (41.0, "click", 0.35),
    (41.95, "click", 0.35), (42.75, "click", 0.35), (43.4, "whoosh-short", 0.35), (46.12, "whoosh-short", 0.4),
    (48.4, "pop", 0.35), (50.75, "chime", 0.3), (50.92, "whoosh-short", 0.35), (52.4, "pop", 0.35),
    (53.2, "pop", 0.35), (54.1, "pop", 0.35), (55.05, "sparkle", 0.3), (56.93, "pop", 0.35),
    (57.76, "pop", 0.35), (58.84, "pop", 0.35), (59.9, "pop", 0.35), (61.1, "sparkle", 0.35),
    (62.12, "whoosh-short", 0.35), (63.45, "click", 0.5), (63.55, "chime", 0.3),
]
dur = {"pop": 0.72, "click": 0.36, "whoosh-short": 0.57, "chime": 2.5, "typing": 1.5, "sparkle": 1.8}
lane_end, rows = [0.0, 0.0, 0.0], []
for i, (t, f, v) in enumerate(SFX):
    d = min(dur[f], 65.85 - t)
    lane = next(k for k in range(3) if lane_end[k] <= t)
    lane_end[lane] = t + d
    rows.append(f'      <audio id="sfx{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{t}" '
                f'data-duration="{d:.2f}" data-track-index="{4 + lane}" data-volume="{v}"></audio>')
tags = "\n".join(rows)
idx = (proj / "index.html").read_text()
idx = re.sub(r"<!-- SFX__ -->.*?(?=\n    </div>\n    <script>)", "<!-- SFX__ -->\n" + tags, idx, flags=re.S)
(proj / "index.html").write_text(idx)
print("ok", len(G), "groups", len(SFX), "sfx")
