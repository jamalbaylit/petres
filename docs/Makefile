# Minimal makefile for Sphinx documentation

SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run --group docs sphinx-build
PYTHON        ?= uv run --group docs python
SOURCEDIR     = source
BUILDDIR      ?= build
APIDIR        = source/api
GENERATEDDIR  = source/_generated

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile html clean

clean:
	@echo "Removing build directory..."
	@$(PYTHON) -c "import shutil; shutil.rmtree('$(BUILDDIR)', ignore_errors=True)"
	@echo "Removing generated API documentation..."
	@$(PYTHON) -c "import shutil; shutil.rmtree('$(APIDIR)', ignore_errors=True)"
	@echo "Removing generated example documentation..."
	@$(PYTHON) -c "import shutil; shutil.rmtree('$(GENERATEDDIR)', ignore_errors=True)"
	@echo "Removing generated landing pages..."
	@$(PYTHON) -c "from pathlib import Path; [Path(p).unlink(missing_ok=True) for p in ['$(SOURCEDIR)/getting_started.rst', '$(SOURCEDIR)/tutorials.rst', '$(SOURCEDIR)/examples.rst']]"
	@echo "Clean complete."

html: clean
	@echo "Building HTML documentation..."
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)