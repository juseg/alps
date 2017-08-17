# Figures Makefile
# ================


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = PYTHONPATH=iceplotlib python2

# all python figures
PY_FIGS = $(addprefix alpbou_, locmap) \
          $(addprefix alpcyc_, \
            $(addprefix hr_, aletschbed coldslip duration envelope \
                             erosion glaciations inputs lgmbig lgmthk lgmvel \
                             locmap profiles scalability timestamps \
                             timing totalsliding trimlines uplift \
                             ydthk ydvel) \
            $(addprefix lr_, footprints glacareas records rhineareas \
                             scaleinterval stackprints timeseries timing)) \
          $(addprefix alplgl_, extent)
PY_FIGS := $(addsuffix .$(EXT), $(PY_FIGS))

# all figures
ALL_FIGS = $(PY_FIGS)


# Rules
# -----

# default rule
all: $(ALL_FIGS)

# rules and dependencies for python figures
$(PY_FIGS): %.pdf : %.py matplotlibrc util
	$(PY) $<

# clean up
.PHONY: clean
clean:
	rm -f $(ALL_FIGS)
