Grid Modeling from Horizons and Zones
=====================================

This tutorial demonstrates how to construct a **Corner-Point grid**
from pre-defined horizons and zones.
It assumes prior familiarity with :doc:`horizon modeling <horizon-modeling>`, 
:doc:`zone modeling <zone-modeling>`, and :doc:`pillar gridding <pillar-gridding>`.
The focus here is on combining these components into a complete
grid generation.


Workflow Summary
----------------

The workflow follows a structured sequence:

.. code-block:: text

   (Horizons → Zones → Layering) + Pillars → Corner-Point Grid

Each component contributes to a different aspect of the final grid:

- Horizons → Define structural surfaces used to construct zones
- Zones → Define vertical intervals derived from horizons
- Layering → Controls vertical resolution within each zone
- Pillars → Define the lateral grid geometry and cell alignment


Input Preparation
-----------------

First you need to define zones and pillar geometry:

Example setup:

.. code-block:: python

   from petres.interpolators import IDWInterpolator
   from petres.models import Horizon, Zone

   h1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[0,1,0,1], interpolator=IDWInterpolator())
   h2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], depth=[2,2,3,3], interpolator=IDWInterpolator())

   zone = Zone(name="Reservoir", top=h1, base=h2).divide(nk=4)

   from petres.grids import PillarGrid

   pillars = PillarGrid.from_regular(
      xlim=(0, 100),
      ylim=(0, 100),
      ni=50,
      nj=50,
   )

For detailed explanations, see :doc:`horizon-modeling`, :doc:`zone-modeling`, and :doc:`pillar-gridding`.

Building the Grid
-----------------

The grid is constructed by simply combining the pillar grid
with the zones using the  :meth:`~petres.grids.CornerPointGrid.from_zones` method:

.. code-block:: python

   from petres.grids import CornerPointGrid

   grid = CornerPointGrid.from_zones(
      pillars=pillars,
      zones=[zone],
   )

This step integrates:

- Lateral geometry from pillars
- Vertical layering from zones
- Surface geometry from horizons


.. _visualizing-the-grid:

Visualizing the Grid
--------------------

.. code-block:: python

   grid.show()

Optional:

.. code-block:: python

   grid.show(show_inactive=False)


Key Observations
----------------

- Grid layering follows the subdivision defined in each zone
- Cell geometry conforms to interpolated horizon surfaces
- Pillar spacing controls lateral resolution
- Vertical resolution is controlled independently via zone layering


Where to Go Next
----------------

After constructing the grid, typical next steps include:

- Assigning properties → :doc:`grid-properties`
- Exporting the model → :doc:`exporting-grid`
- Exploring advanced workflows → :doc:`../api/index`