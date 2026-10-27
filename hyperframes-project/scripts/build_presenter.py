"""Builds assets/presenter.mp4 (66 s) from one short Flow clip, re-using it between camera cuts."""
import subprocess, sys
src, out = sys.argv[1], sys.argv[2]
S = [0,2.79,4.15,6.05,9.03,11.0,13.31,18.67,21.12,24.42,28.68,33.32,35.92,37.24,38.36,
     43.4,46.12,48.36,50.92,52.36,56.04,61.04,62.12,65.85]
FPS, CLIPF = 30, 178  # source is 6 s; leave a couple of frames of margin
parts, labels = ["[0:v]fps=30,split=%d%s" % (len(S)-1, "".join(f"[i{i}]" for i in range(len(S)-1)))], []
for i in range(len(S)-1):
    n = round(S[i+1]*FPS) - round(S[i]*FPS)
    room = CLIPF - n
    off = int((i*69) % room) if room > 1 else 0
    parts.append(f"[i{i}]trim=start_frame={off}:end_frame={off+n},setpts=PTS-STARTPTS[s{i}]")
    labels.append(f"[s{i}]")
fc = ";".join(parts) + ";" + "".join(labels) + f"concat=n={len(labels)}:v=1:a=0," \
     "scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,format=yuv420p[v]"
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",fc,"-map","[v]","-an","-r","30",
    "-c:v","libx264","-crf","16","-preset","medium","-g","30","-movflags","+faststart",out], check=True)
