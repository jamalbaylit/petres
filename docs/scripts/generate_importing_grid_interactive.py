from __future__ import annotations

from pathlib import Path

import pyvista as pv

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


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Norne grid file not found: {DATA_PATH}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    grid = CornerPointGrid.from_grdecl(DATA_PATH)

    light_theme = Viewer3DTheme(
        background="white",
        show_orientation_widget=True,
        show_coordinate_axes=True,
        title_color="black",
    )
    dark_theme = Viewer3DTheme(
        background="#0f172a",
        show_orientation_widget=True,
        show_coordinate_axes=True,
        title_color="#e5e7eb",
    )

    _export_interactive_html(grid=grid, theme=light_theme, output_path=LIGHT_OUTPUT_PATH)
    _export_interactive_html(grid=grid, theme=dark_theme, output_path=DARK_OUTPUT_PATH)

    print(f"Saved light interactive HTML to: {LIGHT_OUTPUT_PATH}")
    print(f"Saved dark interactive HTML to: {DARK_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
