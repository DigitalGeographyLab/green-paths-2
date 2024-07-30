# Modules and Components

Green Paths 2.0 consist of 3 main modules and 2 routing dependencies. 

The 3 modules are

- Preprocessing: calculating exposure values from exposure data to OSM road segments.
- Routing: routing with custom costs which are expoure weighted.
- (Exposure) Analysing: calculating exposure analytics from paths taken.

The 2 routing dependencies are

- r5: Java written route finding library.
- r5py: Python written wrapper interface for utilizing r5 with python.


The following section will go through the main components briefly. For more detailed descriptions, refer to [R. Heinonen's Geography Masters Thesis](https://helda.helsinki.fi/items/5b77f6c3-2d2c-455f-bb8c-528b0ac136d8) (some parts are outdated).

<p align="center">
  <img src="_static/img/GP2_general_flowchart_legit.final.png" alt="Green Paths 2.0 general flowchart" width="850" height="600">
  </br>
  <i>Green Paths 2.0 general flowchart. The modules / pipelines are not transfering OSM ID's etc. anymore, everything goes to and from sqlite3.</i>
</p>

### Post-thesis Improvements

There has been couple of main improvements after the thesis. 

- The cache is moved from directory based saving to use Sqlite3. All modules save their results to the local db.
- The routing module (and dependencies r5, r5py) support now the precalculations. This meanst that custom cost values for segments are by default calcutated before the actual routing to the segments.
This should make the routing process faster, especially for larger mass route plannings.


## Preprocessing

Preprocessing module is responsible for calculating raw and normalized exposure values for OSM segments, in order to weighten the A* costs for edges.

<p align="center">
  <img src="_static/img/GP2_preprocessing_legit_2drawio.png" alt="Preprocessing flow chart" width="750" height="500">
  </br>
  <i>Preprocessing module flowchart. The "cache" is currenly sqlite3.</i>
</p>

### OSM Network
OSM network goes through segmentation, which means that the native OSM ways are split from intersections. This is necessary as we are using OSM ID's as the common key in all of the modules.
Native OSM ways can expand over multiple intersections, possibly adding too long roads for some OSM ID's compared to the actual road taken during route finding.
The segments are then given new negative OSM ID's which are used in context of Green Paths 2.0.

The OSM network is then converted to geopandas geodataframe. This might not be the fastest solution, but it adds support to various input filetypes.

### Rasterization pipeline
The rasterization pipeline is executed for vector data types. Based on user input the vector data is rasterized, by taking the maximum value found inside the raster cells, making the raster size important to consider.

Raster exposure data is used as is, unless raster cell size is defined in user configurations, then the raster is reprojected to given resolution.

### Overlay analysis
The exposure raster for each exposure data source is overlayed with the OSM road network. Sampling points are created for each segment, thei points average is calculated, and that is saved as the segments exposure value for that exposure.

### Normalization
All of the "raw" exposure values are then normalized based on user configurations theoretical min and max values for that data. The scale is between 0-1. This is done to be able to compare different exposure data.
This normalized exposure factor is passed to the routing module (with sensitivity weight) to update each segmnents traversal time costs.


## Routing
The routing module uses the normalized exposure values and OSM ID's to create a custom cost mapping for the routing process, which is used to modify the segment traversal cost by using the time and exposure(s).
After the path is taken, it will see what all OSM ID's were traversed and save a list of OSM ID's per path to the Sqlite3 db. Also the actual travel time seconds are saved, before altering the traversal cost.

<p align="center">
  <img src="_static/img/GP2_routing_flowchart.drawio.png" alt="A map showing Health index created from the Helsinki metropolitan area" width="750" height="500">
  </br>
  <i>Routing module flowchart.</i>
</p>

## Analysing
The Analysing module calculates the exposures for each path taken, by combining the OSM ID's returned from routing module and the values found from the exposure database table, using OSM ID as common key.


<p align="center">
  <img src="_static/img/GP2_analysing_flowchart.drawio.png" alt="A map showing Health index created from the Helsinki metropolitan area" width="750" height="500">
  </br>
  <i>Exposure analysing module flowchart. Logic of looping the paths has changed a little after improvements. </i>
</p>

