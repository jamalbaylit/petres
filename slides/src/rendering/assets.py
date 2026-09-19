"""Embed local files into HTML as data: URIs (so Playwright's set_content, which
has no base URL to resolve relative paths against, can still show them)."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path


def to_data_uri(path: str | Path) -> str:
    path = Path(path)
    mime_type, _ = mimetypes.guess_type(path.name)
    mime_type = mime_type or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"
