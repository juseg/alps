# Figures Makefile
# ================


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = PYTHONPATH=iceplotlib python2

# all python figures
# (tmp broken:	     alpflo_, egumap profiles )
PY_FIGS = $(addprefix alpbou_, locmap) \
          $(addprefix alpcyc_, \
            $(addprefix hr_, coldslip covertime deformation deglacage inputs \
                             locmap maxextthk maxextvel maxextsrf maxthkage \
			     profiles timestamps trimlines uplift) \
            $(addprefix lr_, footprints glacareas records rhineareas \
                             timeseries timestamps)) \
          $(addprefix alpflo_, scalability timeseries timestamps) \
          $(addprefix alpero_, glerosion lastbvdir totalslip ) \
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
	rm -f $(ALL_FIGS) alpflo_egumap.jpg
