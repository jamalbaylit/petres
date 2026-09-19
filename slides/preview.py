"""Local live-reload preview for editing templates/CSS.

Run:
    python slides/preview.py
    (or python -m slides.preview, from the repo root)

Renders through the exact same pipeline as SlideDeck.to_pdf(), so what you
see in the browser is what ends up in the PDF (the iframe is sized to the
deck's own width/height, so vw-based rem sizing matches exactly). Edit
build_preview_deck() below to point at whatever page you're currently
designing, then just save -- the tab picks up template/CSS/font changes
without a manual refresh.
"""

from __future__ import annotations

import html
import os
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from slides import CodeSnippet, MainPage, SlideDeck, Outro

_THIS_FILE = Path(__file__).resolve()
_PACKAGE_DIR = _THIS_FILE.parent / "src"
_WATCH_PATHS = [
    _PACKAGE_DIR / "assets",
    _PACKAGE_DIR / "components.py",
    _PACKAGE_DIR / "highlight.py",
    _PACKAGE_DIR / "deck.py",
    _PACKAGE_DIR / "rendering",
    # preview.py itself -- build_preview_deck() lives here, so editing it
    # needs the *process* to restart, not just the browser tab to refetch.
    _THIS_FILE,
]

_RELOAD_SCRIPT = """
<script>
let lastToken = null;
async function poll() {
    try {
        const res = await fetch('/__reload__');
        const token = await res.text();
        if (lastToken !== null && token !== lastToken) {
            document.getElementById('frame').contentWindow.location.reload();
        }
        lastToken = token;
    } catch (e) {}
    setTimeout(poll, 500);
}
poll();
</script>
"""


def build_preview_deck() -> SlideDeck:
    """Edit this to preview whatever page(s) you're working on."""
    deck = SlideDeck(width=1350, height=1080)
    deck.add(
        MainPage(
            title="Zone Modeling",
            description="Create zones from horizons and divide them into layers.",
            theme="dark",
            logo=True,
            footer_left="petres.io",
            footer_right="Swipe →",
        )
    )

    
    # Each CodeSnippet is highlighted in isolation (its own jedi.Script), so a
    # later step referencing names an earlier step defined (horizon, zone,
    # np) can't resolve them on its own -- pass the earlier steps' code as
    # context= so jedi can still infer types, without it being rendered.
    step1_code = """
    from petres.interpolators import IDWInterpolator
    from petres.models import Horizon

    horizon = Horizon(
        name="Top Layer",
        xy=[[20, 78], [70, 80], [32, 55]],
        depth=[100, 110, 90],
        interpolator=IDWInterpolator(power = 2)
    )
            """
    deck.add(
        CodeSnippet(
            header_left="STEP 01",
            header_right_first="Tutorials",
            header_right_second="Zone Modeling",
            title="Define a Horizon",
            description="Start with a few depth measurements and turn them into a continuous horizon.",
            code=step1_code,
            footer_right="1 / 3",
            theme="light",
        )
    )


    step2_code = """
import numpy as np

zone = horizon.to_zone(
    name="Reservoir",
    depth=20
)

zone.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50)
)
            """
    deck.add(
        CodeSnippet(
            header_left="STEP 02",
            header_right_first="Tutorials",
            header_right_second="Zone Modeling",
            title="Create a Zone",
            description="Turn the horizon into a zone by giving it a defined thickness.",
            code=step2_code,
            context=step1_code,
            code_preview=r"C:\Users\Tayfun\Desktop\GitHub\Personal\petres\slides\examples\zone_modeling\assets\zone.png",
            footer_right="2 / 3",
            theme="light",
        )
    )

    deck.add(
        CodeSnippet(
            header_left="STEP 03",
            header_right_first="Tutorials",
            header_right_second="Zone Modeling",
            title="Subdivide the Zone",
            description="Divide the zone into three layers based on their relative thickness.",
            code="""
zone.divide(fractions=[0.3, 0.5, 0.2])

zone.show(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50)
)
            """,
            context=step1_code + step2_code,
            code_preview=r"C:\Users\Tayfun\Desktop\GitHub\Personal\petres\slides\examples\zone_modeling\assets\layering.png",
            footer_right="3 / 3",
            theme="light",
        )
    )
    deck.add(
        Outro(
            title="Explore Further",
            theme="dark",
            logo=True,
            footer_left="petres.io",

            footer_left_title="TUTORIALS & DOCUMENTATION",
            footer_right_title="SOURCE CODE",
            footer_right="github.com/jamalbaylit/petres",
        )
    )
    return deck


def _render_single_page(deck: SlideDeck, page: int) -> str:
    """deck.to_html() stacks every .slide-page in normal document flow (right,
    for print pagination) -- for an on-screen single-page preview that means
    N pages' worth of height inside one iframe, which is what was actually
    causing the scrollbar. Hide every page but the requested one instead of
    touching the shared templates/CSS used for the real PDF export.
    """
    doc = deck.to_html()
    override = (
        "<style>"
        "html, body { overflow: hidden; }"
        ".slide-page { display: none; }"
        f".slide-page:nth-of-type({page + 1}) {{ display: flex; }}"
        "</style></head>"
    )
    return doc.replace("</head>", override, 1)


def _watch_token() -> str:
    latest = 0.0
    for base in _WATCH_PATHS:
        paths = base.rglob("*") if base.is_dir() else [base]
        for path in paths:
            if path.is_file():
                latest = max(latest, path.stat().st_mtime)
    return str(latest)


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):  # keep the console quiet
        pass

    def _send(self, body: str, content_type: str = "text/html") -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/__reload__":
            self._send(_watch_token(), "text/plain")
            return

        if parsed.path == "/frame":
            try:
                deck = build_preview_deck()
                page = int(query.get("page", ["0"])[0])
                page = max(0, min(page, len(deck) - 1))
                self._send(_render_single_page(deck, page))
            except Exception as exc:
                message = html.escape(f"{type(exc).__name__}: {exc}")
                self._send(f"<pre style='color:#c00;white-space:pre-wrap;font:1rem monospace'>{message}</pre>")
            return

        deck = build_preview_deck()
        # The iframe is fixed at the deck's real width x height, so the
        # vw-based CSS inside computes against the true page dimensions --
        # /frame itself only ever shows one .slide-page at a time (see
        # _render_single_page), so there's nothing inside it to overflow.
        wrapper = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Slide Preview</title>
<style>
  html, body {{ margin: 0; height: 100%; background: #333; }}
  .wrap {{ min-height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 1rem; padding: 2rem; box-sizing: border-box; }}
  iframe {{ display: block; border: 0; box-shadow: 0 0 3rem rgba(0,0,0,.5); width: {deck.width}px; height: {deck.height}px; }}
  .nav {{ display: flex; align-items: center; gap: 1rem; font: 14px sans-serif; color: #ccc; }}
  .nav button {{ font: inherit; padding: 0.3em 0.8em; cursor: pointer; }}
</style></head>
<body>
  <div class="wrap">
    <iframe id="frame" src="/frame?page=0"></iframe>
    <div class="nav">
      <button id="prev">&larr; Prev</button>
      <span id="counter"></span>
      <button id="next">Next &rarr;</button>
    </div>
  </div>
  <script>
    const TOTAL = {len(deck)};
    let current = 0;
    const frame = document.getElementById('frame');
    const counter = document.getElementById('counter');

    function showPage(n) {{
        current = Math.max(0, Math.min(n, TOTAL - 1));
        frame.src = '/frame?page=' + current;
        counter.textContent = (current + 1) + ' / ' + TOTAL;
    }}
    document.getElementById('prev').addEventListener('click', () => showPage(current - 1));
    document.getElementById('next').addEventListener('click', () => showPage(current + 1));
    document.addEventListener('keydown', (e) => {{
        if (e.key === 'ArrowLeft') showPage(current - 1);
        if (e.key === 'ArrowRight') showPage(current + 1);
    }});
    showPage(0);
  </script>
  {_RELOAD_SCRIPT}
</body></html>"""
        self._send(wrapper)


def _watch_and_restart(initial_token: str) -> None:
    """Re-exec this process when preview.py/components.py/etc. change.

    Templates and CSS are re-read from disk on every request already, so
    they don't need this -- but build_preview_deck() and the rendering code
    it calls are regular Python, loaded into memory once at import time.
    """
    while True:
        time.sleep(1)
        if _watch_token() != initial_token:
            print("\nSource changed -- restarting preview server...")
            os.execv(sys.executable, [sys.executable, str(_THIS_FILE)])


class _Server(HTTPServer):
    # HTTPServer defaults this to True, which on Windows lets a second
    # process silently bind the same port instead of failing -- so a stale
    # instance from a previous run keeps answering requests underneath a
    # new one, invisibly. Fail fast instead.
    allow_reuse_address = False


def run(host: str = "127.0.0.1", port: int = 8000) -> None:
    threading.Thread(target=_watch_and_restart, args=(_watch_token(),), daemon=True).start()
    try:
        server = _Server((host, port), _Handler)
    except OSError as exc:
        raise SystemExit(
            f"Could not bind {host}:{port} ({exc}). "
            f"A previous `slides.preview` instance is probably still running -- stop it first."
        ) from exc
    print(f"Live preview: http://{host}:{port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
