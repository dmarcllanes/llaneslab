"""Build voiceover + original music bed for the apps-launch ad and mux them into the video.

Usage (from ads/flow-trio/audio):
    uv run --with numpy --with kokoro-onnx --with soundfile python build_audio.py      # Kokoro voice af_heart
    VOICE=am_michael uv run ... python build_audio.py      # another Kokoro voice (af_bella, bm_george, ...)
    TTS=say VOICE=Samantha uv run ... python build_audio.py  # built-in macOS voice instead
  Kokoro model files: KOKORO_DIR (default ./models) must hold kokoro-v1.0.int8.onnx and voices-v1.0.bin
  from https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0).
    VO_DIR=my_takes uv run --with numpy python build_audio.py # use recorded lines 01.wav, 02.wav ... instead of TTS

Outputs: music.wav, voiceover.wav, mix.wav, and ../flow-trio-vertical-audio.mp4
"""
import os, subprocess, tempfile, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 44100
DUR = 42.0
TTS = os.environ.get("TTS", "kokoro")
VOICE = os.environ.get("VOICE", "af_heart" if TTS == "kokoro" else "Samantha")
KOKORO_DIR = Path(os.environ.get("KOKORO_DIR", HERE / "models"))
SPEED = float(os.environ.get("SPEED", "1.05"))
RATE = os.environ.get("RATE", "185")
VIDEO = HERE.parent / "apps-launch-vertical.mp4"
OUT = HERE.parent / "apps-launch-vertical-audio.mp4"


def run(*a):
    subprocess.run(a, check=True)


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    st = (np.stack([x[0], x[1]], 1) * 32767).astype("<i2") if x.ndim == 2 else (x * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2 if x.ndim == 2 else 1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())


# ---------------------------------------------------------------- music (original, generated)
def music():
    n = int(DUR * SR); t = np.arange(n) / SR
    L = np.zeros(n); R = np.zeros(n)
    bpm = 110; beat = 60 / bpm; bar = beat * 4
    midi = lambda m: 440 * 2 ** ((m - 69) / 12)
    # A minor -> F -> C -> G   (one chord per bar)
    prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]
    roots = [45, 41, 48, 43]

    def env(length, a, r):
        k = int(length * SR); e = np.ones(k)
        ka = max(1, int(a * SR)); kr = max(1, int(r * SR))
        e[:ka] = np.linspace(0, 1, ka); e[-kr:] *= np.linspace(1, 0, kr)
        return e

    def add(start, sig, gl=1.0, gr=1.0):
        i = int(start * SR); j = min(n, i + len(sig))
        if i >= n: return
        L[i:j] += sig[: j - i] * gl; R[i:j] += sig[: j - i] * gr

    def section_gain(tt):  # arrangement: intro pad, build, full, outro
        if tt < 5.4: return 0.0
        if tt < 9.4: return 0.55
        if tt < DUR - 3.5: return 1.0
        return max(0.0, 1 - (tt - (DUR - 3.5)) / 3.0)

    nbars = int(DUR / bar) + 1
    for b in range(nbars):
        t0 = b * bar; ch = prog[b % 4]; rt = roots[b % 4]
        # pad: soft detuned sines with gentle harmonics, slow attack
        tt = np.arange(int(bar * 1.15 * SR)) / SR
        pad = sum((np.sin(2 * np.pi * midi(m) * tt * (1 + d)) + .25 * np.sin(4 * np.pi * midi(m) * tt * (1 + d)))
                  for m in ch for d in (-.003, .003)) / 16
        pad *= env(bar * 1.15, .6, .5) * (0.55 if t0 < 5.4 else 0.4)
        fade_in = min(1, t0 / 2 + .25); out = max(0, 1 - max(0, t0 - (DUR - 3.5)) / 3.0)
        add(t0, pad * fade_in * out, .9, 1.0)
        g = section_gain(t0)
        if g <= 0: continue
        for k in range(4):  # beats
            bt = t0 + k * beat; gb = section_gain(bt)
            if gb <= 0: continue
            # kick: sine sweep
            kl = .35; kt = np.arange(int(kl * SR)) / SR
            f = 50 + 90 * np.exp(-kt * 30)
            kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-kt * 9) * .55
            if t0 >= 9.4: add(bt, kick * gb)
            # bass: root note pulse on each beat
            bl = beat * .9; btt = np.arange(int(bl * SR)) / SR
            bass = (np.sin(2 * np.pi * midi(rt - 12) * btt) + .3 * np.sin(4 * np.pi * midi(rt - 12) * btt)) * env(bl, .01, .25) * .22
            add(bt, bass * gb)
            # hat on off-beats (noise burst)
            if t0 >= 9.4:
                hl = .06; hat = np.random.default_rng(b * 4 + k).standard_normal(int(hl * SR))
                hat = np.diff(hat, prepend=0) * np.exp(-np.arange(len(hat)) / SR * 70) * .05
                add(bt + beat / 2, hat * gb, .7, 1.0)
        # arpeggio pluck (8th notes) from the build onward
        for k in range(8):
            at = t0 + k * beat / 2; ga = section_gain(at)
            if ga <= 0: continue
            m = ch[[0, 1, 2, 3, 2, 1, 3, 2][k]] + 12
            pl = .4; ptt = np.arange(int(pl * SR)) / SR
            pluck = (np.sin(2 * np.pi * midi(m) * ptt) + .35 * np.sin(4 * np.pi * midi(m) * ptt)) * np.exp(-ptt * 9) * .09
            pan = .6 + .4 * (k % 2)
            add(at, pluck * ga, pan, 1.6 - pan)
    # whoosh swells into each scene cut
    for c in (5.6, 15.4, 26.2, 35.2):
        wl = .9; w = np.random.default_rng(int(c * 10)).standard_normal(int(wl * SR))
        w = np.convolve(w, np.ones(40) / 40, "same") * np.linspace(0, 1, len(w)) ** 2 * .35
        add(c - wl + .05, w, 1.0, .8)
    # soft final chime
    ct = np.arange(int(2.5 * SR)) / SR
    chime = sum(np.sin(2 * np.pi * midi(m) * ct) for m in (69, 76, 81)) * np.exp(-ct * 1.6) * .08
    add(35.3, chime)
    mx = np.stack([L, R]); mx /= np.abs(mx).max() / .8
    return mx


# ---------------------------------------------------------------- voiceover
def voiceover(tmp):
    lines = []
    for raw in (HERE / "voiceover.txt").read_text().splitlines():
        if not raw.strip() or raw.startswith("#"): continue
        s, m, text = [x.strip() for x in raw.split("|", 2)]
        lines.append((float(s), float(m), text))
    vo_dir = os.environ.get("VO_DIR")
    if not vo_dir and TTS == "kokoro":
        import soundfile as sf
        from kokoro_onnx import Kokoro
        kk = Kokoro(str(KOKORO_DIR / "kokoro-v1.0.int8.onnx"), str(KOKORO_DIR / "voices-v1.0.bin"))
    inputs, filters = [], []
    for i, (start, maxd, text) in enumerate(lines, 1):
        if vo_dir:
            src = Path(vo_dir) / f"{i:02d}.wav"
        elif TTS == "kokoro":
            src = tmp / f"{i:02d}.wav"
            audio, sr = kk.create(text, voice=VOICE, speed=SPEED, lang="en-us")
            sf.write(str(src), audio, sr)
            run("ffmpeg", "-loglevel", "error", "-y", "-i", str(src), "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse", str(src) + ".t.wav")
            os.replace(str(src) + ".t.wav", src)
        else:
            src = tmp / f"{i:02d}.aiff"
            run("say", "-v", VOICE, "-r", RATE, "-o", str(src), text)
        d = dur(src); tempo = max(1.0, d / maxd)
        if tempo > 1.25: print(f"  ! line {i} is {d:.1f}s for a {maxd}s slot; shorten the text")
        tempo = min(tempo, 1.25)
        print(f"  {i:02d} @ {start:5.1f}s  {d:4.1f}s{'  x%.2f' % tempo if tempo > 1 else ''}  {text}")
        inputs += ["-i", str(src)]
        filters.append(f"[{i-1}:a]aresample={SR},atempo={tempo:.3f},adelay={int(start*1000)}:all=1[v{i}]")
    mix = "".join(f"[v{i}]" for i in range(1, len(lines) + 1))
    fc = ";".join(filters) + f";{mix}amix=inputs={len(lines)}:normalize=0,pan=stereo|c0=c0|c1=c0," \
         f"highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,apad=whole_dur={DUR}[vo]"
    run("ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[vo]", "-t", str(DUR), "-ar", str(SR), str(HERE / "voiceover.wav"))


def main():
    print("music..."); write_wav(HERE / "music.wav", music())
    print(f"voiceover ({os.environ.get('VO_DIR') or VOICE})...")
    with tempfile.TemporaryDirectory() as td: voiceover(Path(td))
    # music: light reverb + low-pass, ducked under the voice; then loudness-normalise for social (~ -14 LUFS)
    fc = ("[0:a]lowpass=f=7000,aecho=0.8:0.5:60|110:0.25|0.15,volume=0.55[m];"
          "[1:a]asplit=2[vo][sc];"
          "[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=350[duck];"
          "[duck][vo]amix=inputs=2:normalize=0:weights=1 1.15,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    run("ffmpeg", "-loglevel", "error", "-y", "-i", str(HERE / "music.wav"), "-i", str(HERE / "voiceover.wav"),
        "-filter_complex", fc, "-map", "[out]", "-ar", str(SR), "-t", str(DUR), str(HERE / "mix.wav"))
    run("ffmpeg", "-loglevel", "error", "-y", "-i", str(VIDEO), "-i", str(HERE / "mix.wav"), "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(OUT))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
