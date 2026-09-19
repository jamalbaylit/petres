"""Embed local font files (assets/static/fonts/) as @font-face rules with
base64 data URIs -- Playwright's set_content() has no base URL, so a plain
url(../fonts/...) reference wouldn't resolve.

Family name is the part of the filename before the first '-'; weight is
guessed from a keyword in the rest of the filename (Bold, SemiBold, ...).
Drop a new font file in that folder and it's picked up automatically.
"""

from __future__ import annotations

from pathlib import Path

from .assets import to_data_uri

_FORMATS = {".ttf": "truetype", ".otf": "opentype", ".woff2": "woff2", ".woff": "woff"}

_WEIGHTS = {
    "thin": 100,
    "extralight": 200,
    "light": 300,
    "regular": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
    "extrabold": 800,
    "black": 900,
}


def _guess_weight(stem: str) -> int:
    lowered = stem.lower()
    for keyword, weight in _WEIGHTS.items():
        if keyword in lowered:
            return weight
    return 400


def build_font_face_css(fonts_dir: Path) -> str:
    if not fonts_dir.is_dir():
        return ""

    rules = []
    for path in sorted(fonts_dir.iterdir()):
        fmt = _FORMATS.get(path.suffix.lower())
        if fmt is None:
            continue
        family = path.stem.split("-")[0]
        weight = _guess_weight(path.stem)
        rules.append(
            "@font-face {\n"
            f'    font-family: "{family}";\n'
            f'    src: url("{to_data_uri(path)}") format("{fmt}");\n'
            f"    font-weight: {weight};\n"
            "    font-style: normal;\n"
            "    font-display: swap;\n"
            "}"
        )
    return "\n".join(rules)
