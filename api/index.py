"""Vercel entry point: exposes the FastHTML app from main.py as a Python serverless function.

vercel.json rewrites every path to this function, so `/`, `/api/chat`, `/api/audit`,
`/api/beta` and `/favicon.ico` all behave exactly as they do locally.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import app  # noqa: E402,F401
