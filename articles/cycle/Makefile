PAPER = alps-cycle

$(PAPER).pdf: $(PAPER).tex
	latexmk -pdf -dvi- -ps- $<

.PHONY: clean
clean:
	latexmk -CA
