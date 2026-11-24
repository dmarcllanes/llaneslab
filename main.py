"""FastHTML server for the Dan Marc Llanes portfolio.

- `/`           serves the single-file portfolio (index.html stays portable / zero-build).
- `/api/audit`  stores Free Audit requests.
- `/api/beta`   stores app beta invite requests.
- `/api/chat`   "Ask about Dan" chatbot, powered by Claude and grounded in chat_knowledge.py.
                Needs ANTHROPIC_API_KEY. Without it the endpoint answers 503 + fallback, and the
                page switches to its built-in offline FAQ answers.

Submissions are appended to data/*.jsonl (git-ignored). If the page is opened
without this server, the front end falls back to `mailto:` automatically.

Run:  uv run python main.py   →  http://localhost:5001
"""

import json
import os
import re
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

import anthropic

from fasthtml.common import fast_app, serve
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse

from chat_knowledge import SYSTEM_PROMPT

ROOT = Path(__file__).parent
DATA = ROOT / "data"
INDEX = ROOT / "index.html"

# On Vercel the project folder is read-only and each function instance is temporary,
# so the session key comes from an env var (or /tmp) and form submissions are not stored on disk.
ON_VERCEL = bool(os.environ.get("VERCEL"))

# static_path points at public/ so project files (CLAUDE.md, data/, etc.) are never served.
# Plain `app = ...` (not tuple unpacking) so Vercel's FastHTML preset can find the entry point.
app = fast_app(
    static_path=str(ROOT / "public"),
    pico=False,
    secret_key=os.environ.get("SESSION_SECRET"),
    key_fname="/tmp/.sesskey" if ON_VERCEL else ".sesskey",
)[0]
rt = app.route

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
APPS = {"Kalamooo", "Folingoo", "Roostart", "Owolot", "Otaroo"}
INDUSTRIES = {
    "Retail Shop / Small Business",
    "Hotel, Resort or Short-Term Rental",
    "Clinic / Healthcare Practice",
    "Other",
}


def _clean(data: dict, key: str, limit: int = 200) -> str:
    return str(data.get(key) or "").strip()[:limit]


def _save(kind: str, record: dict) -> bool:
    """Append a submission to data/<kind>.jsonl. Returns False where disk storage isn't possible
    (e.g. Vercel); the page then opens a pre-filled email to Dan instead, so nothing is lost."""
    if ON_VERCEL:
        return False
    DATA.mkdir(exist_ok=True)
    record["received_at"] = datetime.now(timezone.utc).isoformat()
    with (DATA / f"{kind}.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return True


async def _json(req: Request) -> dict | None:
    try:
        data = await req.json()
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _bad(msg: str) -> JSONResponse:
    return JSONResponse({"ok": False, "error": msg}, status_code=400)


@rt("/")
def get():
    return FileResponse(INDEX, media_type="text/html")


@rt("/api/audit", methods=["post"])
async def audit(req: Request):
    data = await _json(req)
    if data is None:
        return _bad("Invalid request.")
    if _clean(data, "website"):  # honeypot field: bots fill it, people never see it
        return JSONResponse({"ok": True})
    rec = {
        "name": _clean(data, "name", 120),
        "email": _clean(data, "email", 200),
        "industry": _clean(data, "industry", 80),
        "problem": _clean(data, "problem", 200),
        "message": _clean(data, "message", 4000),
    }
    if not rec["name"] or not EMAIL_RE.match(rec["email"]):
        return _bad("Please add your name and a valid email.")
    if rec["industry"] not in INDUSTRIES:
        rec["industry"] = "Other"
    if not _save("audit", rec):
        return _fallback()
    return JSONResponse({"ok": True})


@rt("/api/beta", methods=["post"])
async def beta(req: Request):
    data = await _json(req)
    if data is None:
        return _bad("Invalid request.")
    rec = {
        "app": _clean(data, "app", 40),
        "platform": _clean(data, "platform", 20),
        "name": _clean(data, "name", 120),
        "email": _clean(data, "email", 200),
    }
    if rec["app"] not in APPS or rec["platform"] not in {"iOS", "Android"}:
        return _bad("Unknown app or platform.")
    if not EMAIL_RE.match(rec["email"]):
        return _bad("Please add the email linked to your store account.")
    if not _save("beta", rec):
        return _fallback()
    return JSONResponse({"ok": True})


# ---------------------------------------------------------------- chatbot
CHAT_MODEL = "claude-opus-5-5"
CHAT_MAX_TURNS = 12          # only the most recent messages are sent
CHAT_MAX_CHARS = 800         # per visitor message
CHAT_LIMIT = (20, 600)       # 20 messages per visitor per 10 minutes
_chat_hits: dict[str, deque] = defaultdict(deque)
_chat_client: anthropic.AsyncAnthropic | None = None


def _fallback(status: int = 503) -> JSONResponse:
    """Tell the page to answer from its built-in offline FAQ instead."""
    return JSONResponse({"ok": False, "fallback": True}, status_code=status)


def _rate_limited(req: Request) -> bool:
    ip = req.headers.get("x-forwarded-for", "").split(",")[0].strip() or (req.client.host if req.client else "?")
    now, (limit, window) = time.monotonic(), CHAT_LIMIT
    hits = _chat_hits[ip]
    while hits and now - hits[0] > window:
        hits.popleft()
    if len(hits) >= limit:
        return True
    hits.append(now)
    return False


def _clean_history(data: dict) -> list[dict] | None:
    msgs = data.get("messages")
    if not isinstance(msgs, list) or not msgs:
        return None
    out = []
    for m in msgs[-CHAT_MAX_TURNS:]:
        if not isinstance(m, dict) or m.get("role") not in ("user", "assistant"):
            return None
        text = str(m.get("content") or "").strip()[:CHAT_MAX_CHARS * 3]
        if text:
            out.append({"role": m["role"], "content": text})
    while out and out[0]["role"] != "user":   # history must start with the visitor
        out.pop(0)
    if not out or out[-1]["role"] != "user" or len(out[-1]["content"]) > CHAT_MAX_CHARS:
        return None
    return out


@rt("/api/chat", methods=["post"])
async def chat(req: Request):
    global _chat_client
    data = await _json(req)
    msgs = _clean_history(data) if data else None
    if msgs is None:
        return _bad(f"Please send a question under {CHAT_MAX_CHARS} characters.")
    if _rate_limited(req):
        return JSONResponse({"ok": False, "error": "You've sent a lot of questions. Please wait a few minutes, or email dandigital1688@gmail.com."}, status_code=429)
    try:
        _chat_client = _chat_client or anthropic.AsyncAnthropic()
        resp = await _chat_client.beta.messages.create(
            model=CHAT_MODEL,
            max_tokens=4000,
            output_config={"effort": "low"},  # short, factual chat replies
            # If Claude declines a request, the API retries it on a fallback model in the same call.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=msgs,
        )
    except (anthropic.AuthenticationError, anthropic.PermissionDeniedError):
        return _fallback()                      # no or invalid API key: use the offline FAQ
    except anthropic.RateLimitError:
        return _fallback()
    except anthropic.APIStatusError as e:
        print(f"[chat] API error {e.status_code}: {e.message}")
        return _fallback()
    except anthropic.APIConnectionError:
        return _fallback()
    except anthropic.AnthropicError as e:
        print(f"[chat] client error: {e}")
        return _fallback()
    except TypeError as e:                      # SDK raises this when no credentials are configured
        if "authentication" not in str(e):
            raise
        return _fallback()
    if resp.stop_reason == "refusal":
        return JSONResponse({"ok": True, "reply": "I can only help with questions about Dan's work, services and apps. What would you like to know?"})
    reply = "".join(b.text for b in resp.content if b.type == "text").strip()
    if not reply:
        return _fallback()
    return JSONResponse({"ok": True, "reply": reply})


if __name__ == "__main__":
    serve()
