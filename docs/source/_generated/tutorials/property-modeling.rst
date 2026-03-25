Property Modeling
=================

Build and apply grid-based property distributions.

**Difficulty:** intermediate
**Tags:** property, modeling

These examples show how to create and apply properties on grids.

See :class:`petres.property.GridProperty` and related APIs.

Create a property distribution
------------------------------

Start with a general property distribution workflow.

**Source:** ``examples/create_property_distribution.py``

.. code-block:: python

   from petres.interpolators import IDWInterpolator
   from petres.grids import GridProperty 
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
   

Apply constant properties
-------------------------

These examples show constant-value assignments over different supports.

Constant value in the full grid
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/property_modeling/constant_full_grid.py``

.. code-block:: python

   from petres.grids import CornerPointGrid
   import numpy as np
   
   # Create grid
   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )
   
   # Assign constant porosity to whole grid
   porosity = grid.properties.create(
       "poro",
       eclipse_keyword="PORO",
       description="Porosity"
   )
   
   porosity.fill(0.20)
   porosity.show(show_inactive=False)
   # Access
   
   print("Min Value:", porosity.min)
   print("Max Value:", porosity.max)
   print("Mean Value:", porosity.mean)
   print("Median Value:", porosity.median)
   print("Standard Deviation:", porosity.std)
   print("Shape:", porosity.values.shape)

Constant value per zone
^^^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/property_modeling/constant_per_zone.py``

.. code-block:: python

   from petres.grids import CornerPointGrid, PillarGrid
   from petres.interpolators import IDWInterpolator
   from petres.models import Zone, Horizon
   from petres.viewers import Viewer3D
   import numpy as np
   
   h1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], z=[0,1,0,1], interpolator=IDWInterpolator())
   h2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], z=[2,2,3,3], interpolator=IDWInterpolator())
   h3 = Horizon("H3", xy=[[0,0],[100,0],[100,100],[0,100]], z=[5,7,8,4], interpolator=IDWInterpolator())
   h4 = Horizon("H4", xy=[[0,0],[100,0],[100,100],[0,100]], z=[11,14,13,12], interpolator=IDWInterpolator())
   viewer = Viewer3D()
   viewer.add_horizon(h1, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="red")
   viewer.add_horizon(h2, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="green")
   viewer.add_horizon(h3, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="blue")
   viewer.add_horizon(h4, x=np.linspace(0,100,50), y=np.linspace(0,100,50), color="purple")
   viewer.show()
   
   zones = [
     Zone("Caprock", top=h1, base=h2).divide(fractions=[0.2,0.3,0.5]),
     # Zone("Reservoir", top=h2, base=h3).divide(fractions=[0.2,0.3,0.5]),
     Zone("Base", top=h3, base=h4).divide(nk=3),
   ]
   viewer.add_zones(zones, x=np.linspace(0,100,50), y=np.linspace(0,100,50), colormap="viridis", show_layers=True)
   viewer.show()
   
   pillars = PillarGrid.from_regular(xlim=(0,100), ylim=(0,100), ni=50, nj=50)
   grid = CornerPointGrid.from_zones(pillars=pillars, zones=zones)
   grid.show(show_inactive=False)
   
   
   porosity = grid.properties.create(
       "poro",
       eclipse_keyword="PORO",
       description="Porosity"
   )
   
   porosity.fill(0.20, zone="Caprock")
   porosity.fill(0.5, zone="Base")
   
   porosity.show(show_inactive=False)
   
   
   
   
   
   
   
   
   

Build properties from wells and statistical models
--------------------------------------------------

Generate properties from samples or stochastic distributions.

Property modeling from wells
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/property_modeling/from_wells.py``

.. code-block:: python

   from petres.interpolators import IDWInterpolator, RBFInterpolator, OKInterpolator, UKInterpolator
   from petres.grids import CornerPointGrid
   from petres.models import VerticalWell
   import numpy as np
   
   well1 = VerticalWell(name="Well 1", x=20, y=78)
   well3 = VerticalWell(name="Well 3", x=32, y=55)
   
   well1.add_sample('porosity', 100, 3)
   well1.add_sample('porosity', 50, 12)
   well1.add_sample('porosity', 25, 20)
   
   
   
   
   
   
   grid = CornerPointGrid.from_regular(
       xlim=(0, 100),
       ylim=(0, 100),
       zlim=(0, 20),
       ni=100,
       nj=100,
       nk=10,
   )
   grid.show()
   
   
   porosity = grid.properties.create(
       name='porosity',
       eclipse_keyword='PORO',
       description='Porosity'
   )
   porosity.from_wells(
       wells=[well1, well3],
       # interpolator=OKInterpolator(),
       interpolator=UKInterpolator(),
       mode='xyz'
   )
   porosity.show()

Normal distribution example
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/property_modeling/normal_distribution.py``

.. code-block:: python

   from petres.grids import CornerPointGrid
   import numpy as np
   
   # Create grid
   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )
   
   porosity = grid.properties.create(name="poro", eclipse_keyword="PORO", description="Porosity")
   
   porosity.fill_normal(mean=0.24, std=0.03, min=0.0, max=0.35)
   porosity.show(show_inactive=False)

Lognormal distribution example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Source:** ``examples/property_modeling/lognormal_distribution.py``

.. code-block:: python

   from petres.grids import CornerPointGrid
   import numpy as np
   
   # Create grid
   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )
   
   porosity = grid.properties.create(name="poro", eclipse_keyword="PORO", description="Porosity")
   
   porosity.fill_lognormal(mean=0.24, std=0.03, min=0.0, max=0.35)
   porosity.show(show_inactive=False)

Apply a property model
----------------------

Apply the generated property model to the target grid.

**Source:** ``examples/property_modeling/apply.py``

.. code-block:: python

   from petres.grids import CornerPointGrid
   import numpy as np
   
   # Create grid
   grid = CornerPointGrid.from_regular(
       xlim=(0, 1000),
       ylim=(0, 1000),
       zlim=(0, 100),
       ni=20,
       nj=20,
       nk=3,
   )
   
   # Assign constant porosity to whole grid
   porosity = grid.properties.create(
       "poro",
       eclipse_keyword="PORO",
       description="Porosity"
   )
   
   porosity.fill(0.20)
   porosity.show(show_inactive=False)
   
   
   
   permeability = grid.properties.create(
       "perm",
       eclipse_keyword="PERM",
       description="Permeability"
   )
   permeability.apply(lambda poro: 100 * poro**3, source="top")
   permeability.show(show_inactive=False)
