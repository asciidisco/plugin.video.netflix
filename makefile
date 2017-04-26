# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
SPHINXPROJ    = pluginvideonetflix
SOURCEDIR     = ./resources/lib
BUILDDIR      = _build
DOCS_DIR=./docs
REPORT_DIR=./report
TEST_DIR=./resources/test
MODULES=addon service NetflixSession KodiHelper MSL Library NetflixSessionUtils Navigation NetflixHttpRequestHandler NetflixHttpSubRessourceHandler MSLHttpRequestHandler utils

clean-pyc:
	find . -name '*.pyc' -exec rm {} +
	find . -name '*.pyo' -exec rm {} +

clean-report:
	rm -rf $(REPORT_DIR)
	mkdir $(REPORT_DIR)

clean-docs:
	rm -rf $(DOCS_DIR)
	mkdir $(DOCS_DIR)	

lint:
	flake8	
	pylint $(MODULES) --output-format=html > ./report/lint.html || exit 0
	pylint $(MODULES) --output-format=colorized

test:
	nosetests $(TEST_DIR) -s --cover-package=resources.lib.MSL --cover-package=resources.lib.NetflixSession --cover-package=resources.lib.Navigation --cover-package=resources.lib.utils --cover-package=resources.lib.Library --cover-package=resources.lib.KodiHelper --cover-package=resources.lib.KodiHelperUtils --cover-package=resources.lib.NetflixSessionUtils --cover-erase --with-coverage --cover-html --cover-branches --cover-html-dir=$(REPORT_DIR)/coverage
	rm -rf ./_tmp

html:
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

help:
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    clean-report"
	@echo "        Remove coverage/lint report artifacts."
	@echo "    clean-docs"
	@echo "        Remove pydoc artifacts."	
	@echo "    lint"
	@echo "        Check style with flake8 & pylint"
	@echo "    test"
	@echo "        Run unit tests"
	@echo "    html"
	@echo "        Generates sphinx docs"	