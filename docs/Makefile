# Minimal makefile for Sphinx documentation

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run --group docs sphinx-build
SOURCEDIR     = source
BUILDDIR      = build
APIDIR        = source/api

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile html clean

# Custom clean target that removes build and generated API files
clean:
	@echo "Removing build directory..."
	@rm -rf $(BUILDDIR)
	@echo "Removing generated API documentation..."
	@rm -rf $(APIDIR)
	@echo "Clean complete."

# Custom html target that cleans before building
html:
	@echo "Cleaning previous build and generated files..."
	@rm -rf $(BUILDDIR) $(APIDIR)
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

uv:
	@uv run --group docs examples/generate_api_docs.py
# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
