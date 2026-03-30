from __future__ import annotations

from typing import Any

from furo.navigation import get_navigation_tree


def _inject_navigation_tree_with_sections(
    app: Any,
    pagename: str,
    templatename: str,
    context: dict[str, Any],
    doctree: Any,
) -> None:
    toctree = context.get("toctree")
    if not toctree:
        return

    maxdepth = getattr(app.config, "furo_nav_sections_maxdepth", 3)

    toctree_html = toctree(
        collapse=False,
        titles_only=False,
        maxdepth=maxdepth,
        includehidden=True,
    )
    context["furo_navigation_tree"] = get_navigation_tree(toctree_html)


def setup(app: Any) -> dict[str, Any]:
    app.add_config_value("furo_nav_sections_maxdepth", 3, "html")
    app.connect("html-page-context", _inject_navigation_tree_with_sections, priority=900)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
