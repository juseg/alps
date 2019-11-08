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
processed: postprocess_alpcyc_agg.py postprocess_alpcyc_cts.sh \
	   postprocess_alpero_agg.py
	bash $<

# clean up
.PHONY: clean
clean:
	rm -rf external processed
