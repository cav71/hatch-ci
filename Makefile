help:
	@echo "make install|build"

install:
	-pip uninstall hatch-github
	pip install --edit .

build:
	rm -rf dist && python -m build -n .

.PHONY: tests
tests:
	PYTHONPATH=src py.test -vvs tests
