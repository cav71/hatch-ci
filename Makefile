# REF:
#   master  : refs/heads/master"
#   beta    : refs/heads/beta/0.3.7
#   release : refs/tags/release/0.3.7

REF=$(shell git rev-parse --symbolic-full-name HEAD)
SHA=$(shell git rev-parse HEAD)
RUNNO=123
RUNID=5753082134

GITHUB_DUMP="{\"ref\": $(REF), \"sha\": $(SHA), \"run_id\": $(RUNID), \"run_number\": $(RUNNO)}"
export GITHUB_DUMP


help:
	@echo "make help|build|tests"
	@echo ""
	@echo "Vars"
	@echo "  REF:          $(REF)"
	@echo "  SHA:          $(SHA)"
	@echo "  RUNID:        $(RUNID)"
	@echo "  RUNNO:        $(RUNNO)"
	@echo "  GITHUB_DUMP:  $(GITHUB_DUMP)"

install:
	-pip uninstall hatch-ci
	pip install --edit .


.PHONY: build
build: 
	rm -rf dist
	git checkout src/hatch_ci/__init__.py
	GITHUB_DUMP='\
    {\
       "ref": "refs/heads/$(shell git branch --show-current)", \
       "sha": "$(shell git rev-parse HEAD)", \
       "run_number": 14, \
       "run_id": 5753082134 \
    }\
    ' python -m build $(NFLAG)

.PHONY: debug
debug: NFLAG=-n
debug: build
	mv dist/hatch_ci-*.whl dist/out.zip
	mkdir -p build
	cd build && unzip ../dist/out.zip
	git checkout README.md src/hatch_ci/__init__.py

.PHONY: tests
tests:
	PYTHONPATH=src py.test -vvs tests
