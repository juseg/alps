# Data Makefile
# =============


# Rules
# -----

all: external

# retrieve exteral files
external: retrieve-external.sh
	bash $<

# clean external files
.PHONY: clean
clean:
	rm -rf external
