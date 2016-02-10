# Postprocessing Makefile

ETOPO1 = "http://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/\
grid_registered/georeferenced_tiff/ETOPO1_Bed_c_geotiff.zip"

all: etopo1.nc srtm.nc

etopo1.nc: get_etopo1.sh
	bash $<

srtm.nc: get_srtm.sh
	bash $<
