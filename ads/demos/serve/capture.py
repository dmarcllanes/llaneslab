"""Capture the ServeFlow demo screens from a running demo restaurant (Kapé at Kain).
Run the app first (see ../README.md), then:  uv run --with playwright python capture.py"""
import asyncio, os, sys
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from capture_lib import Cap, make_proof, wait_reply

B = os.environ.get("SERVE_URL", "http://demo-resto.localhost:5102")
PW = os.environ.get("SERVE_ADMIN_PASSWORD", "demo-owner-123")
HERE = Path(__file__).resolve().parent
PROOF = HERE / "sample-payment.png"
TAGALOG = (" ang ", " ng ", " mo ", " po ", "oo,", " kami", " gusto", " lang", " sa ", " na ", " may ", " ba ")


async def main():
    c = Cap(HERE / "shots")
    async with async_playwright() as p:
        rules = os.environ.get("HOST_RULES")   # e.g. "MAP demo.stayflow.example 127.0.0.1:5103" for a clean URL on screen
        b = await p.chromium.launch(args=[f"--host-resolver-rules={rules}"] if rules else [])
        # 1. customer scans the table QR -> menu for table 5
        for attempt in range(10):
            cu = await (await c.ctx(b)).new_page()
            await cu.goto(B + "/menu?table=5", wait_until="networkidle")
            if attempt == 0:
                await c.shot(cu, "menu")
                await cu.evaluate("document.querySelector('#cat-2')?.scrollIntoView({block:'start'})"); await c.shot(cu, "menu-scrolled")
                await cu.evaluate("window.scrollTo(0,0)")
            if os.environ.get("SKIP_AI"): break
            # 2. AI menu helper
            await cu.click("text=Need help choosing?"); await cu.wait_for_timeout(600)
            await cu.fill("form[hx-post='/chat'] input[name=message], #bf-chat input[name=message], input[name=message]", "Something iced and sweet under ₱170?")
            await c.shot(cu, "chat-ask")
            await cu.press("input[name=message]", "Enter")
            await wait_reply(cu)
            body = " " + (await cu.inner_text("body")).lower().replace("\n", " ") + " "
            reply = body.split("ask about the menu")[0][-900:]
            bad = [w for w in TAGALOG if w in reply] + (["markdown"] if any(m in reply for m in ("**", "|", "variant", "##")) else [])
            if not bad: break
            print("  chat retry", attempt + 1, bad)
        if not os.environ.get("SKIP_AI"): await c.shot(cu, "chat-answer")
        # 3. customise the drink
        await cu.goto(B + "/menu?table=5", wait_until="networkidle")
        await c.shot(cu, "menu-tap", tap="text=Ube Spanish Latte >> nth=0")
        await cu.locator("text=Ube Spanish Latte").first.click(); await cu.wait_for_timeout(1500)
        await c.shot(cu, "item")
        await cu.click("label:has(input[name=variant_id][value='2'])"); await cu.click("label:has(input[name=g1][value='1'])")
        await cu.click("label:has-text('Ube cold foam')")
        await c.shot(cu, "item-picked", tap="button:has-text('Add to cart')")
        await cu.click("button:has-text('Add to cart')"); await cu.wait_for_timeout(1200)
        # 4. checkout: dine-in at table 5, GCash
        await cu.goto(B + "/checkout", wait_until="networkidle")
        await cu.fill("input[name=name]", "Maria"); await cu.fill("input[name=phone]", "09171234567")
        await c.shot(cu, "checkout-top", scroll="input[name=table_no]")
        await cu.click("label:has(input[name=payment][value=gcash])")
        await c.shot(cu, "checkout-pay", tap="button:has-text('Place order')")
        await cu.click("button:has-text('Place order')"); await cu.wait_for_load_state("networkidle"); await cu.wait_for_timeout(800)
        order_url = cu.url.split("?")[0]
        code = (await cu.inner_text("body")).split("#")[1][:4]
        total = (await cu.inner_text("body")).split("Total")[-1].split("\n")[1].strip() if "Total" in await cu.inner_text("body") else "₱190"
        print("  order", code, total)
        await make_proof(b, PROOF, "₱190.00", "Kapé at Kain", "#" + code)
        await c.shot(cu, "order-new")
        await cu.set_input_files("input[name=proof]", str(PROOF))
        await c.shot(cu, "proof-chosen", tap="button:has-text('Send payment proof')")
        await cu.click("button:has-text('Send payment proof')"); await cu.wait_for_load_state("networkidle"); await cu.wait_for_timeout(1000)
        await c.shot(cu, "proof-sent")
        # 5. kitchen board
        ow = await (await c.ctx(b)).new_page()
        ow.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
        await ow.goto(B + "/admin/login"); await ow.fill("input[type=password]", PW); await ow.press("input[type=password]", "Enter")
        await ow.wait_for_load_state("networkidle")
        await ow.goto(B + "/admin/queue?tab=pending_payment", wait_until="networkidle"); await ow.wait_for_timeout(800)
        card = "[id^=order-]:has-text('Maria')"
        await c.shot(ow, "k-verify", tap=f"{card} button:has-text('Verify payment')")
        await ow.click(f"{card} button:has-text('Verify payment')"); await ow.wait_for_timeout(1500)
        await ow.goto(B + "/admin/queue?tab=preparing", wait_until="networkidle"); await ow.wait_for_timeout(800)
        await c.shot(ow, "k-preparing", tap=f"{card} button:has-text('Mark ready')")
        await ow.click(f"{card} button:has-text('Mark ready')"); await ow.wait_for_timeout(1500)
        await ow.goto(B + "/admin/queue?tab=ready", wait_until="networkidle"); await ow.wait_for_timeout(800)
        await c.shot(ow, "k-ready")
        # 6. customer sees "ready"
        await cu.goto(order_url, wait_until="networkidle"); await cu.wait_for_timeout(800); await c.shot(cu, "customer-ready")
        if not os.environ.get("SKIP_AI"):
    # 7. kitchen co-pilot (owner confirms)
            for attempt in range(10):
                if attempt:   # dismiss the unused proposal, then start a fresh co-pilot thread
                    await ow.locator("button:has-text('Dismiss')").last.click(); await ow.wait_for_timeout(800)
                    octx = await c.ctx(b); ow = await octx.new_page(); ow.on("dialog", lambda d: asyncio.ensure_future(d.accept()))
                    await ow.goto(B + "/admin/login"); await ow.fill("input[type=password]", PW); await ow.press("input[type=password]", "Enter")
                    await ow.wait_for_load_state("networkidle")
                await ow.goto(B + "/admin/copilot", wait_until="networkidle")
                await ow.fill("input[name=message]", "Set ensaymada to 10 left")
                await c.shot(ow, "copilot-ask")
                await ow.press("input[name=message]", "Enter")
                await ow.wait_for_selector("button:has-text('Confirm')", timeout=60000); await wait_reply(ow, min_growth=20)
                last = (await ow.inner_text("body")).split("Set ensaymada to 10 left")[-1]
                if not any(m in last for m in ("**", "proposal_id", "(id", "|")): break
                print("  copilot retry", attempt + 1)
            await c.shot(ow, "copilot-confirm", tap="button:has-text('Confirm') >> nth=-1")
            await ow.locator("button:has-text('Confirm')").last.click(); await ow.wait_for_timeout(1500)
            await c.shot(ow, "copilot-done")
        # 8. table QR codes
        await ow.goto(B + "/admin/qr", wait_until="networkidle"); await ow.wait_for_timeout(800); await c.shot(ow, "qr")
        await b.close()
    c.save()

asyncio.run(main())
