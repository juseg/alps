# Figures Makefile

# default figure extension
EXT = pdf

# all python figures
PY_FIGS = duration envelope footprints glaciations inputs lgm \
          locmap_alps locmap_rhone \
          scalability sensrheo timeseries timing totalsliding zoom
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

# all figures
ALL_FIGS = $(PY_FIGS)

# to make all figures
all: data $(ALL_FIGS)

# rules and dependencies for python figures
$(PY_FIGS): %.pdf : %.py matplotlibrc
	python2 $<

# phony targets
.PHONY : data clean

data:
	cd data && $(MAKE)

clean:
	rm $(ALL_FIGS)
