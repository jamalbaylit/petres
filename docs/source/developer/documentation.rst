Documentation
=============

Petres documentation is built using Sphinx with the Furo theme.

Build Documentation Locally
---------------------------

.. code-block:: bash

   uv run --group docs sphinx-build -b html docs/source docs/build/html

Open the generated HTML:

.. code-block:: bash

   docs/build/html/index.html

Live Reload (Optional)
----------------------

For development, you may use:

.. code-block:: bash

   uv run --group docs sphinx-autobuild docs/source docs/build/html

Project Structure
-----------------

.. code-block:: text

   docs/
     source/
       index.rst
       getting_started/
       fundamentals/
       developer/
       api/

Guidelines
----------

- Keep documentation **technical and concise**
- Prefer **clear definitions over long explanations**
- Use mathematical notation where appropriate:

  .. math::

     N_i, N_j, N_k

- Avoid redundancy between sections
- Use figures where they add real value (not decoration)

API Documentation
-----------------

API reference pages are auto-generated.

Ensure:

- Public API is exposed via ``__all__``
- Docstrings follow consistent style (NumPy or Google style)

Theme Customization
-------------------

Furo theme options are configured in ``conf.py``.

Custom templates can be placed under:

.. code-block:: text

   docs/source/_templates/