# Article Makefile
# ================


# Variables
# ---------

PAPER = alps-cycle

# Rules
# -----

# default rule
$(PAPER).pdf: $(PAPER).tex $(PAPER).sum
	latexmk -pdf -dvi- -ps- $<

# word count
$(PAPER).sum: $(PAPER).tex
	texcount -sub=section $< -out=$@

# clean up
.PHONY: clean
clean:
	latexmk -CA
