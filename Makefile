# Makefile für lokale Dokumentations-Vorschau (Stand-alone)
# --------------------------------------------------------

SPHINXBUILD = sphinx-build
SOURCEDIR   = .
BUILDDIR    = _build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)"

.PHONY: help html clean

# Der einfachste Befehl für Redakteure
html:
	@echo "Generiere lokale HTML-Vorschau..."
	$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html"
	@echo "Fertig! Öffne $(BUILDDIR)/html/index.html in deinem Browser."

clean:
	rm -rf $(BUILDDIR)
