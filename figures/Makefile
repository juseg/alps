# Figures Makefile


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = PYTHONPATH=iceplotlib python2

# all python figures
PY_FIGS = aletschbed cpugrid duration envelope erosion footprints glacareas \
          glaciations inputs lgmbig lgmthk lgmvel map_records \
          locmap locmap_alps locmap_rhone profile scalability \
          timeseries timestamps timing totalsliding trimlines tsbig \
          uplift warmdepth warmtime ydthk ydvel
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

# all figures
ALL_FIGS = $(PY_FIGS)


# Rules
# -----

# to make all figures
all: $(ALL_FIGS)

# rules and dependencies for python figures
$(PY_FIGS): %.pdf : %.py matplotlibrc util
	$(PY) $<

# clean figures
.PHONY: clean
clean:
	rm $(ALL_FIGS)
