# Figures Makefile

# default figure extension
EXT = pdf

# all python figures
PY_FIGS = duration envelope footprints glaciations inputs \
          lgmbig lgmthk lgmvel \
          locmap_alps locmap_rhone scalability sensrheo \
          timeseries timestamps timing totalsliding trimlines tsbig \
          uplift zoom ydthk ydvel
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

# all figures
ALL_FIGS = $(PY_FIGS)

# to make all figures
all: $(ALL_FIGS)

# rules and dependencies for python figures
$(PY_FIGS): %.pdf : %.py matplotlibrc
	python2 $<

# clean figures
.PHONY: clean
clean:
	rm $(ALL_FIGS)
