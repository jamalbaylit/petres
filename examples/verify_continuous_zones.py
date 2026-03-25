"""Verify that continuous zones (no gaps) all remain active."""

from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.models import Zone, Horizon
import numpy as np

# Create continuous horizons (no gaps)
h1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], z=[0,1,0,1], interpolator=IDWInterpolator())
h2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], z=[2,2,3,3], interpolator=IDWInterpolator())
h3 = Horizon("H3", xy=[[0,0],[100,0],[100,100],[0,100]], z=[2,2,3,3], interpolator=IDWInterpolator())  # Same as h2!
h4 = Horizon("H4", xy=[[0,0],[100,0],[100,100],[0,100]], z=[5,7,8,4], interpolator=IDWInterpolator())

zones = [
  Zone("Zone1", top=h1, base=h2).divide(nk=2),  # 2 layers
  Zone("Zone2", top=h3, base=h4).divide(nk=3),  # 3 layers, continuous with Zone1
]

pillars = PillarGrid.from_regular(xlim=(0,100), ylim=(0,100), ni=10, nj=10, z_top=0, z_bottom=10)
grid = CornerPointGrid.from_zones(pillars=pillars, zones=zones)

print(f"Grid shape (nk, nj, ni): {grid.shape}")
print(f"Total cells: {grid.n_cells}")
print(f"Active cells: {grid.n_active}")
print(f"All cells active: {grid.n_active == grid.n_cells}")

# Check if ACTNUM is None or all True
if grid.active is None:
    print("\nACTNUM: None (all cells active by default)")
else:
    all_active = np.all(grid.active)
    print(f"\nACTNUM: boolean array with all values = {all_active}")
    if not all_active:
        print("WARNING: Some cells are inactive, but all should be active!")
        for k in range(grid.nk):
            active_count = np.sum(grid.active[k, :, :])
            total_count = grid.ni * grid.nj
            if active_count < total_count:
                print(f"  Layer {k}: {active_count}/{total_count} cells active")
