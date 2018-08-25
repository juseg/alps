# Data Makefile
# =============


# Rules
# -----

# default rule
all: external processed

# retrieve external files
external: retrieve-external.sh
	bash $<

# postprocess output files
processed: postprocess-alpcyc-agg.py postprocess-alpcyc-cts.sh \
	   postprocess-alpero-agg.py
	bash $<

# clean up
.PHONY: clean
clean:
	rm -rf external processed
