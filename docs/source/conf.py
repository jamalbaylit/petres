# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import sys
from pathlib import Path

# -- Path setup --------------------------------------------------------------

# Add src directory to Python path for autodoc
root_dir = Path(__file__).parent.parent.parent
src_dir = root_dir / 'src'
sys.path.insert(0, str(src_dir))

# -- Project information -----------------------------------------------------

project = 'petres'
copyright = '2026, Petres Team'
author = 'Petres Team'
release = '0.1.0'

# -- General configuration ---------------------------------------------------

extensions = [
    # Core Sphinx extensions
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    
    # Third-party extensions
    'sphinx_design',
    
    # Custom extension for automatic API generation
    'apigen',
]

# Add custom extension directory
sys.path.insert(0, str(Path(__file__).parent / '_ext'))

# Configure package name for API generator
api_package_name = 'petres'

# -- Napoleon settings (NumPy style docstrings) ------------------------------

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
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'
autodoc_class_signature = 'separated'
autodoc_member_order = 'bysource'

# Don't skip __init__ docstrings
autoclass_content = 'both'

# -- Autosummary settings ----------------------------------------------------

autosummary_generate = False  # We generate manually via apigen

# -- Intersphinx settings ----------------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'scipy': ('https://docs.scipy.org/doc/scipy/', None),
}

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo'

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2b5b84",
        "color-brand-content": "#2b5b84",
    },
    "dark_css_variables": {
        "color-brand-primary": "#5b9bd5",
        "color-brand-content": "#5b9bd5",
    },
}

html_title = f"{project} Documentation"
html_static_path = ['_static']

# -- Options for other builders ---------------------------------------------

# LaTeX settings
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    ('index', 'petres.tex', 'petres Documentation',
     'Petres Team', 'manual'),
]
