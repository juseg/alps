# Figures Makefile


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = PYTHONPATH=iceplotlib python2

# all python figures
PY_FIGS = $(addprefix alpbou_, locmap) \
          $(addprefix alpcyc_, \
            $(addprefix hr_, aletschbed cpugrid duration envelope erosion \
                             glaciations inputs lgmbig lgmthk lgmvel \
                             locmap profile scalability timestamps \
                             timing totalsliding trimlines uplift \
                             warmdepth warmtime ydthk ydvel) \
            $(addprefix lr_, footprints glacareas records timeseries))
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
