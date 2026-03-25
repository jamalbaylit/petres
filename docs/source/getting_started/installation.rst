Installation
============

This page describes how to install Petres for regular use and for development.

Requirements
------------

Petres requires:

- Python 3.10 or newer
- NumPy
- SciPy
- A supported visualization backend for 3D plotting, if visualization features are used

Install from PyPI
-----------------

Install the latest released version from PyPI:

.. code-block:: bash

   pip install petres

If you use ``uv``:

.. code-block:: bash

   uv pip install petres

Verify the installation by importing Petres in Python:

.. code-block:: python

   import petres
   print("Petres installed successfully")

Install optional visualization dependencies
-------------------------------------------

Some features, such as 3D visualization, may depend on optional packages.

For example, if your workflow uses PyVista-based visualization, install the visualization extras if your package configuration exposes them:

.. code-block:: bash

   pip install "petres[viz]"

or with ``uv``:

.. code-block:: bash

   uv pip install "petres[viz]"

If extras are not yet exposed in your packaging configuration, install the required visualization libraries directly according to your project setup.

Development installation
------------------------

To install Petres in editable mode for development:

.. code-block:: bash

   git clone https://github.com/<your-username>/petres.git
   cd petres
   pip install -e .

With ``uv``:

.. code-block:: bash

   git clone https://github.com/<your-username>/petres.git
   cd petres
   uv sync

If your project defines optional dependency groups for development tools, documentation, or testing, install them as needed.

For example:

.. code-block:: bash

   pip install -e ".[dev,docs,test]"

or with ``uv``:

.. code-block:: bash

   uv sync --group dev --group docs --group test

Recommended virtual environment setup
-------------------------------------

Using a virtual environment is strongly recommended.

With ``venv``:

.. code-block:: bash

   python -m venv .venv

Activate it on Windows:

.. code-block:: bash

   .venv\Scripts\activate

Activate it on macOS or Linux:

.. code-block:: bash

   source .venv/bin/activate

Then install Petres:

.. code-block:: bash

   pip install petres

With ``uv``:

.. code-block:: bash

   uv venv
   uv sync

Install from source
-------------------

If you want to work directly from the source tree without an editable install:

.. code-block:: bash

   git clone https://github.com/<your-username>/petres.git
   cd petres
   pip install .

Troubleshooting
---------------

Import errors
^^^^^^^^^^^^^

If ``import petres`` fails:

- confirm that the correct virtual environment is activated
- confirm that the installation completed successfully
- confirm that the Python interpreter in your editor matches the environment where Petres was installed

Visualization issues
^^^^^^^^^^^^^^^^^^^^

If plotting or 3D rendering does not work:

- verify that optional visualization dependencies are installed
- verify that your environment supports OpenGL rendering if required by the selected backend
- try a minimal non-visual workflow first to confirm the core installation is correct

Upgrade Petres
--------------

To upgrade to the latest available release:

.. code-block:: bash

   pip install --upgrade petres

or with ``uv``:

.. code-block:: bash

   uv pip install --upgrade petres

Next step
---------

Once installation is complete, continue to :doc:`quickstart` to create your first Petres model.