Installation
============

Petres requires **Python ≥ 3.10** and is tested on Linux, Windows, and macOS platforms.


Install from PyPI
-----------------

Petres is currently in a pre-release stage,
so installation requires enabling pre-releases:

.. code-block:: bash

   pip install petres


If you use ``uv``:

.. code-block:: bash

   uv pip install petres


Install from Source
-------------------

Alternatively, you can install the latest development version directly from the GitHub repository:

.. code-block:: bash

   git clone https://github.com/jamalbaylit/petres.git
   cd petres
   pip install .


Verify Installation
-------------------

Run the following command in your terminal to ensure Petres is correctly installed and accessible:

.. code-block:: bash

   python -c "import petres; print(f'Petres version: {petres.__version__}')"
   


Upgrade Petres
--------------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade petres

Or with ``uv``:

.. code-block:: bash

   uv pip install --upgrade petres