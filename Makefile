.DEFAULT_GOAL := help

CURRENT_PYTHON_VERSION := 313
OLDEST_PYTHON_VERSION  := 312

ifeq ($(OS),Windows_NT)
	DETECTED_OS := Windows
else
	DETECTED_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
endif
IS_WSL := false
ifneq ($(WSL_DISTRO_NAME),)
	IS_WSL := true
endif

all: build

.PHONY:
test-makefile:
	$(info    DETECTED_OS is "$(DETECTED_OS)")
	$(info    IS_WSL is "$(IS_WSL)")

.PHONY:
install:  ## setup user environment
	./bootstrap.sh

.PHONY:
setup: install

.PHONY:
install-dev:  ## setup development environment
	./bootstrap.sh --dev

.PHONY:
setup-dev: install-dev

.PHONY:
build: ## build wheels and sdists
	echo Detected OS: $(DETECTED_OS)
	./run.sh poetry build

# .PHONY:
# build-debug: build ### build for debug

# .PHONY:
# build-release: build ### build for release

.PHONY:
extract-build: build ## extract built archives into folders
	cd dist; for x in *; do mkdir "$$x-extracted"; tar -xzf "$$x" -C "$$x-extracted"; done

.PHONY:
clean-build:  ### clean build results
	rm -rf ./output
	rm -rf ./dist
	rm -rf static_src
	# cspell: disable-next-line
	rm -f .sconsign-*.dblite
	rm -f @link_input.txt
	rm -f build_definitions.h
	# cspell: disable-next-line
	rm -f ccache-*.txt
	rm -f scons-error-report.txt
	rm -f scons-report.txt

.PHONY:
clean-cache:  ### clean caches
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	find . \( -name '__pycache__' -or -name '*.pyc' -or -name '*.pyo' -or -name '*.pyd' \) -print0 | xargs -r0 rm -rf

.PHONY:
clean-test:  ### clean test results
	rm -rf .reports
	rm -rf htmlcov
	rm -f .coverage
	rm -f .coverage.*
	rm -f cov.xml
	rm -f coverage.cobertura.xml
	rm -f coverage.json
	rm -f coverage.html
	rm -f coverage.xml
	rm -f jacoco.xml
	rm -f junit.xml
	rm -f lcov.info
	rm -f lcov.xml

.PHONY:
clean: clean-build clean-cache clean-test  ### clean build results, caches, and test results

.PHONY:
clean-old: ## remove all *.old files
	find . -name '*.old' -print0 | xargs -r0 rm -f

.PHONY:
clean-tox: ## remove tox environments
	rm -rf .tox

.PHONY:
sterilize: clean clean-old clean-tox ## clean EVERYTHING

.PHONY:
superclean: sterilize

.PHONY:
run: ## run software
	./run.sh

.PHONY:
update-bfi: ## update batteries-forking-included files
	./bfi-update.sh

.PHONY:
quicktest: ### run tests for latest python version
	./run.sh tox -e py$(CURRENT_PYTHON_VERSION) -- --verbose

.PHONY:
legacytest: ### run tests for oldest supported python version
	./run.sh tox -e py$(OLDEST_PYTHON_VERSION) -- --verbose

.PHONY:
coverage: ## gather coverage data
	./run.sh tox -e coverage -- --verbose

.PHONY:
lint: ## run all linters
	./run.sh tox -e lint -- --verbose

.PHONY:
test-all: ### run all tests for all python versions, linters, and gather coverage
	./run.sh tox

.PHONY:
test: quicktest

.PHONY:
check: test

# cspell: disable
.PHONY:
help: ## show this help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
# cspell: enable
