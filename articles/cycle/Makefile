# Article Makefile
# ================


# Variables
# ---------

PAPER = alps-cycle


# Rules
# -----

# default rule
$(PAPER).pdf: $(PAPER).tex
	latexmk -pdf -dvi- -ps- $<

# clean up
.PHONY: clean
clean:
	latexmk -CA
