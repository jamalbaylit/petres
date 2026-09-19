"""Print the assembled HTML document via headless Chromium (Playwright)."""

from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


def write_pdf(html: str, width: int, height: int, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": width, "height": height})
            page.set_content(html, wait_until="load")
            page.pdf(
                path=str(path),
                width=f"{width}px",
                height=f"{height}px",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
        finally:
            browser.close()

    return path


def write_png(html: str, width: int, height: int, directory: str | Path, *, scale: float = 2.0) -> list[Path]:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
            page.set_content(html, wait_until="load")
            locator = page.locator(".slide-page")
            for i in range(locator.count()):
                out_path = directory / f"page_{i:02d}.png"
                locator.nth(i).screenshot(path=str(out_path))
                paths.append(out_path)
        finally:
            browser.close()

    return paths
