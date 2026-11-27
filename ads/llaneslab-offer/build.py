"""Build the LlanesLab client-offer ad: voiceover -> timeline -> video frames -> music -> final MP4.

Usage (from ads/llaneslab-offer):
    uv run --with numpy --with kokoro-onnx --with soundfile --with playwright python build.py short   # 60s vertical
    uv run --with numpy --with kokoro-onnx --with soundfile --with playwright python build.py full    # full landscape
Env: VOICE=am_michael  SPEED=1.0  LAYOUT=vertical|landscape (default: short->vertical, full->landscape)
     TARGET=60 (short cut default; pads the scenes to exactly this length)  STAGE=all|video|audio
     STILLS=3,12,30  only render stills (to stills-<cut>/) and stop
     VARIANT=face  face-first version: story-face.json, output ...-face.mp4
Story (spoken lines, scene order) lives in story.json; visuals in ad.html.
Output: llaneslab-offer-<layout>-<60s|full>.mp4
"""
import asyncio, json, os, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
CUT = sys.argv[1] if len(sys.argv) > 1 else "short"
LAYOUT = os.environ.get("LAYOUT", "vertical" if CUT == "short" else "landscape")
TARGET = float(os.environ.get("TARGET", "60" if CUT == "short" else "0"))
VOICE = os.environ.get("VOICE", "am_michael")
SPEED = float(os.environ.get("SPEED", "1.05"))
STAGE = os.environ.get("STAGE", "all")
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", HERE.parent / "flow-trio" / "audio" / "models"))
SR, FPS = 44100, 30
LEAD, TAIL = 0.5, 0.9
VARIANT = os.environ.get("VARIANT", "")  # e.g. "face": reads story-face.json, files get a -face suffix
TAG = CUT + (f"-{VARIANT}" if VARIANT else "")
STORY = HERE / (f"story-{VARIANT}.json" if VARIANT else "story.json")
NAME = f"llaneslab-offer-{LAYOUT}-{'60s' if CUT == 'short' else 'full'}" + (f"-{VARIANT}" if VARIANT else "")
VO_DIR = HERE / f"voice-{TAG}"


def run(*a):
    subprocess.run([str(x) for x in a], check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    st = (x.T * 32767).astype("<i2") if x.ndim == 2 else (x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2 if x.ndim == 2 else 1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())


# ------------------------------------------------------------------ voice + timeline
def voice_and_timeline():
    story = [s for s in json.loads(STORY.read_text())["scenes"] if s.get(CUT)]
    VO_DIR.mkdir(exist_ok=True)
    import soundfile as sf
    from kokoro_onnx import Kokoro
    kk = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.int8.onnx"), str(KOKORO_DIR / "voices-v1.0.bin"))
    scenes, t = [], 0.0
    with tempfile.TemporaryDirectory() as td:
        for i, s in enumerate(story):
            raw, out = Path(td) / f"{i}.wav", VO_DIR / f"{i:02d}-{s['id']}.wav"
            audio, sr = kk.create(s[CUT], voice=VOICE, speed=SPEED, lang="en-us")
            sf.write(str(raw), audio, sr)
            run("ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af",
                "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                "-ar", SR, out)
            d = dur(out)
            sd = max(s["min"], LEAD + d + TAIL)
            scenes.append({"id": s["id"], "start": round(t, 3), "dur": round(sd, 3), "voice": out.name, "voice_len": round(d, 3)})
            print(f"  {s['id']:6} {t:6.2f}s +{sd:5.2f}s  voice {d:4.1f}s")
            t += sd
    print(f"  total {t:.1f}s")
    if TARGET:
        extra = TARGET - t
        if extra < 0:
            sys.exit(f"Cut runs {t:.1f}s, over the {TARGET:.0f}s target: shorten some lines in story.json.")
        t = 0.0
        for s in scenes:
            s["dur"] = round(s["dur"] + extra / len(scenes), 3); s["start"] = round(t, 3); t += s["dur"]
        scenes[-1]["dur"] = round(TARGET - scenes[-1]["start"], 3); t = TARGET
        print(f"  padded +{extra:.1f}s -> exactly {TARGET:.0f}s")
    tl = {"dur": round(t, 3), "scenes": scenes}
    (HERE / f"timeline-{TAG}.js").write_text("window.TIMELINE = " + json.dumps(tl, indent=1) + ";\n")
    return tl


def load_timeline():
    s = (HERE / f"timeline-{TAG}.js").read_text()
    return json.loads(s[s.index("{"): s.rindex("}") + 1])


# ------------------------------------------------------------------ video
async def render(dest, stills=None):
    from playwright.async_api import async_playwright
    W, H = (1920, 1080) if LAYOUT == "landscape" else (1080, 1920)
    url = (HERE / "ad.html").as_uri() + f"?layout={LAYOUT}&cut={CUT}&variant={VARIANT}&render=1"
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": W, "height": H})
        await pg.goto(url, wait_until="networkidle")
        await pg.evaluate("document.fonts.ready")
        if stills:
            out = HERE / f"stills-{TAG}"; out.mkdir(exist_ok=True)
            for t in stills:
                await pg.evaluate(f"seek({t})"); await pg.screenshot(path=str(out / f"{LAYOUT}-t{float(t):05.1f}.png"))
            await b.close(); return
        d = await pg.evaluate("DUR")
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest)],
                              stdin=subprocess.PIPE)
        n = int(round(d * FPS))
        for i in range(n):
            await pg.evaluate(f"seek({i / FPS})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=95))
            if i % 300 == 0: print(f"  frame {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); await b.close()


# ------------------------------------------------------------------ music (original, generated)
def music(DUR, cuts):
    n = int(DUR * SR); L = np.zeros(n); R = np.zeros(n)
    bpm = 104; beat = 60 / bpm; bar = beat * 4
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    prog = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67]]   # Cmaj7 - Am7 - Fmaj7 - G
    roots = [48, 45, 41, 43]
    intro_end, build_end = cuts[1], cuts[2]

    def env(length, a, r):
        k = int(length * SR); e = np.ones(k); ka = max(1, int(a * SR)); kr = max(1, int(r * SR))
        e[:ka] = np.linspace(0, 1, ka); e[-kr:] *= np.linspace(1, 0, kr); return e

    def add(start, sig, gl=1.0, gr=1.0):
        i = int(start * SR); j = min(n, i + len(sig))
        if i >= n: return
        L[i:j] += sig[: j - i] * gl; R[i:j] += sig[: j - i] * gr

    def gain(tt):
        if tt < intro_end: return 0.0
        if tt < build_end: return 0.55
        if tt < DUR - 4: return 1.0
        return max(0.0, 1 - (tt - (DUR - 4)) / 3.5)

    rng = np.random.default_rng(7)
    for b in range(int(DUR / bar) + 1):
        t0 = b * bar; ch = prog[b % 4]; rt = roots[b % 4]
        tt = np.arange(int(bar * 1.15 * SR)) / SR
        pad = sum((np.sin(2 * np.pi * midi(m) * tt * (1 + d)) + .25 * np.sin(4 * np.pi * midi(m) * tt * (1 + d))) for m in ch for d in (-.003, .003)) / 16
        pad *= env(bar * 1.15, .6, .5) * (0.55 if t0 < intro_end else 0.4)
        add(t0, pad * min(1, t0 / 2 + .25) * max(0, 1 - max(0, t0 - (DUR - 4)) / 3.5), .9, 1.0)
        if gain(t0) <= 0: continue
        for k in range(4):
            bt = t0 + k * beat; g = gain(bt)
            if g <= 0: continue
            kt = np.arange(int(.35 * SR)) / SR; f = 50 + 90 * np.exp(-kt * 30)
            if bt >= build_end: add(bt, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kt * 9) * .5 * g)
            bl = beat * .9; btt = np.arange(int(bl * SR)) / SR
            add(bt, (np.sin(2 * np.pi * midi(rt - 12) * btt) + .3 * np.sin(4 * np.pi * midi(rt - 12) * btt)) * env(bl, .01, .25) * .22 * g)
            if bt >= build_end:
                h = rng.standard_normal(int(.06 * SR)); h = np.diff(h, prepend=0) * np.exp(-np.arange(len(h)) / SR * 70) * .05
                add(bt + beat / 2, h * g, .7, 1.0)
        for k in range(8):
            at = t0 + k * beat / 2; g = gain(at)
            if g <= 0: continue
            m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12; ptt = np.arange(int(.4 * SR)) / SR
            pl = (np.sin(2 * np.pi * midi(m) * ptt) + .35 * np.sin(4 * np.pi * midi(m) * ptt)) * np.exp(-ptt * 9) * .08
            pan = .6 + .4 * (k % 2); add(at, pl * g, pan, 1.6 - pan)
    for c in cuts[1:]:
        w = np.random.default_rng(int(c * 10)).standard_normal(int(.9 * SR))
        add(c - .85, np.convolve(w, np.ones(40) / 40, "same") * np.linspace(0, 1, len(w)) ** 2 * .3, 1.0, .8)
    ct = np.arange(int(2.5 * SR)) / SR
    add(cuts[-1] + .1, sum(np.sin(2 * np.pi * midi(m) * ct) for m in (72, 79, 84)) * np.exp(-ct * 1.6) * .07)
    mx = np.stack([L, R]); mx /= np.abs(mx).max() / .8
    return mx


def audio(tl, video, out):
    D = tl["dur"]; cuts = [s["start"] for s in tl["scenes"]]
    write_wav(HERE / f"music-{TAG}.wav", music(D, cuts))
    ins, fs = [], []
    for i, s in enumerate(tl["scenes"]):
        ins += ["-i", VO_DIR / s["voice"]]
        fs.append(f"[{i}:a]aresample={SR},adelay={int((s['start'] + LEAD) * 1000)}:all=1[v{i}]")
    k = len(tl["scenes"])
    fc = ";".join(fs) + ";" + "".join(f"[v{i}]" for i in range(k)) + f"amix=inputs={k}:normalize=0,pan=stereo|c0=c0|c1=c0," \
         f"highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,apad=whole_dur={D}[vo]"
    vo = HERE / f"voiceover-{TAG}.wav"
    run("ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", fc, "-map", "[vo]", "-t", D, "-ar", SR, vo)
    mfc = ("[0:a]lowpass=f=7000,aecho=0.8:0.5:60|110:0.25|0.15,volume=0.55[m];[1:a]asplit=2[vo][sc];"
           "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[duck];"
           "[duck][vo]amix=inputs=2:normalize=0:weights=1 1.15,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    mix = HERE / f"mix-{TAG}.wav"
    run("ffmpeg", "-loglevel", "error", "-y", "-i", HERE / f"music-{TAG}.wav", "-i", vo, "-filter_complex", mfc, "-map", "[out]", "-ar", SR, "-t", D, mix)
    run("ffmpeg", "-loglevel", "error", "-y", "-i", video, "-i", mix, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", out)


def main():
    tl = voice_and_timeline() if STAGE == "all" else load_timeline()
    if os.environ.get("STILLS"):
        asyncio.run(render(None, os.environ["STILLS"].split(","))); return
    silent = HERE / f".{NAME}-rendering.mp4"  # hidden in Finder until the final video is written
    if STAGE in ("all", "video"):
        print("video..."); asyncio.run(render(silent))
    print("audio..."); audio(tl, silent, HERE / f"{NAME}.mp4")
    print("wrote", HERE / f"{NAME}.mp4")


if __name__ == "__main__":
    main()
