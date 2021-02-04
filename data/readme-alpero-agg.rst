Alpine ice sheet erosion potential aggregated variables
-------------------------------------------------------

Files [required]::

   alpero.1km.epic.pp.agg.nc
   alpero.2km.epic.cp.agg.nc
   alpero.2km.epic.pp.agg.nc
   alpero.2km.grip.cp.agg.nc
   alpero.2km.grip.pp.agg.nc
   alpero.2km.md01.cp.agg.nc
   alpero.2km.md01.pp.agg.nc

Communities [recommended]
   --

Upload type [required]
   Dataset

Basic information [required]
   Digital Object Identifier
      10.5281/zenodo.4495419

   Publication date
      2021-02-02

   Title
      Alpine ice sheet erosion potential aggregated variables

   Authors
      Seguinot, Julien

   Description
      These data contain domain-integrated and time-integrated model output
      variables presented in the reference below or otherwise relevant to last
      glacial cycle glacier erosion in the Alps.

      **Reference**:

      * J. Seguinot and I. Delanay.
        Last glacial cycle glacier erosion potential in the Alps,
        Submitted to Earth Surface Dynamics Discussions,
        2021.

      **File names**:

         alpero.{1km|2km}.{epic|grip|md01}.{cp|pp}.agg.nc

      * Horizontal resolution:

        - *1km*: 1 km horizontal resolution
        - *2km*: 2 km horizontal resolution

      * Temperature forcing:

        - *epic*: EPICA ice core temperature forcing
        - *grip*: GRIP ice core temperature forcing
        - *md01*: MD01-2444 core temperature forcing

      * Precipitation forcing:

        - *cp*: constant precipitation
        - *pp*: palaeo-precipitation reduction

      **Variables**:

      * Coordinate variables:

        - *x*:    X-coordinate in Cartesian system
        - *y*:    Y-coordinate in Cartesian system
        - *lon*:  longitude
        - *lat*:  latitude
        - *time*: time
        - *age*:  model age
        - *z*:    elevation band midpoints
        - *d*:    distance along transect

      * Glacier erosion variables:

        - *coo2020_cumu*: Cook et al. (2020) cumulative glacial erosion potential
        - *coo2020_rate*: Cook et al. (2020) domain total volumic erosion rate
        - *coo2020_hyps*: Cook et al. (2020) erosion rate geometric mean
        - *coo2020_rhin*: Cook et al. (2020) rhine transect erosion rate
        - *her2015_cumu*: Herman et al. (2015) cumulative glacial erosion potential
        - *her2015_rate*: Herman et al. (2015) domain total volumic erosion rate
        - *her2015_hyps*: Herman et al. (2015) erosion rate geometric mean
        - *her2015_rhin*: Herman et al. (2015) rhine transect erosion rate
        - *hum1994_cumu*: Humphrey and Raymond (1994) cumulative glacial erosion potential
        - *hum1994_rate*: Humphrey and Raymond (1994) domain total volumic erosion rate
        - *hum1994_hyps*: Humphrey and Raymond (1994) erosion rate geometric mean
        - *hum1994_rhin*: Humphrey and Raymond (1994) rhine transect erosion rate
        - *kop2015_cumu*: Koppes et al. (2015) cumulative glacial erosion potential
        - *kop2015_rate*: Koppes et al. (2015) domain total volumic erosion rate
        - *kop2015_hyps*: Koppes et al. (2015) erosion rate geometric mean
        - *kop2015_rhin*: Koppes et al. (2015) rhine transect erosion rate

      * Other variables:

        - *cumu_sliding*: cumulative basal motion
        - *glacier_time*: total ice cover duration
        - *warmbed_time*: temperate-based ice cover duration
        - *glacier_area*: glacierized area
        - *volumic_lift*: volumic bedrock uplift
        - *warmbed_area*: temperate-based ice cover area

      **Data format**:

      The data use compressed netCDF format. For quick inspection I recommend
      ncview. Conversion to GeoTIFF (and other GIS formats) can be achieved
      with e.g. GDAL::

         gdal_translate NETCDF:filename.nc:variable filename.variable.tif

      The list of variables (subdatasets) can be obtained from ncdump or
      gdalinfo. To convert all variables to separate files use::

         gdalinfo $filename | grep NETCDF | cut -d '=' -f 2 |
            egrep -v '(lat|lon|time_bounds)' | while read sub
         do
            gdal_translate $sub ${filename%.nc}.${sub##*:}.tif
         done

      Variable long names, units, PISM configuration parametres and additional
      information are contained within the netCDF metadata. Also see glacial
      cycle `aggregated <https://doi.org/10.5281/zenodo.1423160>`_ and
      `continuous <https://doi.org/10.5281/zenodo.1423176>`_ variables.

      **Changelog:**

      * Version 1:

         - Initial version.

   Version
      --

   Language
      en

   Keywords
      alps, glacier, ice sheet, modelling

   Additional notes
      This work was supported by the Swiss National Science Foundation (SNSF)
      grants 200020-169558 and 200021-153179/1, and the Swiss National
      Supercomputing Centre (CSCS) grants s573 and sm13.

License [required]
   Open Access / Creative Commons Attribution 4.0

Funding [recommended]
   -- (not working)

Related/alternate identifiers [recommended]
   https://doi.org/10.5281/zenodo.1423160 is referenced by this upload
   https://doi.org/10.5281/zenodo.1423176 is referenced by this upload
   https://doi.org/10.5194/tc-12-3265-2018 is referenced by this upload

Contributors [optional]
   Delanay, Ian

References [optional]

   * Cook, S. J., Swift, D. A., Kirkbride, M. P., Knight, P. G., and Waller, R.
     I.: The empirical basis for modelling glacial erosion rates, Nature
     Communications, 11, https://doi.org/10.1038/s41467-020-14583-8, 2020.

   * Herman, F., Beyssac, O., Brughelli, M., Lane, S. N., Leprince, S., Adatte,
     T., Lin, J. Y. Y., Avouac, J.-P., and Cox, S. C.: Erosion by an Alpine
     glacier, Science, 350, 193–195, https://doi.org/10.1126/science.aab2386,
     2015.

   * Humphrey, N. F. and Raymond, C. F.: Hydrology, erosion and sediment
     production in a surging glacier: Variegated Glacier, Alaska, 1982–83, J.
     Glaciol., 40, 539–552, https://doi.org/10.3189/s0022143000012429, 1994.

   * Koppes, M., Hallet, B., Rignot, E., Mouginot, J., Wellner, J. S., and
     Boldt, K.: Observed latitudinal variations in erosion as a function of
     glacier dynamics, Nature, 526, 100–103,
     https://doi.org/10.1038/nature15385, 2015.

   * Seguinot, J., Ivy-Ochs, S., Jouvet, G., Huss, M., Funk, M., and Preusser,
     F.: Modelling last glacial cycle ice dynamics in the Alps, The Cryosphere,
     12, 3265–3285, https://doi.org/10.5194/tc-12-3265-2018, 2018.

   * the PISM authors: PISM, a Parallel Ice Sheet Model,
     http://www.pism-docs.org, 2017.

Journal [optional]
   --

Conference [optional]
   --

Book/Report/Chapter [optional]
   --

Thesis [optional]
   --

Subjects [optional]
   --
