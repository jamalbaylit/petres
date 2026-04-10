from __future__ import annotations

from pathlib import Path

import pyvista as pv

from petres.grids import CornerPointGrid
from petres.viewers import Viewer3D


ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "examples" / "data" / "corner_point" / "Norne.GRDECL"
OUTPUT_PATH = (
    ROOT
    / "docs"
    / "source"
    / "_static"
    / "tutorials"
    / "importing-grid-norne-interactive.html"
)


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Norne grid file not found: {DATA_PATH}")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    grid = CornerPointGrid.from_grdecl(DATA_PATH)

    plotter = pv.Plotter(off_screen=True, window_size=(1400, 900))
    viewer = Viewer3D(plotter=plotter)
    depth_scalars = grid._resolve_source("depth")
    viewer.add_grid(grid, show_inactive=False, scalars=depth_scalars)
    viewer.apply_theme(viewer.theme)
    viewer.apply_camera(viewer.camera)

    plotter.export_html(str(OUTPUT_PATH))
    plotter.close()

    print(f"Saved interactive HTML to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
