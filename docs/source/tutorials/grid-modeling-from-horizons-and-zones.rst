Grid Modeling from Horizons and Zones
=====================================

Overview
--------

This tutorial demonstrates how to construct a **corner-point grid**
from pre-defined horizons and zones.

It assumes familiarity with:

- Horizon modeling → :doc:`horizon-modeling`
- Zone definition and layering → :doc:`zone-modeling`
- Pillar grid construction → :doc:`pillar-grid-modeling`

The focus here is on **combining these components into a complete
grid modeling workflow**.


Workflow Summary
----------------

The workflow follows a structured sequence:

.. code-block:: text

   Horizons → Zones → Layering → Pillars → Corner-Point Grid

Each component contributes to a different aspect of the final grid:

- Horizons → define structural surfaces
- Zones → define vertical intervals
- Layering → defines vertical resolution
- Pillars → define lateral structure


Input Preparation
-----------------

In this tutorial, we assume that:

- Horizons are already defined
- Zones are created between horizons
- Zones are subdivided into layers

Example setup:

.. code-block:: python

   from petres.models import Horizon, Zone
   from petres.interpolators import IDWInterpolator

   h1 = Horizon("H1", xy=[[0,0],[100,0],[100,100],[0,100]], z=[0,1,0,1], interpolator=IDWInterpolator())
   h2 = Horizon("H2", xy=[[0,0],[100,0],[100,100],[0,100]], z=[2,2,3,3], interpolator=IDWInterpolator())

   zone = Zone(name="Reservoir", top=h1, base=h2).divide(nk=4)

.. note::

   For detailed explanations of horizons and zones, refer to:

   - :doc:`horizon-modeling`
   - :doc:`zone-modeling`


Creating the Pillar Grid
------------------------

The pillar grid defines the lateral structure of the model.

.. code-block:: python

   from petres.grids import PillarGrid

   pillars = PillarGrid.from_regular(
       xlim=(0, 100),
       ylim=(0, 100),
       ni=50,
       nj=50,
   )

.. note::

   See :doc:`pillar-grid-modeling` for detailed pillar grid workflows.


Building the Corner-Point Grid
------------------------------

The corner-point grid is constructed by combining the pillar grid
with the layered zones:

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