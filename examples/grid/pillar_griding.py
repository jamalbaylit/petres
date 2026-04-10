"""
Pillar Grid Creation Examples
=============================

This example demonstrates different ways to construct a ``PillarGrid`` 
using the Petres library. Pillar grids define the structural framework 
for corner-point grids and are typically created using regular or 
rectilinear spacing.

The examples below cover:
- Regular grid generation using limits or spacing
- Rectilinear grid construction with custom coordinates
- Use of NumPy for flexible grid definition
- Manual specification of pillar top and bottom depths
- Basic visualization of the resulting grid
"""

from petres.grids import PillarGrid
import numpy as np


# ---------------------------------------------------------------------
# Example 1: Regular grid using domain limits and number of cells
# ---------------------------------------------------------------------
pillars = PillarGrid.from_regular(
    xlim=(0, 100),
    ylim=(0, 100),
    ni=50,
    nj=50,
)
pillars.show()  # Visualize the grid

# ---------------------------------------------------------------------
# Example 2: Regular grid using cell spacing (dx, dy)
# ---------------------------------------------------------------------
pillars = PillarGrid.from_regular(
    xlim=(0, 100),
    ylim=(0, 100),
    dx=2,
    dy=2,
)

pillars.show()
# ---------------------------------------------------------------------
# Example 3: Rectilinear grid with non-uniform spacing
# ---------------------------------------------------------------------
pillars = PillarGrid.from_rectilinear(
    x=[0, 10, 50, 70, 100],
    y=np.linspace(0, 100, 50),
)
pillars.show()

# ---------------------------------------------------------------------
# Example 4: Using NumPy to generate structured coordinates
# ---------------------------------------------------------------------
pillars = PillarGrid.from_rectilinear(
    x=np.linspace(0, 100, 50),
    y=np.linspace(0, 100, 50),
    top=0,
    base=15,
)
pillars.show()

# ---------------------------------------------------------------------
# Example 5: Manually specifying pillar top and bottom depths
# ---------------------------------------------------------------------
pillars = PillarGrid.from_rectilinear(
    x=[0, 10, 50, 70, 100],
    y=np.linspace(0, 100, 50),
    top=1000,
    base=1500,
)

# ---------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------
# The grid can be visualized interactively using the `show` method.
pillars.show()