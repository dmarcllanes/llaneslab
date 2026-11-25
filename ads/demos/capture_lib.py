"""Shared helpers: drive a real app with Playwright and save phone screenshots + tap positions."""
import json
from pathlib import Path

VIEW = {"width": 390, "height": 844}


class Cap:
    def __init__(self, out: Path):
        self.out = out; out.mkdir(parents=True, exist_ok=True)
        self.shots = {}

    async def ctx(self, browser):
        return await browser.new_context(viewport=VIEW, device_scale_factor=2, is_mobile=True, has_touch=True, reduced_motion="reduce")

    async def shot(self, pg, name, tap=None, scroll=None, wait=500):
        """Save a viewport screenshot. `scroll`: selector to bring into view first.
        `tap`: selector whose centre is recorded as the tap point (and then clicked by the caller)."""
        if scroll:
            await pg.locator(scroll).first.scroll_into_view_if_needed()
            await pg.locator(scroll).first.evaluate("e => e.scrollIntoView({block: 'center'})")
        if tap:
            el = pg.locator(tap).first
            await el.scroll_into_view_if_needed()
            await el.evaluate("e => e.scrollIntoView({block: 'center'})")
        await pg.wait_for_timeout(wait)
        rec = {"src": f"shots/{name}.png"}
        if tap:
            bb = await pg.locator(tap).first.bounding_box()
            rec["tap"] = [round(bb["x"] + bb["width"] / 2), round(bb["y"] + bb["height"] / 2)]
        await pg.screenshot(path=str(self.out / f"{name}.png"))
        self.shots[name] = rec
        print("  shot", name, rec.get("tap", ""))
        return rec

    def save(self):
        (self.out.parent / "shots.json").write_text(json.dumps(self.shots, indent=1))


PROOF_HTML = """<!doctype html><html><body style="margin:0;width:390px;height:700px;background:#EEF2F7;font-family:-apple-system,Helvetica,sans-serif;display:flex;align-items:center;justify-content:center">
<div style="width:330px;background:#fff;border-radius:22px;padding:30px 24px;text-align:center;box-shadow:0 10px 30px rgba(0,0,0,.08)">
<div style="width:64px;height:64px;border-radius:50%;background:#10B981;color:#fff;font-size:38px;line-height:64px;margin:0 auto">&#10003;</div>
<div style="font-size:15px;color:#64748B;margin-top:16px">Payment sent</div>
<div style="font-size:40px;font-weight:800;color:#0F172A;margin-top:6px">{amount}</div>
<div style="font-size:15px;color:#334155;margin-top:18px;line-height:1.7">To: {to}<br>Note: {note}<br>{when}</div>
<div style="margin-top:22px;font-size:12px;letter-spacing:.2em;color:#94A3B8">SAMPLE &middot; DEMO ONLY</div></div></body></html>"""


async def make_proof(browser, path, amount, to, note, when="Nov 25, 2026 · 8:40 PM"):
    """A plain, clearly-labelled sample payment screenshot (not styled after any real wallet app)."""
    pg = await browser.new_page(viewport={"width": 390, "height": 700})
    await pg.set_content(PROOF_HTML.format(amount=amount, to=to, note=note, when=when))
    await pg.screenshot(path=str(path)); await pg.close()
    return path


async def wait_reply(pg, min_growth=60, timeout=60):
    """Wait until the page text has grown and then stayed the same for ~3 s (an AI reply finished streaming in)."""
    start = len(await pg.inner_text("body")); prev, stable = "", 0
    for _ in range(timeout):
        await pg.wait_for_timeout(1000)
        txt = await pg.inner_text("body")
        stable = stable + 1 if txt == prev else 0; prev = txt
        if stable >= 3 and len(txt) - start >= min_growth:
            return txt
    return prev
