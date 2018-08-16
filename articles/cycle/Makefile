# Article Makefile
# ================


# Variables
# ---------

PAPER = alps-cycle
REV = $(shell git describe --abbrev=0 --match=alpcyc*)
REV = alpcyc-2.1


# Named rules
# -----------

# default rule
pdf: $(PAPER).pdf

# word count
sum: $(PAPER).sum

# latex diff
diff: $(PAPER)-diff.pdf

# responses
resp: $(addprefix response-, editor1.pdf editor2.pdf editor3.pdf monegato.pdf \
			     referee1.pdf referee2.pdf referee3.pdf )


# Patterned rules
# ---------------

# latex to pdf
%.pdf: %.tex
	latexmk -pdf -dvi- -ps- $<

# latex word count
%.sum: %.tex
	texcount -sub=section $< -out=$@

# latex diff
%-diff.tex: %.tex
	latexdiff-vc --force --git -r $(REV) $<
	mv $(basename $@)$(REV).tex $@

# Clean up
# --------

.PHONY: clean
clean:
	latexmk -CA
