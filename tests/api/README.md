"""API Tests for Petres - Summary and Guide

This document describes the comprehensive API test suite created based on your tutorials. The tests validate that all Petres APIs work as documented and don't crash, organized by user workflow categories with examples from each tutorial.

## Overview

The tests/api/ folder contains 88+ test cases organized by user workflow categories,
ensuring all Petres API functionalities work without crashing.

## Test Organization

### 1. Grid Creation Tests (test_grid_creation.py)
Tests for creating different types of grids:
- Rectilinear grids with non-uniform spacing
- Regular grids by cell count or cell size  
- Pillar grids (regular and rectilinear)
- Grid summary method validation

**Tutorials covered:**
- docs/source/tutorials/rectilinear-and-regular-grids.rst
- docs/source/tutorials/pillar-gridding.rst

### 2. Horizon and Zone Modeling Tests (test_horizon_zone_modeling.py)
Tests for structural surface creation:
- Creating horizons from sample points with different interpolators
- Creating horizons from well tops
- Evaluating horizons at arbitrary points
- Creating zones from horizons
- Zone layering (uniform, fractional, explicit levels)
- Complete workflows from well data to zones

**Tutorials covered:**
- docs/source/tutorials/horizon-modeling.rst
- docs/source/tutorials/zone-modeling.rst
- docs/source/tutorials/grid-modeling-from-horizons-and-zones.rst

### 3. Boundary Polygon Tests (test_boundary_polygon.py)
Tests for spatial masking:
- Creating boundary polygons from vertices and bounding boxes
- Applying boundaries to grids
- Verifying cell deactivation
- Boundaries on zone-based grids

**Tutorials covered:**
- docs/source/tutorials/boundary-polygon.rst

### 4. Property Modeling Tests (test_property_modeling.py)
Tests for grid property assignment:
- Property creation and access
- Filling properties with constant values
- Stochastic distributions (normal, uniform, lognormal)
- Deriving properties from other properties
- Populating from well data via interpolation
- Property statistics

**Tutorials covered:**
- docs/source/tutorials/property-modeling.rst

### 5. Grid Import/Export Tests (test_grid_import_export.py)
Tests for Eclipse GRDECL file I/O:
- Exporting grids to GRDECL
- Exporting with/without ACTNUM
- Exporting properties
- Importing grids and properties
- Export-import roundtrip validation
- Modifying imported grids

**Tutorials covered:**
- docs/source/tutorials/importing-grid.rst
- docs/source/tutorials/exporting-grid.rst

### 6. Grid Visualization Tests (test_grid_visualization.py)
Tests for visualization APIs (using mocked displays):
- Grid visualization with various parameters
- Property visualization
- Horizon/Zone visualization
- Boundary polygon visualization
- Custom colormaps and titles

**Tutorials covered:**
- docs/source/tutorials/grid-visualization.rst

**Note:** Visualization tests are marked with `@pytest.mark.viewer` and use
mocked display backends to avoid hanging on window creation. Run with:
    pytest -m viewer tests/api/test_grid_visualization.py

### 7. Complete Workflows Tests (test_complete_workflows.py)
Integration tests demonstrating full user workflows:
- Grid creation to property modeling
- Rectilinear grids with stochastic properties
- Horizon/zone/grid construction
- Boundary application with properties
- Import-export with boundaries
- Well data interpolation to properties
- Complete reservoir model creation from scratch

## Running Tests

### Run all API tests:
    pytest tests/api/ -v

### Run specific test file:
    pytest tests/api/test_grid_creation.py -v

### Run specific test class:
    pytest tests/api/test_grid_creation.py::TestRectilinearGridCreation -v

### Run specific test:
    pytest tests/api/test_grid_creation.py::TestRectilinearGridCreation::test_create_simple_rectilinear_grid -v

### Skip visualization tests (for CI/headless environments):
    pytest tests/api/ -v -m "not viewer"

### Run only visualization tests:
    pytest tests/api/ -v -m viewer

## Test Coverage

- **Grid Creation Workflows**: ✓ All tutorial examples covered
- **Modeling Workflows**: ✓ Horizons, zones, and layering
- **Boundary Masking**: ✓ Polygon creation and application
- **Property Assignment**: ✓ All distribution and derivation methods
- **File I/O**: ✓ Import/export roundtrips
- **Visualization**: ✓ API validation with mocked display
- **End-to-End**: ✓ Complex multi-step workflows

## Key Features

1. **Tutorial-Aligned**: Each test class maps directly to a user tutorial
2. **Non-Blocking**: Visualization tests use mocking to prevent hanging
3. **Comprehensive**: Covers all major user workflows from docs
4. **Clear Structure**: Tests organized by functionality for easy navigation
5. **Validation**: All tests verify API doesn't crash and returns expected types

## Notes for Users

- Tests validate that APIs work as documented
- Visualization tests verify methods exist and accept correct parameters
- Property tests validate both creation and statistical accuracy
- Import/export tests ensure data roundtrip integrity
- Well-based workflows test interpolation accuracy

## Future Enhancements

Potential additions for more complete coverage:
- 2D visualization workflows
- Advanced property transformations
- Custom interpolator implementations
- Grid fault/skew scenarios
- Performance benchmarks
"""