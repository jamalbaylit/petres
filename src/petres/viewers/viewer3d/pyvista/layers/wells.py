import numpy as np
import pyvista as pv

def _add_wells(backend, viewer, wells, *, color=None) -> None:
    p = backend.plotter
    t = viewer.theme

    well_color = color or t.well_line_color
    avg_len = float(np.mean([w.bottom - w.top for w in wells])) if wells else 0.0
    z_offset = avg_len * 0.05

    for w in wells:
        line = pv.Line((w.x, w.y, w.top), (w.x, w.y, w.bottom))
        tube = line.tube(radius=t.well_line_width, n_sides=16, capping=True)
        p.add_mesh(tube, color=well_color, smooth_shading=True)

        label_pos = (w.x * t.xscale, w.y * t.yscale, (w.top - z_offset) * t.zscale)
        p.add_point_labels(
            [label_pos], [w.name],
            font_size=t.wells_label_font_size,
            text_color="white", bold=True, shadow=True,
            always_visible=True, show_points=False,
            shape_opacity=1,
        )
