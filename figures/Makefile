# Figures Makefile
# ================


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = python

# all python figures
# (tmp off: alpero_, finalslip
# 	    alpflo_, egumap profiles scalability timeseries timestamp
#           alplgl_, extent)
# (require coldroom: alpero_, temperature)
PY_FIGS = $(addprefix alpbou_, locmap) \
          $(addprefix alpcyc_, \
            $(addprefix hr_, coldslip covertime deformation deglacage inputs \
                             locmap maxextthk maxextvel maxextsrf maxthkage \
			     profiles timestamp trimlines) \
            $(addprefix lr_, footprints records glacareas \
                             timeseries timestamp)) \
          $(addprefix alpero_, basaldrag cumulative evolution hypsogram \
                               landscape powerlaws sensitivity transects)
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
