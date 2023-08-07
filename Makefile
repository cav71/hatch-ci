help:
	@echo "make install|build"

install:
	-pip uninstall hatch-ci
	pip install --edit .

build: 
	rm -rf dist
	GITHUB_DUMP='\
    {\
       "ref": "refs/heads/$(shell git branch --show-current)", \
       "sha": "$(shell git rev-parse HEAD)", \
       "run_number": 14, \
       "run_id": 5753082134 \
    }\
    ' python -m build -n

debug:
	rm -rf dist
	git checkout README.md src/hatch_ci/__init__.py
	GITHUB_DUMP='\
    {\
       "ref": "refs/heads/$(shell git branch --show-current)", \
       "sha": "$(shell git rev-parse HEAD)", \
       "run_number": 14, \
       "run_id": 5753082134 \
    }\
    ' python -m build -n
	mv dist/hatch_ci-0.0.7b14-py3-none-any.whl dist/hatch_ci-0.0.7b14-py3-none-any.zip
	mkdir -p build
	cd build && unzip ../dist/hatch_ci-0.0.7b14-py3-none-any.zip
	git checkout README.md src/hatch_ci/__init__.py

.PHONY: test
test:
	PYTHONPATH=src py.test -vvs tests
