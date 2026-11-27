"""Build the print files for the LlanesLab business card.

    cd ~/Developer/llaneslab/print/business-card
    uv run --no-project --with playwright python build.py          # print files
    uv run --no-project --with playwright python build.py --guides # also trim/safe-zone check images

Edit card.src.html for wording or design. qr.path holds the QR code for https://danmarcllanes.vercel.app/card.
"""
import random
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

D = Path(__file__).parent


def stars(seed: int, n: int, keep_out: list[tuple[float, float, float, float]]) -> str:
    """Small seeded star field on the 375 x 225 canvas, kept out of text boxes."""
    r = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = r.uniform(4, 371), r.uniform(4, 221)
        if any(a <= x <= c and b <= y <= d for a, b, c, d in keep_out):
            continue
        size = r.choice([0.45, 0.55, 0.65, 0.8, 1.1])
        colour = r.choice(["#FFFFFF"] * 5 + ["#BFDBFE", "#E9D5FF"])
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size}" fill="{colour}" opacity="{r.uniform(.35, .9):.2f}"/>')
    return "".join(out)


def build_html(guides: bool) -> str:
    n, d = (D / "qr.path").read_text().split("|")
    n = int(n)
    h = (D / "card.src.html").read_text()
    h = h.replace("__QRVB__", f"-1 -1 {n + 2} {n + 2}").replace("__QRPATH__", d)
    h = h.replace("__STARS_FRONT__", stars(7, 70, [(30, 70, 300, 160), (30, 180, 190, 205)]))
    h = h.replace("__STARS_BACK__", stars(11, 40, [(30, 20, 250, 210), (255, 20, 360, 215)]))
    return h.replace("__GUIDES__", "guides" if guides else "")


def main() -> None:
    guides = "--guides" in sys.argv
    (D / "card.html").write_text(build_html(False))
    (D / "card-guides.html").write_text(build_html(True))
    with sync_playwright() as p:
        b = p.chromium.launch()
        jobs = [("card.html", "LlanesLab-card-{}-300dpi.png")] + ([("card-guides.html", "check-{}.png")] if guides else [])
        for f, out in jobs:
            pg = b.new_page(viewport={"width": 360, "height": 216}, device_scale_factor=3.125)  # 300 dpi
            pg.goto((D / f).as_uri())
            pg.wait_for_load_state("networkidle")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(400)
            if f == "card.html":
                pg.pdf(path=str(D / "LlanesLab-card-print.pdf"), width="3.75in", height="2.25in", print_background=True)
            for i, side in enumerate(["front", "back"]):
                pg.locator(".card").nth(i).screenshot(path=str(D / out.format(side)))
        b.close()
    print("Built LlanesLab-card-print.pdf and 300 dpi PNGs in", D)


if __name__ == "__main__":
    main()
