"""Capture the ShopFlow demo screens from a running demo store.
Run the app first (see ../README.md), then:  uv run --with playwright python capture.py"""
import asyncio, os, sys
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from capture_lib import Cap

B = os.environ.get("SHOP_URL", "http://demo-store.localhost:5101")
PW = os.environ.get("SHOP_ADMIN_PASSWORD", "ad-capture-pass")
HERE = Path(__file__).resolve().parent
PROOF = HERE.parent / "assets" / "sample-payment.png"


async def main():
    c = Cap(HERE / "shots")
    async with async_playwright() as p:
        b = await p.chromium.launch()
        cu = await (await c.ctx(b)).new_page()
        # 1. storefront
        await cu.goto(B + "/", wait_until="networkidle"); await c.shot(cu, "home")
        await cu.evaluate("window.scrollTo(0, 1050)"); await c.shot(cu, "home-cats")
        # 2. AI shop assistant (retry in a fresh session until the reply is plain English with one cart card)
        TAGALOG = (" ang ", " ng ", " mo ", " po ", "oo,", " kami", " kulay", " gusto", " lang", " sa ", " na ", " may ")
        for attempt in range(6):
            if attempt: cu = await (await c.ctx(b)).new_page()
            await cu.goto(B + "/chat", wait_until="networkidle")
            await cu.fill("input[name=message]", "Do you have the linen shirt in size M?")
            await c.shot(cu, "chat-ask", tap="button:has-text('Send')")
            await cu.click("button:has-text('Send')"); await cu.wait_for_load_state("networkidle")
            await c.shot(cu, "chat-answer")
            await cu.fill("input[name=message]", "White, please. Just one.")
            await cu.click("button:has-text('Send')"); await cu.wait_for_load_state("networkidle")
            body = " " + (await cu.inner_text("body")).lower().replace("\n", " ") + " "
            cards = await cu.locator("button:has-text('Add to cart')").count()
            tagalog = [w for w in TAGALOG if w in body]
            if not tagalog and cards == 1:
                break
            print(f"  chat retry {attempt + 1}: tagalog={tagalog} cards={cards}")
        await c.shot(cu, "chat-cart", tap="button:has-text('Add to cart') >> nth=-1")
        await cu.locator("button:has-text('Add to cart')").last.click(); await cu.wait_for_load_state("networkidle"); await cu.wait_for_timeout(800)
        # 3. checkout
        await cu.goto(B + "/checkout", wait_until="networkidle"); await c.shot(cu, "checkout-top")
        await cu.fill("input[name=customer_name]", "Maria Santos"); await cu.fill("input[name=phone]", "09171234567")
        await cu.check("input[value=delivery]"); await cu.select_option("select[name=zone_id]", "1")
        await cu.fill("textarea[name=address]", "12 Acacia St, Brgy. San Antonio, Quezon City")
        await c.shot(cu, "checkout-filled", tap="button:has-text('Place order')")
        await cu.click("button:has-text('Place order')"); await cu.wait_for_load_state("networkidle")
        order_url = cu.url.split("?")[0]
        # 4. pay + upload proof
        await c.shot(cu, "order-new")
        await cu.evaluate("document.querySelector('input[name=proof]').closest('form').scrollIntoView({block:'center'})")
        await c.shot(cu, "order-pay")
        await cu.set_input_files("input[name=proof]", str(PROOF))
        await c.shot(cu, "proof-chosen", tap="button:has-text('Send payment pr')")
        await cu.click("button:has-text('Send payment pr')"); await cu.wait_for_load_state("networkidle")
        await c.shot(cu, "proof-sent")
        # 5. owner side
        ow = await (await c.ctx(b)).new_page()
        await ow.goto(B + "/admin/login"); await ow.fill("input[type=password]", PW); await ow.press("input[type=password]", "Enter")
        await ow.wait_for_load_state("networkidle"); await c.shot(ow, "admin-orders")
        ow.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await c.shot(ow, "admin-verify", tap="button:has-text('Payment received')")
        await ow.click("button:has-text('Payment received')"); await ow.wait_for_timeout(1500)
        await c.shot(ow, "admin-paid")
        # 6. owner AI co-pilot: prepares the change, owner confirms
        ref = (await cu.inner_text("body")).split("SF-")[1].split()[0]
        ref = "SF-" + ref.strip()
        print("  order ref", ref)
        await ow.goto(B + "/admin/copilot", wait_until="networkidle")
        await ow.fill("form[action='/admin/copilot'] input[name=message]", f"Mark {ref} as packed")
        await c.shot(ow, "copilot-ask", tap="form[action='/admin/copilot'] button:has-text('Send')")
        await ow.click("form[action='/admin/copilot'] button:has-text('Send')")
        await ow.wait_for_selector("button:has-text('Confirm')", timeout=60000); await ow.wait_for_timeout(800)
        await c.shot(ow, "copilot-confirm", tap="button:has-text('Confirm')")
        await ow.click("button:has-text('Confirm')"); await ow.wait_for_timeout(1500)
        await c.shot(ow, "copilot-done")
        # 7. ship
        await ow.goto(B + "/admin?tab=ship", wait_until="networkidle")
        await ow.fill("input[name=courier]", "J&T Express"); await ow.fill("input[name=tracking_no]", "JT0012345678")
        await c.shot(ow, "admin-ship", tap="button:has-text('Ship')")
        await ow.click("button:has-text('Ship')"); await ow.wait_for_timeout(1500)
        await c.shot(ow, "admin-shipped")
        # 8. customer sees progress
        await cu.goto(order_url, wait_until="networkidle")
        await cu.evaluate("[...document.querySelectorAll('h2,h3,p,div')].find(e=>e.innerText.trim()==='Progress')?.scrollIntoView({block:'start'})")
        await c.shot(cu, "customer-progress")
        await b.close()
    c.save()

asyncio.run(main())
