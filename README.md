<div align="center">

![Banner](https://raw.githubusercontent.com/jamalbaylit/petres/main/assets/banner.png)



<p>
  <em>
    <strong> 
      Lightweight Python Library for Static Reservoir Modeling
    </strong>
  </em>
</p>


<p>
  <a href="https://petres.readthedocs.io/en/latest/index.html">Documentation</a> •
  <a href="https://petres.readthedocs.io/en/latest/getting-started/installation.html">Installation</a> •
  <a href="https://petres.readthedocs.io/en/latest/getting-started/quickstart.html">Quick Start</a>
</p>

[![License](https://img.shields.io/badge/License-LGPL%20v3%2B-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)
[![Python Version](https://img.shields.io/badge/python-3.10%E2%80%933.14-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://petres.readthedocs.io)

</div>


# Introduction

Petres is a lightweight, open-source Python library for corner-point reservoir grid generation, property modeling, and visualization. It provides a fully code-driven workflow for static reservoir modeling.

For complete documentation, see the [Petres documentation](https://petres.readthedocs.io/).

> **Stability Notice**  
> Petres is currently in early development. The API is not yet stable and may change without notice.


# Why Petres?

- **Open Access:** Free alternative for engineers and students without access to expensive commercial softwares.

- **Scriptable Modeling:** Avoid UI complexity and work with code-driven workflows.

- **Fully Customizable:** Integrate your own code alongside built-in methods.

- **AI Integration:** Use the Python ecosystem to apply AI and Machine Learning techniques.

# Features

- **Grid Generation:** Construct Corner-Point, Rectilinear, and Regular grids.  
Apply boundary polygons to deactivate cells outside the target region.  

- **Structural Modeling:** Generate horizon and zone surfaces from well tops to support grid construction.  

- **Property Modeling:** Assign petrophysical properties to grid cells using stochastic or deterministic methods, derived attributes, or interpolation from well data.  

- **Import & Export Grids:** Handle Eclipse grids (SLB reservoir simulator) using the ``.GRDECL`` file format. Visualize and export modeled Corner-Point grids.

- **Visualization:**
Interactive 2D and 3D rendering of Corner-Point grids, structural zones, horizons, and spatial property distributions.  


# Installation

Full installation instructions are available in the [documentation](https://petres.readthedocs.io/en/latest/getting-started/installation.html).

# Quickstart

Import and visualize a corner-point grid from a `.GRDECL` file:

```python
from petres.grids import CornerPointGrid

# Define the path to the ".GRDECL" file containing the grid data
path = r"https://raw.githubusercontent.com/jamalbaylit/petres/v0.1.0/data/opm/norne/grdecl/norne_with_props.grdecl"

# Import corner-point grid from a ".GRDECL" file, including specified properties
grid = CornerPointGrid.from_grdecl(
  path, 
  properties=["PORO", "PERMX"]
)

# Visualize grid
grid.show(scalars="depth", z_scale=5)

# Visualize property
grid.show(scalars="PORO", z_scale=5)
```


# Technical Architecture
<div align="center">
<table width="100%">
  <tr>
    <th>Component</th>
    <th>Implementation</th>
  </tr>
  <tr>
    <td>Grid Operations</td>
    <td>High-performance, vectorized array computations using NumPy</td>
  </tr>
  <tr>
    <td>2D Plotting</td>
    <td>Visualization via Matplotlib</td>
  </tr>

  <tr>
    <td>3D Visualization</td>
    <td>Interactive rendering and mesh handling via PyVista</td>
  </tr>
  <tr>
    <td>Kriging Interpolation</td>
    <td>Ordinary and Universal Kriging via PyKrige</td>
  </tr>
  <tr>
    <td>RBF Interpolation</td>
    <td>Multi-dimensional Radial Basis Function interpolation via SciPy</td>
  </tr>
  <tr>
    <td>IDW Interpolation</td>
    <td>In-house implementation of Inverse Distance Weighting</td>
  </tr>
</table>
</div>


# Contact

For questions, bug reports, or collaboration opportunities contact via [jamalbaylit@gmail.com](mailto:jamalbaylit@gmail.com) or connect via [LinkedIn](https://www.linkedin.com/in/jamalbaylit).