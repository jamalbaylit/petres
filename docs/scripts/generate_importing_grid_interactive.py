from __future__ import annotations

from pathlib import Path

import pyvista as pv
from matplotlib.colors import to_hex

from petres.grids import CornerPointGrid
from petres.viewers import Viewer3D, Viewer3DTheme


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "examples" / "data" / "corner_point" / "Norne.GRDECL"
OUTPUT_DIR = (
    ROOT
    / "docs"
    / "source"
    / "_static"
    / "tutorials"
)
LIGHT_OUTPUT_PATH = OUTPUT_DIR / "importing-grid-norne-interactive-light.html"
DARK_OUTPUT_PATH = OUTPUT_DIR / "importing-grid-norne-interactive-dark.html"


def _background_to_css(background: str | tuple[float, float, float]) -> str:
    """Convert a theme background value to a CSS hex color string."""
    return to_hex(background)


def _patch_html_background(html_path: Path, css_color: str) -> None:
    """Inject a matching background-color into the exported HTML body.

    PyVista's ``export_html`` produces a VTK.js viewer whose HTML body has no
    background-color.  This causes a white flash before the WebGL canvas
    renders — especially jarring in dark-themed docs.
    """
    text = html_path.read_text(encoding="utf-8")
    text = text.replace(
        "html, body { margin: 0; padding: 0; height: 100%; }",
        f"html, body {{ margin: 0; padding: 0; height: 100%; background: {css_color}; }}",
    )
    html_path.write_text(text, encoding="utf-8")


def _export_interactive_html(
    *,
    grid: CornerPointGrid,
    theme: Viewer3DTheme,
    output_path: Path,
) -> None:
    plotter = pv.Plotter(off_screen=True, window_size=(1400, 900))
    viewer = Viewer3D(plotter=plotter, theme=theme)

    depth_scalars = grid._resolve_source("depth")
    viewer.add_grid(grid, show_inactive=False, scalars=depth_scalars)
    viewer.apply_theme(viewer.theme)
    viewer.apply_camera(viewer.camera)

    plotter.export_html(str(output_path))
    plotter.close()

    _patch_html_background(output_path, _background_to_css(theme.background))


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Norne grid file not found: {DATA_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    grid = CornerPointGrid.from_grdecl(DATA_PATH)

    light_theme = Viewer3DTheme(
        background="white",
        font_color="black",
        show_orientation_widget=True,
        show_coordinate_axes=True,
    )
    dark_theme = Viewer3DTheme(
        background="#0f172a",
        font_color="#e5e7eb",
        show_orientation_widget=True,
        show_coordinate_axes=True,
    )

    _export_interactive_html(grid=grid, theme=light_theme, output_path=LIGHT_OUTPUT_PATH)
    _export_interactive_html(grid=grid, theme=dark_theme, output_path=DARK_OUTPUT_PATH)

    print(f"Saved light interactive HTML to: {LIGHT_OUTPUT_PATH}")
    print(f"Saved dark interactive HTML to: {DARK_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
