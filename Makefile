help:
	@echo "make install|wheel"


install:
	-pip uninstall hatch-github
	pip install --edit .

wheel:
	rm -rf dist && python -m build .
