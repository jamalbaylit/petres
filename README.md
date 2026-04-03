<div align="center">

![Banner](./assets/banner-high.png)
<em>
    A lightweight, open-source Python library for reservoir grid modeling
</em>

[![License](https://img.shields.io/badge/License-LGPL%20v3%2B-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://petres.readthedocs.io)

</div>


# Introduction

Petres is a lightweight, open-source Python library for reservoir grid modeling, providing a fully programmatic approach to constructing Corner-Point grid models.

For complete documentation, see the [Petres documentation](https://petres.readthedocs.io/).

> **Stability Notice**  
> Petres is currently in early development. The API is not yet stable and may change without notice.


## Why Petres?

- **Open Access:** Free alternative for engineers and students without access to expensive commercial softwares.

- **Scriptable Modeling:** Avoid UI complexity and work with code-driven workflows.

- **Fully Customizable:** Integrate your own code alongside built-in methods.

- **AI Integration:** Use the Python ecosystem to apply AI and Machine Learning techniques.

## Features

- **Grid Generation:** Construct Corner-Point, Rectilinear, and Regular grids.  
Apply boundary polygons to deactivate cells outside the target region.  

- **Structural Modeling:** Generate horizon and zone surfaces from well tops to support grid construction.  

- **Property Modeling:** Assign petrophysical properties to grid cells using stochastic or deterministic methods, derived attributes, or interpolation from well data.  

- **Import & Export Grids:** Handle SLB Eclipse reservoir simulation grids using the `.GRDECL` file format. Import, visualize, and export grids within modeling workflows.  

- **Visualization:**
Interactive 2D and 3D rendering of Corner-Point grids, structural zones, horizons, and spatial property distributions.  


## Getting Started

To get started with Petres, refer to the [Installation Guide](https://petres.readthedocs.io/en/latest/getting-started/installation.html) and the [Quickstart Tutorial](https://petres.readthedocs.io/en/latest/getting-started/quickstart.html).  



## Technical Architecture

<table width="100%">
  <tr>
    <th>Component</th>
    <th>Implementation</th>
  </tr>
  <tr>
    <td>Grid Operations</td>
    <td>High-performance, vectorized array computations using NumPy &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
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






## Contact

For questions or collaboration, please contact [jamalbaylit@gmail.com](mailto:jamalbaylit@gmail.com) or connect via [LinkedIn](https://www.linkedin.com/in/jamalbaylit).