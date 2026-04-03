<div align="center">

![Banner](./assets/banner-high.png)

[![License](https://img.shields.io/badge/License-LGPL%20v3%2B-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0.html)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://petres.readthedocs.io)

</div><br>


# Introduction

Petres is a lightweight, open-source Python library for reservoir grid modeling, providing a fully programmatic approach to constructing Corner-Point grid models.

For detailed documentation, https://petres.readthedocs.io/


> Petres is currently in early development. The API should be considered unstable and may change without notice.

---

## Features

### Grid Generation
Construct Corner-Point, Rectilinear, and Regular grids.  
Apply boundary polygons to deactivate cells outside the target region.  
[View tutorial](docs/tutorials/rectilinear-and-regular-grids.md)

### Structural Modeling
Generate horizon and zone surfaces from well tops to support grid construction.  
[View tutorial](docs/tutorials/grid-modeling-from-horizons-and-zones.md)

### Property Modeling
Assign petrophysical properties to grid cells using stochastic or deterministic methods, derived attributes, or interpolation from well data.  
[View tutorial](docs/tutorials/property-modeling.md)

### Import & Export Grids
Handle SLB Eclipse reservoir simulation grids using the `.GRDECL` file format.  
Import, visualize, and export grids within modeling workflows.  
[View tutorial](docs/tutorials/exporting-grid.md)

### Visualization
Interactive 2D and 3D rendering of Corner-Point grids, structural zones, horizons, and spatial property distributions.  
[View documentation](docs/visualizing-the-grid.md)

---

## Why Petres

- Open access alternative to commercial reservoir modeling software  
- Fully scriptable workflows using Python  
- Designed for extensibility and integration  
- Compatible with AI and machine learning pipelines  

---

## Technical Architecture


| Component | Implementation |
| --- | --- | 
| Grid Operations | High-performance, vectorized array computations using NumPy |
| 2D Plotting | Visualization via Matplotlib |
| 3D Visualization | Interactive rendering and mesh handling via PyVista |
| Kriging Interpolation | Ordinary and Universal Kriging via PyKrige |
| RBF Interpolation | Multi-dimensional Radial Basis Function interpolation via SciPy |
| IDW Interpolation | In-house implementation of Inverse Distance Weighting |


---

## Getting Started

- [Installation Guide](docs/getting-started/installation.md)  
- [Quickstart Tutorial](docs/getting-started/quickstart.md)  

Source code:  
https://github.com/jamalbaylit/petres

---

## Contact

- Email: jamalbaylit@gmail.com  
- LinkedIn: https://www.linkedin.com/in/jamalbaylit  

---

