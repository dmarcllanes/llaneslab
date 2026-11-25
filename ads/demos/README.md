# Product demo videos (ShopFlow, ServeFlow, StayFlow)

One vertical (1080×1920) how-it-works video per app, with a female voiceover (Kokoro `af_heart`) and an original music bed.

| App | Folder | Video |
| :--- | :--- | :--- |
| ShopFlow | `shop/` | `shop/shop-demo-vertical.mp4` |
| ServeFlow | `serve/` | `serve/serve-demo-vertical.mp4` |
| StayFlow | `stay/` | `stay/stay-demo-vertical.mp4` |

## How it is made

1. `<app>/capture.py` drives the **real app** (running locally on a copy of its demo data) with Playwright and saves phone screenshots plus tap positions to `<app>/shots/`.
2. `<app>/script.json` is the storyboard: one entry per step with the on-screen title, the subtitle (`text`), the spoken line (`say`, spelled for the voice, e.g. "G Cash", "Q R") and the screens (`frames`).
   - `"type": "explain"` steps are animated "How the AI works" scenes. They illustrate the AI features without a live AI call.
3. `build.py <app>` voices each step, times the video to the voice, renders `demo.html?app=<app>` frame by frame, generates the music, mixes and muxes.

```sh
cd ads/demos
uv run --with numpy --with kokoro-onnx --with soundfile --with playwright python build.py shop
# STAGE=video  re-render with the existing voice timing;  VOICE=am_michael  for the male voice
```

The voice model lives in `../flow-trio/audio/models/` (not committed).

## Running the apps for a capture

Always run on a **copy** of the data (`DATA_DIR=<scratch folder>`), never the real `data/` folder.

| App | Start (from the app's folder) | Capture env |
| :--- | :--- | :--- |
| ShopFlow | `DATA_DIR=… PORT=5101 RELOAD=0 DEV_STORE=demo-store ADMIN_PASSWORD=… uv run python main.py` | `SHOP_ADMIN_PASSWORD` |
| ServeFlow | `BASE_DOMAIN=serveflow.example LLM_API_KEY= DATA_DIR=… PORT=5102 uv run python main.py` | `HOST_RULES="MAP demo-resto.serveflow.example 127.0.0.1:5102" SERVE_URL=http://demo-resto.serveflow.example SKIP_AI=1` |
| StayFlow | seed first: `DATA_DIR=… STAYFLOW_ADMIN_PASSWORD=… uv run python seed_client.py seeds/demo.json`, then `BASE_DOMAIN=stayflow.example DATA_DIR=… PORT=5103 DEFAULT_TENANT=demo ADMIN_PASSWORD=… LLM_API_KEY= uv run python main.py` | `HOST_RULES="MAP demo.stayflow.example 127.0.0.1:5103" STAY_URL=http://demo.stayflow.example` |

Notes:
- ServeFlow: in the data copy, widen the opening hours if capturing at night, or checkout shows "We're closed right now".
- `HOST_RULES` keeps `localhost` addresses off the screen.
- `LLM_API_KEY=` (empty) turns the app's AI off, so a capture makes no AI calls. ShopFlow's capture uses its live AI chat and co-pilot. Expect a few calls, and avoid repeat runs on a free-tier key.
- The sample payment screenshots are plain images labelled "SAMPLE · DEMO ONLY" and are not styled after any real wallet app.
