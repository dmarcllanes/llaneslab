# Dan Marc Llanes — Portfolio

Single-file site (`index.html`) served by a small FastHTML app (`main.py`).

```bash
uv sync
uv run python main.py   # http://localhost:5001
```

- `POST /api/audit` and `POST /api/beta` store form submissions in `data/*.jsonl` (git-ignored).
- `index.html` still works on its own (static hosting / opened as a file): forms fall back to `mailto:`.
- `POST /api/chat` powers the "Ask about Dan" chatbot with Claude (`claude-opus-5-5`, low effort), grounded only in `chat_knowledge.py`.

## Chatbot setup

```bash
export ANTHROPIC_API_KEY=sk-ant-...   # get one at https://platform.claude.com
uv run python main.py
```

- Without a key (or when the page is opened as a file / on static hosting), the chat widget answers from its built-in offline FAQ instead. Nothing breaks.
- Limits: 20 questions per visitor per 10 minutes, 800 characters per question, last 12 messages sent.
- When facts change (app status, services, contact), update `chat_knowledge.py` **and** the offline `FAQ` in `index.html`.

## Deploy on Vercel

The site runs on Vercel as one Python function: `api/index.py` loads the FastHTML app from
`main.py`, and `vercel.json` sends every path to it.

```bash
npx vercel login          # once
npx vercel                # preview deploy (first run links the project)
npx vercel --prod         # production deploy
```

Environment variables (Vercel → Project → Settings → Environment Variables):

- `ANTHROPIC_API_KEY`: turns on live chatbot answers. Without it the chat uses the offline FAQ.
- `SESSION_SECRET` (optional): any long random string, for stable sessions across instances.

On Vercel, audit and beta form submissions are **not stored on disk** (the server's disk is
temporary). The page opens a pre-filled email to dandigital1688@gmail.com instead. If you add or
change Python packages, refresh `requirements.txt` with:
`uv export --no-hashes --no-dev --no-emit-project --format requirements-txt -o requirements.txt`.
