"""
Petres Grid Visualization Tutorial
==================================

This script demonstrates how to visualize Corner-Point grids using Petres.
It covers:
- Basic 3D grid visualization
- Displaying inactive cells
- Using built-in grid attributes
- Visualizing imported grid properties
- Customizing colors and titles
"""

from petres.grids import CornerPointGrid

# ---------------------------------------------------------------------
# Step 1: Load the grid from a GRDECL file
# ---------------------------------------------------------------------
grid = CornerPointGrid.from_grdecl(
    "examples/data/corner_point/Norne_with_props.GRDECL",
    properties=["PORO", "PERMX"]  # Only import selected properties
)

print("Available grid properties:", grid.properties)

# ---------------------------------------------------------------------
# Step 2: Basic 3D visualization
# ---------------------------------------------------------------------
# Display the grid in 3D viewer with default settings
grid.show(title="Basic Grid Visualization")

# ---------------------------------------------------------------------
# Step 3: Visualize inactive cells
# ---------------------------------------------------------------------
# By default, inactive cells are hidden. To show them:
grid.show(show_inactive=True, title="Grid with Inactive Cells")

# ---------------------------------------------------------------------
# Step 4: Using built-in scalars
# ---------------------------------------------------------------------
# Petres provides built-in scalar fields, such as "top" and "active"
grid.show(scalars="top", title="Grid Colored by 'top'")
grid.show(scalars="active", title="Grid Colored by 'active'")

# ---------------------------------------------------------------------
# Step 5: Visualize imported grid properties
# ---------------------------------------------------------------------
# You can visualize any imported property as a scalar
for prop in grid.properties:
    grid.show(scalars=prop, cmap="viridis", title=f"Grid Property: {prop.name}")

# ---------------------------------------------------------------------
# Step 6: Custom colors
# ---------------------------------------------------------------------
# Scalar visualization with a specific colormap
grid.show(scalars="PORO", cmap="viridis", title="Porosity with Viridis Colormap")

# Non-scalar visualization with a fixed color
grid.show(color="lightblue", title="Grid with Custom Color")

# ---------------------------------------------------------------------
# Notes:
# - Matplotlib named colors are supported: 
#   https://matplotlib.org/stable/gallery/color/named_colors.html
# ---------------------------------------------------------------------