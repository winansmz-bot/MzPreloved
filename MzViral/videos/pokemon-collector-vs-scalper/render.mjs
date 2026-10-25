// Usage: node render.mjs            -> out/frames piped to ffmpeg, out/video.mp4
//        node render.mjs stills t1 t2 ...  -> out/still-<t>.png
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright");
import { spawn } from "node:child_process";
import { writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dir = path.dirname(fileURLToPath(import.meta.url));
const FPS = 30;
const [mode, ...times] = process.argv.slice(2);

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto("file://" + path.join(dir, "index.html"));
await page.evaluate(() => window.__ready);
const total = await page.evaluate(() => window.__total);
writeFileSync(path.join(dir, "out/cues.json"), JSON.stringify(await page.evaluate(() => window.CUES)));

if (mode === "stills") {
  for (const t of times) {
    await page.evaluate(t => window.__seek(t), +t);
    await page.screenshot({ path: path.join(dir, `out/still-${t}.png`) });
  }
} else {
  const ff = spawn("ffmpeg", ["-y", "-v", "error", "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", path.join(dir, "out/video.mp4")],
    { stdio: ["pipe", "inherit", "inherit"] });
  const n = Math.round(total * FPS);
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => window.__seek(t), i / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
    if (i % 150 === 0) console.log(`frame ${i}/${n}`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on("close", r));
}
await browser.close();
