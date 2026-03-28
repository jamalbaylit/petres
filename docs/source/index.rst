Petres
======

**Petres** is an open-source Python library designed for **reservoir engineers**
to build, analyze, and visualize **Eclipse-compatible corner-point grids**
and subsurface models.

It provides a **fully scriptable alternative** to commercial reservoir modeling
software (e.g., Petrel), enabling users to generate and manipulate reservoir
grids using only Python — without relying on graphical user interfaces.

Petres is particularly suited for engineers and researchers who:

- Do not have access to expensive proprietary software  
- Prefer reproducible, code-driven workflows  
- Require full control over grid geometry and simulation inputs  

.. note::

   Petres focuses on **structured grids** and **corner-point grid systems**
   commonly used in reservoir simulation workflows.



.. figure:: _static/images/cpg_example.png
   :align: center
   :width: 75%

   Example corner-point grid representation.



Quick Start
-----------

Install Petres:

.. code-block:: bash

   pip install petres

Create a simple grid:

.. code-block:: python

   from petres.grid import CornerPointGrid

   grid = CornerPointGrid.from_rectilinear(
       x=[0, 100, 200],
       y=[0, 100],
       z=[0, -50, -100],
   )

   grid.plot()



What You Can Do with Petres
---------------------------

Petres provides a programmatic workflow for building reservoir models
from the ground up:

- Generate **corner-point grids** compatible with Eclipse simulators  
- Define **pillar geometry** and explicitly control grid topology  
- Construct grids from **rectilinear inputs or custom geometries**  
- Create and manage **horizons and zones** using interpolation methods  
- Assign and manipulate **cell-based properties**  
- Export grid data in **GRDECL format** (COORD, ZCORN, ACTNUM)  
- Visualize grids and properties in 3D  

This enables fully reproducible reservoir modeling workflows entirely within Python.



Core Capabilities
-----------------

.. grid:: 2
   :gutter: 3

   .. grid-item-card:: 🧱 Grid Modeling
      Build structured and corner-point grids with full control over geometry.

   .. grid-item-card:: 🌍 Horizons and Zones
      Define subsurface structure using interpolation-based surfaces.

   .. grid-item-card:: ⚙️ Eclipse Compatibility
      Read and write GRDECL data (COORD, ZCORN, ACTNUM).

   .. grid-item-card:: 📊 Visualization
      Interactive 3D visualization using modern Python tools.



Design Philosophy
-----------------

Petres is built around a **code-first modeling approach**:

- No GUI dependencies  
- Full control over data and geometry  
- Reproducible and version-controlled workflows  

Rather than replacing graphical tools, Petres complements them by enabling
automation, experimentation, and integration with modern data science pipelines.



Where to go next
----------------

- :doc:`Getting Started <getting_started/quickstart>`
- :doc:`Fundamentals <fundamentals/grid-classification>`
- :doc:`Tutorials <tutorials>`
- :doc:`Examples <examples>`
- :doc:`API Reference <api/index>`



Learn the Fundamentals
----------------------

Petres documentation includes detailed technical explanations of
reservoir grid systems, designed both as a reference and as educational material:

- Structured vs unstructured grids  
- Rectilinear, regular, and Cartesian grids  
- Corner-point grid geometry  
- Eclipse data representation (COORD, ZCORN, ACTNUM)

👉 Start here: :doc:`Grid Types in Reservoir Simulation <fundamentals/grid-types>`



.. note::

   Petres is under active development. Contributions, feedback,
   and collaboration are welcome.



.. toctree::
   :maxdepth: 2
   :caption: Getting Started
   :hidden:

   getting-started/installation
   getting-started/quickstart


.. toctree::
   :maxdepth: 2
   :caption: Fundamentals
   :hidden:

   fundamentals/grid-classification
   fundamentals/grid-types
   fundamentals/corner-point-grids

.. toctree::
   :maxdepth: 3
   :caption: User Guide
   :hidden:

   tutorials/index
   examples
   api/index


