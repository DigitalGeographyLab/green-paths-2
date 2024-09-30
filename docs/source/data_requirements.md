# DATA REQUIREMENTS

Green Paths 2.0 supports different raster and vector data formats, and multiple simultaneous exposure data sources.

Data sources are filled in the user configurations file, and the data need to be on the users local machine.
See the instructions on how to fill the user configurations in the user configurations section.

```{important}
The exposure data should have numerical values (float) for the exposure calculations.
```

## OSM PBF

A OSM PBF file is needed, and it can be downloaded from various online sources, see e.g.:

- [Bbbike.org](https://extract.bbbike.org/)
- [Geofabrik.de](https://download.geofabrik.de/) (street network should have as small extent as possible, so cropping might be required)


## OD files

Origins and destinations need to be set to a filepath. Supported filetypes: gpkg and csv.

The OD's need to have a lowercase "id" column for all origin and destination point! 

Cvs data needs additionally the crs, and od_lon_name and od_lat_name which should correspond to the column header names.


## Supported Exposure Data File Types

| Type   | File Extension           |
|--------|---------------------------|
| Vector | .gpkg                    |
| Vector | .shp                     |
| Vector | .geojson / .topojson     |
| Vector | .gdb                     |
| Vector | .kml                     |
| Vector | .tab / .mif              |
| Raster | .tif / .tiff             |
| Raster | .jp2 / .j2k              |
| Raster | .nc                      |
| Raster | .h5 / .hdf               |
| Raster | .asc                     |
| Raster | .mbtiles                 |
| Raster | .grib / .grb             |
| Raster | .rpf / .cadrg / .cib     |



```{warning}
Not all filetypes are yet properly tested. Tested types: shp, tif, gpkg, nc, and gml.
```

## GENERAL

The CRS of project needs to be in metric CRS, not in degrees!

