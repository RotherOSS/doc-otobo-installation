VENV        = .venv
PYTHON      = python3
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP    = $(VENV)/bin/pip
SPHINXBUILD = $(VENV)/bin/sphinx-build
VENV_STAMP  = $(VENV)/.installed
SOURCEDIR   = .
BUILDDIR    = _build
MAKEFILE    = $(lastword $(MAKEFILE_LIST))

UNAME_S := $(shell uname -s)

ifeq ($(UNAME_S),Darwin)
	OPEN_CMD := open
else ifeq ($(UNAME_S),Linux)
	OPEN_CMD := xdg-open
else
	$(error Unsupported OS: $(UNAME_S))
endif

.PHONY: help open clean venv build auto clean-venv check linkcheck trailing-whitespace sembr buildable

help: ## List every available make target and what it does.
	@echo
	@echo "make targets:"
	@echo
	@awk 'BEGIN { FS = ":.*## " } /^[^#[:space:].][^:]*:.*## / { printf "  make %-22s %s\n", $$1, $$2 }' $(MAKEFILE)


$(VENV_PYTHON): ## (internal) Create the virtual environment if it does not exist.
	@test -x $@ || $(PYTHON) -m venv $(VENV)

$(VENV_STAMP): $(VENV_PYTHON) requirements.txt ## (internal) Install or refresh the documentation dependencies.
	$(VENV_PIP) install --quiet --no-cache-dir --upgrade pip
	$(VENV_PIP) install --quiet --no-cache-dir -r requirements.txt
	@touch $@

venv: $(VENV_STAMP) ## Validate the virtual environment and install dependencies if needed.
	@echo "Virtual environment ready at $(VENV)/"

build: $(VENV_STAMP) ## Build the local HTML preview.
	@echo "Generating local HTML preview ..."
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html"
	@echo "Done! Run \"make open\" to show the preview in your browser."

check: $(VENV_STAMP) clean ## Check validity
	@status=0;\
	$(MAKE) buildable || status=1; \
	$(MAKE) linkcheck || status=1; \
	$(MAKE) trailing-whitespace || status=1; \
	$(MAKE) sembr || status=1; \
	if [ $$status -eq 0 ]; then printf "\n`tput bold`=== All checks passed 🎉`tput sgr0`\n"; fi; \
	exit $$status

buildable: $(VENV_STAMP) ## Check if the documentation is buildable.
	@printf "\n`tput bold`=== [check] buildability ...`tput sgr0`\n"; \
	$(SPHINXBUILD) --color -q -W --keep-going -n -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" && printf "`tput setaf 2`ok.`tput sgr0`\n"

linkcheck: $(VENV_STAMP) ## Check for broken links in the documentation.
	@printf "\n`tput bold`=== [check] external links ...`tput sgr0`\n"; \
	$(SPHINXBUILD) -Q -b linkcheck "$(SOURCEDIR)" "$(BUILDDIR)/linkcheck"; \
  STATUS=$$?; \
	OUTPUT=$$(jq -r '\
      select(.status | IN("working", "unchecked") | not) |\
      "\u001b[35m\(.filename)\u001b[0m:\u001b[32m\(.lineno)\u001b[0m \(.uri) - \u001b[1m\(.status)\u001b[0m - \(.info)"\
      ' $(BUILDDIR)/linkcheck/output.json); \
  if [ -z "$$OUTPUT" ]; then echo "`tput setaf 2`ok.`tput sgr0`"; else echo "$$OUTPUT"; exit 1; fi; \
  exit $$STATUS

trailing-whitespace: $(VENV_STAMP) ## Check for trailing whitespace in the documentation.
	@printf "\n`tput bold`=== [check] trailing whitespace ...`tput sgr0`\n"; \
	! git --no-pager grep --ignore-case --line-number --color=always --recursive ' $$' -- '*.rst' '*.md' && printf "`tput setaf 2`ok.`tput sgr0`\n"

sembr: $(VENV_STAMP) ## Check for semantic linebreaks (best effort).
	@printf "\n`tput bold`=== [check] https://sembr.org ...`tput sgr0`\n"; \
	! git --no-pager grep --ignore-case --line-number --color=always --recursive '[a-z]\{2,\}[\.\?\!] .*$$' -- '*.rst' '*.md' && printf "`tput setaf 2`ok.`tput sgr0`\n"


open: ## Open the generated HTML preview in the default browser.
	$(OPEN_CMD) $(BUILDDIR)/html/content/index.html

auto: build ## Automatically rebuild the documentation on changes.
	@sleep 2 && $(OPEN_CMD) "http://localhost:9426/content/" &
	@$(VENV)/bin/sphinx-autobuild -a --port 9426 -b html --no-initial "$(SOURCEDIR)" "$(BUILDDIR)/html"

clean: ## Remove the generated documentation build output.
	rm -rf $(BUILDDIR)

clean-venv: clean ## Remove the build output and the virtual environment.
	rm -rf $(VENV)
