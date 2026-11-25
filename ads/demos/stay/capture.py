"""Capture the StayFlow demo screens from a running demo property (Casa Alon Transient House).
Run the app first (see ../README.md), then:  uv run --with playwright python capture.py"""
import asyncio, os, sys
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from capture_lib import Cap

B = os.environ.get("STAY_URL", "http://localhost:5103")
PW = os.environ.get("STAY_ADMIN_PASSWORD", "ad-capture-pass")
HERE = Path(__file__).resolve().parent
CHECK_IN, CHECK_OUT = os.environ.get("STAY_IN", "2026-11-28"), os.environ.get("STAY_OUT", "2026-11-29")


async def request(c, pg, name, phone, shot_prefix=None):
    await pg.goto(B + "/book?room_id=1", wait_until="networkidle")
    await pg.fill("input[name=check_in]", CHECK_IN); await pg.fill("input[name=check_out]", CHECK_OUT)
    await pg.fill("input[name=guests]", "4"); await pg.fill("input[name=guest_name]", name); await pg.fill("input[name=guest_phone]", phone)
    if shot_prefix:
        await c.shot(pg, shot_prefix + "-form", scroll="input[name=guest_name]")
        await c.shot(pg, shot_prefix + "-send", tap="button:has-text('Send request')")
    await pg.click("button:has-text('Send request')"); await pg.wait_for_load_state("networkidle"); await pg.wait_for_timeout(800)
    if shot_prefix:
        await pg.evaluate("[...document.querySelectorAll('*')].find(e=>e.children.length<3 && e.innerText && e.innerText.startsWith('Request sent'))?.scrollIntoView({block:'center'})")
        await c.shot(pg, shot_prefix + "-sent")
    link = await pg.query_selector("a[href*='/stay/']")
    if not link:
        txt = await pg.inner_text("body"); i = txt.find("Book your stay\n\nBook directly")
        print("  no booking link:", txt[i + 80:i + 500].replace("\n", " ") if i >= 0 else txt[-500:])
        return None
    href = await link.get_attribute("href")
    return href if href.startswith("http") else B + href


async def main():
    c = Cap(HERE / "shots")
    async with async_playwright() as p:
        rules = os.environ.get("HOST_RULES")   # e.g. "MAP demo.stayflow.example 127.0.0.1:5103" for a clean URL on screen
        b = await p.chromium.launch(args=[f"--host-resolver-rules={rules}"] if rules else [])
        g = await (await c.ctx(b)).new_page()
        # 1. the property's own booking website
        await g.goto(B + "/", wait_until="networkidle"); await c.shot(g, "home")
        await g.evaluate("window.scrollTo(0, 820)"); await c.shot(g, "home-2")
        # 2. live availability for the guest's dates
        await g.goto(B + f"/rooms?check_in={CHECK_IN}&check_out={CHECK_OUT}&guests=4", wait_until="networkidle")
        await g.evaluate("window.scrollTo(0, 560)"); await c.shot(g, "rooms")
        await g.goto(B + "/rooms/1", wait_until="networkidle"); await c.shot(g, "room")
        # 3. request a stay
        stay_url = await request(c, g, "Maria Santos", "09171234567", "req")
        # 4. owner reviews + approves
        o = await (await c.ctx(b)).new_page()
        o.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await o.goto(B + "/admin/login"); await o.fill("input[type=password]", PW); await o.press("input[type=password]", "Enter")
        await o.wait_for_load_state("networkidle"); await c.shot(o, "admin")
        await c.shot(o, "admin-approve", tap="button:has-text('Approve') >> nth=0")
        await o.locator("button:has-text('Approve')").first.click(); await o.wait_for_timeout(1500)
        await c.shot(o, "admin-approved")
        # 5. downpayment slip for the guest
        await o.goto(B + "/admin/bookings/1/slip", wait_until="networkidle"); await c.shot(o, "slip")
        # 6. guest's booking page
        await g.goto(stay_url, wait_until="networkidle"); await g.wait_for_timeout(800); await c.shot(g, "stay-page")
        # 7. a second guest tries the same room and dates -> the app refuses the double booking
        g2 = await (await c.ctx(b)).new_page()
        await g2.goto(B + "/book?room_id=1", wait_until="networkidle")
        await g2.fill("input[name=check_in]", CHECK_IN); await g2.fill("input[name=check_out]", CHECK_OUT)
        await g2.fill("input[name=guests]", "4"); await g2.fill("input[name=guest_name]", "Juan Dela Cruz"); await g2.fill("input[name=guest_phone]", "09181234567")
        await c.shot(g2, "clash-send", tap="button:has-text('Send request')")
        await g2.click("button:has-text('Send request')"); await g2.wait_for_load_state("networkidle"); await g2.wait_for_timeout(800)
        await g2.evaluate("[...document.querySelectorAll('p,div')].filter(e=>e.children.length<2 && e.innerText.includes('already booked')).pop()?.scrollIntoView({block:'center'})")
        await c.shot(g2, "clash-blocked")
        await b.close()
    c.save()

asyncio.run(main())
