Welcome to Petres
=================

Petres is a lightweight, open-source Python library for reservoir grid modeling, 
providing a fully programmatic approach to constructing :ref:`Corner-Point grid <corner-point-grid>` models. 


.. important::
   
   Petres is currently in early development. 
   The API is not yet stable and may change without notice.


Features
--------

.. grid:: 1 1 2 2
   :gutter: 3

   .. grid-item-card:: 
      :link: tutorials/rectilinear-and-regular-grids
      :link-type: doc
      :class-card: grid-item-card

      .. grid-item-header:: _static/svg/grid.svg
         :svg: grid-item-icon
         :title: Grid Generation

      Construct Corner-Point, Rectilinear, and Regular grids. 
      Apply boundary polygons to deactivate cells outside the target region.

 
   .. grid-item-card::
      :link: tutorials/grid-modeling-from-horizons-and-zones
      :link-type: doc
      :class-card: grid-item-card

      .. grid-item-header:: _static/svg/structure.svg
         :svg: grid-item-icon
         :title: Structural Modeling

      Generate horizon and zone surfaces from well tops to support grid construction.


   .. grid-item-card::
      :link: tutorials/property-modeling
      :link-type: doc
      :class-card: grid-item-card

      .. grid-item-header:: _static/svg/property.svg
         :svg: grid-item-icon
         :title: Property Modeling


      Assign petrophysical properties to grid cells using stochastic or deterministic methods, derived attributes, or interpolation from well data.



   .. grid-item-card::
      :link: tutorials/exporting-grid
      :link-type: doc
      :class-card: grid-item-card

      .. grid-item-header:: _static/svg/export.svg
         :svg: grid-item-icon
         :title: Import & Export Grids

      Handle Eclipse grids (SLB reservoir simulator) 
      using the ``.GRDECL`` file format. Visualize
      and export modeled Corner-Point grids.


   .. grid-item-card:: 
      :link: visualizing-the-grid
      :link-type: ref
      :class-card: grid-item-card

      .. grid-item-header:: _static/svg/visualization.svg
         :svg: grid-item-icon
         :title: Visualization

      Interactive 2D and 3D rendering of Corner-Point grids, structural zones, horizons, and spatial property distributions.


Why Petres?
-----------

- **Open Access:** Free alternative for engineers and students without access to expensive commercial softwares.

- **Scriptable Modeling:** Avoid UI complexity and work with code-driven workflows.

- **Fully Customizable:** Integrate your own code alongside built-in methods.

- **AI Integration:** Use the Python ecosystem to apply AI and Machine Learning techniques.



Technical Architecture
----------------------

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Component
     - Implementation
   * - Grid Operations
     - High-performance, vectorized array computations using *NumPy*.
   * - 2D Plotting
     - 2D plots are generated via the *Matplotlib*.
   * - 3D Visualization
     - Interactive 3D rendering and mesh visualization via *PyVista*.
   * - Kriging Interpolation
     - :ref:`Ordinary and Universal Kriging <kriging-interpolation>` implemented via *PyKrige*.
   * - RBF Interpolation
     - Multi-dimensional :ref:`Radial Basis Function <rbf-interpolation>` interpolation utilizing *SciPy*.
   * - IDW Interpolation
     - In-house implementation for :ref:`Inverse Distance Weighting <idw-interpolation>`.
   


Getting Started
---------------
Start modeling with Petres by following the :doc:`Installation Guide <getting-started/installation>` 
and the :doc:`Quickstart Tutorial <getting-started/quickstart>`.
The source code is also available on GitHub: `Petres Repository <https://github.com/jamalbaylit/petres>`_.

Contact
-------
For questions, suggestions, or collaboration, feel free to reach out:

- **Email:** jamalbaylit@gmail.com  
- **LinkedIn:** `Tayfun Jamalbayli <https://www.linkedin.com/in/jamalbaylit>`_










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
   api/index


