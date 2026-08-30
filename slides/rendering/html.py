"""Jinja2 environment and full-document HTML assembly."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .fonts import build_font_face_css

_ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
_TEMPLATES_DIR = _ASSETS_DIR / "templates"
_STATIC_DIR = _ASSETS_DIR / "static"
_CSS_DIR = _STATIC_DIR / "css"
_FONTS_DIR = _STATIC_DIR / "fonts"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATES_DIR),
    autoescape=select_autoescape(["html"]),
)


def get_template(name: str):
    return _env.get_template(name)


def assemble_document(sections: list[str], *, width: int, height: int) -> str:
    """Wrap already-rendered page fragments in the shared document shell."""
    css_files = "\n".join(path.read_text(encoding="utf-8") for path in sorted(_CSS_DIR.glob("*.css")))
    css = build_font_face_css(_FONTS_DIR) + "\n" + css_files
    return get_template("document.html").render(width=width, height=height, css=css, sections=sections)
