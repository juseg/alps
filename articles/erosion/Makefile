# Article Makefile
# ================


# Variables
# ---------

PAPER = alps-erosion
REV = $(shell git describe --abbrev=0 --match=alpero*)


# Rules
# -----

# default rule
pdf: $(PAPER).pdf

# default diff
diff: $(PAPER)-diff.pdf

# latex to pdf patterned rule
%.pdf: %.tex
	latexmk -pdf -dvi- -ps- $<

# latex diff patterned rule
%-diff.tex: %.tex
	latexdiff-vc --force --git -r $(REV) $<
	mv $(basename $@)$(REV).tex $@

# Clean up
# --------

.PHONY: clean
clean:
	latexmk -pdf -CA
