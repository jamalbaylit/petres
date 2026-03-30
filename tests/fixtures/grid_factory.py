from __future__ import annotations

import numpy as np


def make_rectilinear_vertices(*, ni: int = 2, nj: int = 2, nk: int = 2):
    x = np.linspace(0.0, float(ni) * 100.0, ni + 1)
    y = np.linspace(0.0, float(nj) * 100.0, nj + 1)
    z = np.linspace(1000.0, 1000.0 + float(nk) * 20.0, nk + 1)
    return x, y, z


def make_plane_samples(nx: int = 3, ny: int = 3):
    x = np.linspace(0.0, 100.0, nx)
    y = np.linspace(0.0, 100.0, ny)
    xx, yy = np.meshgrid(x, y)
    xy = np.column_stack([xx.ravel(), yy.ravel()])
    z = 1000.0 + 0.2 * xy[:, 0] + 0.1 * xy[:, 1]
    return xy, z
