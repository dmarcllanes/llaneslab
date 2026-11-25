"""Build a product demo video: voiceover -> timeline -> video frames -> music -> final MP4.

Usage (from ads/demos, after capturing the app's screens with <app>/capture.py):
    uv run --with numpy --with kokoro-onnx --with soundfile --with playwright python build.py shop
Options (env): VOICE=af_heart  SPEED=1.0  KOKORO_DIR=../flow-trio/audio/models  STAGE=all|timeline|video|audio
  LAYOUT=vertical|landscape   SCRIPT=script-60s.json TAG=60s TARGET=60  (short cut padded to exactly TARGET seconds)
Output: <app>/<app>-demo-vertical.mp4
"""
import asyncio, json, os, subprocess, sys, tempfile, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 44100
FPS = 30
VOICE = os.environ.get("VOICE", "af_heart")
SPEED = float(os.environ.get("SPEED", "1.0"))
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", HERE.parent / "flow-trio" / "audio" / "models"))
LEAD, TAIL = 0.45, 0.85          # silence before / after each voice line inside its step
LAYOUT = os.environ.get("LAYOUT", "vertical")
TAG = os.environ.get("TAG", "")
TARGET = float(os.environ.get("TARGET", "0"))
EXPLAIN_MIN = float(os.environ.get("EXPLAIN_MIN", "8.0"))
SFX = f"-{TAG}" if TAG else ""


def run(*a):
    subprocess.run([str(x) for x in a], check=True)


def wav_dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


# ------------------------------------------------------------------ voice + timeline
def make_voice(app_dir, script, tmp):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    kk = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.int8.onnx"), str(KOKORO_DIR / "voices-v1.0.bin"))
    vo_dir = app_dir / f"voice{SFX}"; vo_dir.mkdir(exist_ok=True)
    t = 0.0
    for i, s in enumerate(script["steps"]):
        raw = tmp / f"{i:02d}-raw.wav"; out = vo_dir / f"{i:02d}.wav"
        audio, sr = kk.create(s.get("say", s["text"]), voice=VOICE, speed=SPEED, lang="en-us")
        sf.write(str(raw), audio, sr)
        run("ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af",
            "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse",
            "-ar", SR, out)
        d = wav_dur(out)
        n_frames = len(s.get("frames", [])) or 1
        min_d = {"intro": 4.5, "outro": 7.0, "explain": EXPLAIN_MIN}.get(s.get("type"), 2.4 * n_frames)
        s["voice"] = f"voice{SFX}/{i:02d}.wav"; s["voice_len"] = round(d, 3)
        s["start"] = round(t, 3); s["dur"] = round(max(min_d, LEAD + d + TAIL), 3)
        t += s["dur"]
        print(f"  {i:02d} {s['start']:6.2f}s +{s['dur']:5.2f}s  voice {d:4.1f}s  {s.get('title', s.get('type'))}")
    print(f"  total {t:.1f}s")
    if TARGET:   # pad every step evenly so the video is exactly TARGET seconds
        steps = script["steps"]; extra = TARGET - t
        if extra < 0:
            sys.exit(f"Script runs {t:.1f}s, over the {TARGET:.0f}s target: shorten some lines.")
        t = 0.0
        for s in steps:
            s["dur"] = round(s["dur"] + extra / len(steps), 3); s["start"] = round(t, 3); t += s["dur"]
        steps[-1]["dur"] = round(TARGET - steps[-1]["start"], 3); t = TARGET
        print(f"  padded +{extra:.1f}s -> exactly {TARGET:.1f}s")
    return t


def write_timeline(app_dir, script):
    shots = json.loads((app_dir / "shots.json").read_text())
    for s in script["steps"]:
        for f in s.get("frames", []):
            assert f in shots, f"frame {f!r} not captured"
    data = dict(script, shots=shots)
    (app_dir / f"timeline{SFX}.js").write_text("window.DEMO = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n")


# ------------------------------------------------------------------ video
async def render_video(app, dest):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--allow-file-access-from-files"])
        w, h = (1920, 1080) if LAYOUT == "landscape" else (1080, 1920)
        pg = await b.new_page(viewport={"width": w, "height": h})
        await pg.goto((HERE / "demo.html").as_uri() + f"?app={app}&layout={LAYOUT}&tl=timeline{SFX}.js&render=1", wait_until="networkidle")
        await pg.evaluate("document.fonts.ready")
        dur = await pg.evaluate("DUR")
        ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                               "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", str(dest)], stdin=subprocess.PIPE)
        n = int(dur * FPS)
        for i in range(n):
            await pg.evaluate(f"seek({i / FPS})")
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=93))
            if i % 300 == 0: print(f"  frame {i}/{n}", flush=True)
        ff.stdin.close(); ff.wait(); await b.close()


# ------------------------------------------------------------------ music (original, generated; calmer than the ad)
def music(dur, cuts):
    n = int(dur * SR); L = np.zeros(n); R = np.zeros(n)
    bpm = 96; beat = 60 / bpm; bar = beat * 4
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    prog = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 67]]   # Cmaj7 Am7 Fmaj7 G
    roots = [48, 45, 41, 43]

    def env(length, a, r):
        k = int(length * SR); e = np.ones(k); ka = max(1, int(a * SR)); kr = max(1, int(r * SR))
        e[:ka] = np.linspace(0, 1, ka); e[-kr:] *= np.linspace(1, 0, kr); return e

    def add(start, sig, gl=1.0, gr=1.0):
        i = int(start * SR); j = min(n, i + len(sig))
        if i >= n or j <= i: return
        L[i:j] += sig[: j - i] * gl; R[i:j] += sig[: j - i] * gr

    gain = lambda tt: min(1.0, tt / 3 + .3) * max(0.0, min(1.0, (dur - tt) / 3.0))
    for b in range(int(dur / bar) + 1):
        t0 = b * bar; ch = prog[b % 4]; rt = roots[b % 4]; g = gain(t0)
        if g <= 0: continue
        tt = np.arange(int(bar * 1.15 * SR)) / SR
        pad = sum(np.sin(2 * np.pi * midi(m) * tt * (1 + d)) + .2 * np.sin(4 * np.pi * midi(m) * tt * (1 + d)) for m in ch for d in (-.003, .003)) / 16
        add(t0, pad * env(bar * 1.15, .7, .6) * .42 * g, .9, 1.0)
        for k in range(4):
            bt = t0 + k * beat; gb = gain(bt)
            kt = np.arange(int(.3 * SR)) / SR
            kick = np.sin(2 * np.pi * np.cumsum(50 + 80 * np.exp(-kt * 30)) / SR) * np.exp(-kt * 10) * .38
            if k in (0, 2): add(bt, kick * gb)
            bl = beat * .9; btt = np.arange(int(bl * SR)) / SR
            add(bt, (np.sin(2 * np.pi * midi(rt - 12) * btt)) * env(bl, .01, .3) * .18 * gb)
            hat = np.random.default_rng(b * 4 + k).standard_normal(int(.05 * SR))
            add(bt + beat / 2, np.diff(hat, prepend=0) * np.exp(-np.arange(len(hat)) / SR * 80) * .03 * gb, .7, 1.0)
        for k in range(8):
            at = t0 + k * beat / 2; m = ch[[0, 2, 1, 3, 2, 1, 3, 2][k]] + 12
            ptt = np.arange(int(.45 * SR)) / SR
            pl = (np.sin(2 * np.pi * midi(m) * ptt) + .3 * np.sin(4 * np.pi * midi(m) * ptt)) * np.exp(-ptt * 8) * .06 * gain(at)
            pan = .6 + .4 * (k % 2); add(at, pl, pan, 1.6 - pan)
    for c in cuts:   # soft swoosh into each step
        w = np.random.default_rng(int(c * 10)).standard_normal(int(.6 * SR))
        w = np.convolve(w, np.ones(60) / 60, "same") * np.linspace(0, 1, len(w)) ** 2 * .18
        add(c - .55, w, 1.0, .8)
    mx = np.stack([L, R]); mx /= np.abs(mx).max() / .8
    return mx


def write_wav(path, x):
    st = (np.clip(np.stack([x[0], x[1]], 1), -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())


def build_audio(app_dir, script, dur, video, dest):
    write_wav(app_dir / "music.wav", music(dur, [s["start"] for s in script["steps"][1:]]))
    inputs, filters = [], []
    for i, s in enumerate(script["steps"]):
        inputs += ["-i", app_dir / s["voice"]]
        filters.append(f"[{i}:a]adelay={int((s['start'] + LEAD) * 1000)}:all=1[v{i}]")
    k = len(script["steps"])
    fc = ";".join(filters) + ";" + "".join(f"[v{i}]" for i in range(k)) + \
         f"amix=inputs={k}:normalize=0,pan=stereo|c0=c0|c1=c0,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,apad=whole_dur={dur}[vo]"
    run("ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[vo]", "-t", dur, "-ar", SR, app_dir / "voiceover.wav")
    fc = ("[0:a]lowpass=f=6500,aecho=0.8:0.5:60|110:0.25|0.15,volume=0.5[m];[1:a]asplit=2[vo][sc];"
          "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck];"
          "[duck][vo]amix=inputs=2:normalize=0:weights=1 1.15,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    run("ffmpeg", "-loglevel", "error", "-y", "-i", app_dir / "music.wav", "-i", app_dir / "voiceover.wav", "-filter_complex", fc,
        "-map", "[out]", "-ar", SR, "-t", dur, app_dir / "mix.wav")
    run("ffmpeg", "-loglevel", "error", "-y", "-i", video, "-i", app_dir / "mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dest)
    for f in ("music.wav", "voiceover.wav", "mix.wav"):   # large intermediates; rebuilt on every run
        (app_dir / f).unlink(missing_ok=True)


def main():
    app = sys.argv[1]; stage = os.environ.get("STAGE", "all")
    app_dir = HERE / app
    script = json.loads((app_dir / os.environ.get("SCRIPT", "script.json")).read_text())
    tl = app_dir / f"timeline{SFX}.json"
    if stage in ("all", "timeline") or not tl.exists():
        print("voice + timeline...")
        with tempfile.TemporaryDirectory() as td: make_voice(app_dir, script, Path(td))
        tl.write_text(json.dumps(script, ensure_ascii=False, indent=1))
    script = json.loads(tl.read_text())
    write_timeline(app_dir, script)
    dur = script["steps"][-1]["start"] + script["steps"][-1]["dur"]
    silent = app_dir / f"{app}-demo-{LAYOUT}{SFX}-silent.mp4"
    if stage in ("all", "video"):
        print("video..."); asyncio.run(render_video(app, silent))
    if stage in ("all", "audio", "video"):
        print("audio + mux...")
        dest = app_dir / f"{app}-demo-{LAYOUT}{SFX}.mp4"
        build_audio(app_dir, script, dur, silent, dest)
        silent.unlink(missing_ok=True)
        print("wrote", dest)


if __name__ == "__main__":
    main()
