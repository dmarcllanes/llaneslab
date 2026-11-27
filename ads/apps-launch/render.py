"""Render an ad page to MP4 at 30fps.
AD=landscape renders ad-landscape.html at 1920x1080 (default: ad-vertical.html at 1080x1920).
Usage:  uv run --with playwright python render.py [out.mp4]
        uv run --with playwright python render.py --stills 2,12,20 outdir
"""
import asyncio, subprocess, sys
from pathlib import Path
from playwright.async_api import async_playwright

HERE = Path(__file__).resolve().parent
import os
AD = os.environ.get("AD", "vertical")
W, H = (1920, 1080) if AD == "landscape" else (1080, 1920)
PAGE = (HERE / f"ad-{AD}.html").as_uri() + "?render=1"
FPS = 30

async def main():
    args = sys.argv[1:]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        await pg.goto(PAGE, wait_until="networkidle")
        await pg.evaluate("document.fonts.ready")
        if args and args[0] == "--stills":
            out = Path(args[2]); out.mkdir(parents=True, exist_ok=True)
            for t in args[1].split(","):
                await pg.evaluate(f"seek({t})")
                await pg.screenshot(path=str(out / f"t{float(t):05.1f}.png"))
            await b.close(); return
        dest = Path(args[0]) if args else HERE / f"apps-launch-{AD}.mp4"
        dur = await pg.evaluate("DUR")
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest)],
                              stdin=subprocess.PIPE)
        n = int(dur * FPS)
        for i in range(n):
            await pg.evaluate(f"seek({i / FPS})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=95))
            if i % 150 == 0: print(f"{i}/{n}", flush=True)
        ff.stdin.close(); ff.wait()
        await b.close()
        print("wrote", dest)

asyncio.run(main())
