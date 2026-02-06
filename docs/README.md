# Sphinx Documentation System

## Overview

This is a **100% automatic** Sphinx documentation system that generates complete API reference documentation from your Python package's `__all__` exports. No manual `.rst` files, no hardcoded lists, no manual updates needed.

## Features

✅ **Fully Automatic** - All documentation generated at build time  
✅ **Alias Detection** - Automatically detects and displays object aliases  
✅ **Smart Categorization** - Groups objects by their defining module  
✅ **NumPy Docstrings** - Configured for NumPy-style documentation  
✅ **Clean Navigation** - Human-friendly category names, no "module" terminology  
✅ **Zero Maintenance** - Just add objects to `__all__` and rebuild  

## How It Works

### 1. Discovery Phase
The `apigen` extension recursively walks your package structure, following `__all__` declarations:
- Imports your package
- Recursively discovers all objects in `__all__`
- Tracks object identity to detect aliases
- Categorizes based on the module where each object is **defined**

### 2. Generation Phase
For each discovered object, generates:
- **Category pages** - One per module/category (e.g., "Grids", "Interpolators")
- **Object pages** - One per canonical object with full autodoc
- **Alias sections** - Shows all alternative names for each object
- **API index** - Main landing page with category navigation

### 3. Categorization Logic
Categories are derived from the module where an object is defined:
- `petromod.grids.rectilinear.Rectilinear2DGrid` → **Grids** category
- `petromod.interpolators.spatial.IDWInterpolator` → **Interpolators** category
- Module names are converted to Title Case for display

### 4. Alias Handling
When the same object is exported under multiple names:
- The **first encountered name** becomes canonical
- All other names are tracked as aliases
- Only one page is generated (no duplicates)
- Aliases are prominently displayed at the top of each object page
- Sidebar shows only canonical names

## File Structure

```
docs/
├── Makefile                    # Unix/Linux build commands
├── make.bat                    # Windows build commands
├── source/
│   ├── conf.py                 # Sphinx configuration
│   ├── index.rst               # Main documentation page
│   ├── _static/                # Custom CSS/JS (optional)
│   └── _ext/
│       ├── __init__.py
│       └── apigen.py           # Automatic API generator
└── build/                      # Generated HTML (gitignored)
    └── html/
        └── index.html
```

## Build Commands

### Windows
```bash
# Clean previous build
cd docs
.\make.bat clean

# Build HTML
.\make.bat html

# View documentation
start build\html\index.html
```

### Unix/Linux/macOS
```bash
# Clean previous build
cd docs
make clean

# Build HTML
make html

# View documentation (Linux)
xdg-open build/html/index.html

# View documentation (macOS)
open build/html/index.html
```

### Using uv (recommended)
```bash
cd docs
uv run sphinx-build -M clean source build
uv run sphinx-build -M html source build
```

## Configuration

### conf.py Settings

**Package Name** (required if not "petromod"):
```python
api_package_name = 'your_package'
```

**Napoleon (NumPy docstrings)**:
```python
napoleon_google_docstring = False
napoleon_numpy_docstring = True
```

**Autodoc**:
```python
autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
    ...
}
```

## Public API Definition

The generator ONLY documents objects in `__all__`. Example:

**src/petromod/__init__.py**:
```python
from .grids.rectilinear import Rectilinear2DGrid

# Create alias
Grid2D = Rectilinear2DGrid

__all__ = [
    "Rectilinear2DGrid",  # Canonical name
    "Grid2D",             # Alias (will be detected)
]
```

**src/petromod/grids/__init__.py**:
```python
from .rectilinear import Rectilinear2DGrid

__all__ = ["Rectilinear2DGrid"]
```

## Generated Output

For the above example, you get:

```
API Reference
└── Grids (category)
    └── Rectilinear2DGrid (object page)
        - Aliases: petromod.Grid2D
        - Full class documentation
        - All methods and properties
```

## Customization

### Adding New Categories
Just create new subpackages with `__all__`:
```python
# src/petromod/wells/__init__.py
from .trajectory import WellTrajectory

__all__ = ["WellTrajectory"]
```
Rebuilding automatically creates a "Wells" category.

### Changing Category Names
Edit `_make_title()` in `apigen.py`:
```python
def _make_title(self, text: str) -> str:
    # Custom mappings
    if text == 'interpolators':
        return 'Interpolation'
    return text.replace('_', ' ').title()
```

### Excluding Private Members
Already configured in `conf.py`:
```python
autodoc_default_options = {
    'exclude-members': '__weakref__',
}
```

## Requirements

Installed via `pyproject.toml`:
```toml
[dependency-groups]
docs = [
    "sphinx>=9.1.0",
    "furo>=2025.12.19",
    "sphinx-design>=0.7.0",
]
```

Install with:
```bash
uv sync --group docs
```

## Workflow

1. **Write code** with NumPy-style docstrings
2. **Export via `__all__`** in `__init__.py` files
3. **Run build**: `uv run sphinx-build -M html source build`
4. **View docs**: Open `build/html/index.html`

That's it! No manual `.rst` editing required.

## Example Docstring (NumPy Style)

```python
class Rectilinear2DGrid:
    """2D structured rectilinear grid with lazy-evaluated cell centers.

    Attributes
    ----------
    x_vertex : np.ndarray
        1D array of grid line coordinates along x (size ni+1)
    y_vertex : np.ndarray
        1D array of grid line coordinates along y (size nj+1)
    active : np.ndarray
        Boolean mask of active cells (shape nj x ni)

    Examples
    --------
    >>> x = np.linspace(0, 100, 11)
    >>> y = np.linspace(0, 50, 6)
    >>> grid = Rectilinear2DGrid(x, y, active=np.ones((5, 10)))
    >>> print(grid.cell_shape)
    (5, 10)
    """
```

## Troubleshooting

**Q: "No public objects found"**  
A: Check that your package has `__all__` defined in `__init__.py`

**Q: "Could not import module"**  
A: Ensure your package is installed: `uv sync` or `pip install -e .`

**Q: Wrong category**  
A: Categories use the module where the object is **defined**, not where it's exported

**Q: Duplicate objects**  
A: This shouldn't happen - aliases are automatically detected. Check the logs.

**Q: Missing object**  
A: Ensure it's in `__all__` of an `__init__.py` that's reachable from the root package

## CI/CD Integration

### GitHub Actions
```yaml
- name: Build documentation
  run: |
    uv sync --group docs
    cd docs
    uv run sphinx-build -M html source build
    
- name: Deploy to GitHub Pages
  uses: peaceiris/actions-gh-pages@v3
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    publish_dir: ./docs/build/html
```

### Read the Docs
Create `.readthedocs.yaml`:
```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.13"

sphinx:
  configuration: docs/source/conf.py

python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs
```

## License

Same as your project.
