Grid Modeling from Horizons and Zones
=====================================

This tutorial demonstrates how to construct a **Corner-Point grid**
from pre-defined horizons and zones.
It assumes prior familiarity with :doc:`horizon modeling <horizon-modeling>`, 
:doc:`zone modeling <zone-modeling>`, and :doc:`pillar gridding <pillar-gridding>`.
The focus here is on combining these components into a complete
grid generation.


Workflow
--------

The workflow follows a structured sequence:

.. code-block:: text

   (Horizons → Zones → Layering) + Pillars → Corner-Point Grid

Each component contributes to a different aspect of the final grid:

- Horizons: Define structural surfaces used to construct zones
- Zones: Define vertical intervals derived from horizons
- Layering: Controls vertical resolution within each zone
- Pillars: Define the lateral grid geometry and cell alignment


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
   grid.show()

.. note::
   For more advanced visualization options refer to :doc:`grid-visualization`.

The zone boundaries and zone layers define the vertical resolution of the grid, 
while the pillars determine the horizontal :math:`(x, y)` resolution.  
If the provided zones are not touching, the grid will include a single layer of inactive cells between them.

.. important::
   The grid construction process assumes that the provided zones are **not** overlapping or intersecting. 
   It is perfectly fine if zone boundaries share the same horizon.


Next Steps
----------

- :doc:`grid-visualization`
- :doc:`property-modeling`
- :doc:`boundary-polygon`
- :doc:`mapping-wells-to-grid-cells`
- :doc:`exporting-grid`