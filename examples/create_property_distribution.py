from petres.interpolators import IDWInterpolator
from petres.grids import CellProperty 
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


distribution = pd.DataFrame({
    "x": [100, 200, 300],
    "y": [100, 200, 300],
    "value": [10, 20, 30],
})

xx, yy = np.meshgrid(np.linspace(0, 400, 50), np.linspace(0, 400, 50))

grid_points = np.column_stack([xx.ravel(), yy.ravel()])
print(grid_points.shape)  # (2500, 2)

interpolator = IDWInterpolator(power=3.0, neighbors=3)
interpolator.fit(distribution[["x", "y"]].values, distribution["value"].values)
interpolated_values = interpolator.predict(grid_points).reshape(xx.shape)

# plot
plt.figure(figsize=(8, 6))
plt.contourf(xx, yy, interpolated_values, levels=50, cmap="viridis")
plt.scatter(distribution["x"], distribution["y"], c=distribution["value"], edgecolor="k", s=100, cmap="viridis")
plt.colorbar(label="Interpolated Value")
plt.title("IDW Interpolation of Property Distribution")
plt.xlabel("X")
plt.ylabel("Y")
plt.show()


# pressure = CellProperty(
#     values=np.random.rand(10, 20, 30),
#     eclipse_keyword="PRESSURE",
#     name="Pressure",
#     description="Pressure distribution in the reservoir"
# )

