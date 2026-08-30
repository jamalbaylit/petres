"""One class per slide type. Each pairs itself with a Jinja2 template in
assets/templates/ and exposes a ``render(width, height) -> str`` method that
SlideDeck calls to build the final document.
"""

from __future__ import annotations

import warnings
from pathlib import Path

from .highlight import render_code_html
from .rendering.assets import to_data_uri
from .rendering.html import get_template

_REPO_ROOT = Path(__file__).resolve().parents[1]
_LOGOS = {
    "light": _REPO_ROOT / "assets" / "logo-lockup-light.svg",
    "dark": _REPO_ROOT / "assets" / "logo-lockup-dark.svg",
}


class MainPage:
    def __init__(
        self,
        title: str,
        description: str | None = None,
        theme: str = "light",
        logo: bool = False,
        footer_left: str | None = None,
        footer_right: str | None = None,
    ):
        self.title = title
        self.description = description
        self.theme = theme
        self.logo = logo
        self.footer_left = footer_left
        self.footer_right = footer_right

    def render(self, *, width: int, height: int) -> str:
        logo_path = _LOGOS.get(self.theme) if self.logo else None
        logo_src = to_data_uri(logo_path) if logo_path and logo_path.exists() else None
        return get_template("main_page.html").render(
            title=self.title,
            description=self.description,
            theme=self.theme,
            logo_src=logo_src,
            footer_left=self.footer_left,
            footer_right=self.footer_right,
        )


class CodeSnippet:
    def __init__(
        self,
        code: str,
        title: str | None = None,
        description: str | None = None,
        header_left: str | None = None,
        header_right_first: str | None = None,
        header_right_second: str | None = None,
        header_right_splitter: str = "/",
        code_preview: str | Path | None = None,
        footer_left: str | None = None,
        footer_right: str | None = None,
        theme: str = "light",
    ):
        self.code = code
        self.title = title
        self.description = description
        self.header_left = header_left
        self.header_right_first = header_right_first
        self.header_right_second = header_right_second
        self.header_right_splitter = header_right_splitter
        self.code_preview = code_preview
        self.footer_left = footer_left
        self.footer_right = footer_right
        self.theme = theme

    def render(self, *, width: int, height: int) -> str:
        preview_src = None
        if self.code_preview:
            preview_path = Path(self.code_preview)
            if preview_path.exists():
                preview_src = to_data_uri(preview_path)
            else:
                warnings.warn(f"code_preview not found, skipping: {preview_path}")
        return get_template("code_snippet.html").render(
            header_left=self.header_left,
            header_right_first=self.header_right_first,
            header_right_second=self.header_right_second,
            header_right_splitter=self.header_right_splitter,
            title=self.title,
            description=self.description,
            code_html=render_code_html(self.code),
            preview_src=preview_src,
            footer_left=self.footer_left,
            footer_right=self.footer_right,
            theme=self.theme,
        )
