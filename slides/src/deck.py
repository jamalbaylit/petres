from __future__ import annotations

from pathlib import Path

from .rendering.html import assemble_document
from .rendering.pdf import write_pdf, write_png


class SlideDeck:
    """Builder for a deck: add pages, then export to PDF/PNG.

    Page size is fixed for the whole deck -- component templates use
    relative units (rem/%/vw) so they scale with whatever width/height is
    given here.
    """

    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self._pages: list = []

    def add(self, page) -> "SlideDeck":
        self._pages.append(page)
        return self

    def __len__(self) -> int:
        return len(self._pages)

    def to_html(self) -> str:
        sections = [page.render(width=self.width, height=self.height) for page in self._pages]
        css_files = sorted({name for page in self._pages for name in page.css_files})
        return assemble_document(sections, css_files, width=self.width, height=self.height)

    def to_pdf(self, path: str | Path) -> Path:
        return write_pdf(self.to_html(), self.width, self.height, path)

    def to_png(self, directory: str | Path, *, scale: float = 2.0) -> list[Path]:
        return write_png(self.to_html(), self.width, self.height, directory, scale=scale)
