# Figures Makefile
# ================


# Variables
# ---------

# default figure extension
EXT = pdf

# python executable
PY = PYTHONPATH=iceplotlib python2

# all python figures (broken alpflo_egumap alpflo_profiles)
PY_FIGS = $(addprefix alpbou_, locmap) \
          $(addprefix alpcyc_, \
            $(addprefix hr_, aletschbed coldslip duration deformation \
                             deglacage dynamics \
                             envelope erosion glaciations inputs lastflow \
                             lgmthk lgmvel locmap overshoot profiles \
                             timestamps timing totalsliding trimlines uplift \
                             ydthk ydvel) \
            $(addprefix lr_, footprints glacareas records rhineareas \
                             scaleinterval stackprints timeseries timestamps \
                             timing)) \
          $(addprefix alpflo_, scalability timeseries timestamps) \
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
