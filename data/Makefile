# Data Makefile
# =============


# Rules
# -----

all: external processed

# retrieve external files
external: retrieve-external.sh
	bash $<

# postprocess output files
processed: postprocess-output.sh
	bash $<

# clean external files
.PHONY: clean
clean:
	rm -rf external processed
