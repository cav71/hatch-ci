help:
	@echo "make install|build"

install:
	-pip uninstall hatch-ci
	pip install --edit .

build: install
	rm -rf dist
	GITHUB_DUMP='\
    {\
       "ref": "refs/heads/$(shell git branch --show-current)", \
       "sha": "$(shell git rev-parse HEAD)", \
       "run_number": 14, \
       "run_id": 5753082134 \
    }\
    ' python -m build -n

.PHONY: tests
tests:
	PYTHONPATH=src py.test -vvs tests
