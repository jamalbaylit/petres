# Configuration file for the Sphinx documentation builder.

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


# -- Path setup --------------------------------------------------------------

DOCS_SOURCE_DIR = Path(__file__).resolve().parent
DOCS_DIR = DOCS_SOURCE_DIR.parent
PROJECT_ROOT = DOCS_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
EXT_DIR = DOCS_SOURCE_DIR / "_ext"
TEMPLATES_DIR = DOCS_SOURCE_DIR / "_templates"

sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(EXT_DIR))
# sys.path.insert(0, str(TEMPLATES_DIR))


# -- Project information -----------------------------------------------------

project = "petres"
author = "Tayfun Jamalbayli"
START_YEAR = 2026
YEAR = date.today().year

copyright = (
    f"{START_YEAR}, {author}"
    if START_YEAR == YEAR
    else f"{START_YEAR}–{YEAR}, {author}"
)
release = "0.1.0"


# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinx_copybutton",
    "apigen",
    "exampledocs",
]

templates_path = ["_templates"]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

root_doc = "index"

# Configure package name for API generator
api_package_name = "petres"


# -- Napoleon settings -------------------------------------------------------

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True


# -- Autodoc settings --------------------------------------------------------

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}

autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_class_signature = "separated"
autodoc_member_order = "bysource"
autoclass_content = "both"


# -- Autosummary settings ----------------------------------------------------

autosummary_generate = False


# -- Intersphinx settings ----------------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = "furo"
# html_theme = "shibuya"
html_title = "Documentation"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_show_sphinx = False

html_theme_options = {
    "light_logo": "logo-lockup-light.svg",
    "dark_logo": "logo-lockup-dark.svg",
    "footer_icons": [],
    "light_css_variables": {
        "color-brand-primary": "#622b84",
        "color-brand-content": "#7d2b84",
    },
    "dark_css_variables": {
        "color-brand-primary": "#5b9bd5",
        "color-brand-content": "#5b9bd5",
    },
}


# -- Options for other builders ---------------------------------------------

latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
}

latex_documents = [
    ("index", "petres.tex", "Documentation", f"{author}", "manual"),
]


# pygments_style = "one-dark"
# pygments_dark_style = "one-dark"
