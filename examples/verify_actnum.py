"""Verify that gap-filling cells are marked as inactive in ACTNUM."""

from petres.grids import CornerPointGrid, PillarGrid
from petres.interpolators import IDWInterpolator
from petres.models import Zone, Horizon
import numpy as np

# Create horizons with a gap between h2 and h3
h1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[0,1,0,1], interpolator=IDWInterpolator())
h2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[2,2,3,3], interpolator=IDWInterpolator())
h3 = Horizon("H3", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[5,7,8,4], interpolator=IDWInterpolator())
h4 = Horizon("H4", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[11,14,13,12], interpolator=IDWInterpolator())

zones = [
  Zone("Caprock", top=h1, base=h2).divide(nk=2),  # 2 layers
  Zone("Base", top=h3, base=h4).divide(nk=2),      # 2 layers
]
# Gap between h2 (depth~2-3) and h3 (depth~5-8) should create 1 inactive layer

pillars = PillarGrid.from_regular(xlim=(0,100), ylim=(0,100), ni=10, nj=10, top=0, base=10)
grid = CornerPointGrid.from_zones(pillars=pillars, zones=zones)

print(f"Grid shape (nk, nj, ni): {grid.shape}")
print(f"Total cells: {grid.n_cells}")
print(f"Active cells: {grid.n_active}")
print(f"Inactive cells: {grid.n_cells - grid.n_active}")

# Check ACTNUM structure by layer
print("\nACTNUM by layer:")
for k in range(grid.nk):
    active_count = np.sum(grid.active[k, :, :])
    total_count = grid.ni * grid.nj
    status = "ACTIVE" if active_count == total_count else "INACTIVE"
    print(f"  Layer {k}: {active_count}/{total_count} cells active -> {status}")

# Verify expected structure: [ACTIVE, ACTIVE, INACTIVE, ACTIVE, ACTIVE]
expected_pattern = [True, True, False, True, True]
actual_pattern = [np.all(grid.active[k, :, :]) for k in range(grid.nk)]

print(f"\nExpected pattern: {expected_pattern}")
print(f"Actual pattern:   {actual_pattern}")
print(f"Match: {expected_pattern == actual_pattern}")

# Test export/import round-trip
print("\nTesting GRDECL export/import...")
import tempfile
import os
with tempfile.TemporaryDirectory() as tmpdir:
    export_path = os.path.join(tmpdir, "test_gap.grdecl")
    grid.to_grdecl(export_path)
    grid2 = CornerPointGrid.from_grdecl(export_path)
    print(f"Exported and re-imported successfully")
    print(f"Active cells match: {grid2.n_active == grid.n_active}")
    print(f"ACTNUM arrays equal: {np.array_equal(grid.active, grid2.active)}")
