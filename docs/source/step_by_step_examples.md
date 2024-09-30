# Step-by-Step Example

Lets say we would like to create a greenery matrix of Some city..

```{attention}
Remember that you can run the example all pipeline by: inv gp2 -a "-c green_paths_2/user/working_example_config.yaml all"
```

0. Get familiar with documentation.

<div class="separator_line"></div>

1. Gather the exposure data and download the OSM street network to a reasonable folder.

<div class="separator_line"></div>

2. (optional) Open the exposure data etc. in e.g. QGIS to explore the exposure data and OSM network

<div class="separator_line"></div>

3. Install the Green Paths 2.0 by following the instructions

<div class="separator_line"></div>

4. Start filling the user configuration in green_paths_2/src/user/config.yaml

<div class="separator_line"></div>

5. (optional) Run inv gp2 -a describe (to describe your exposure data). THIS CURRENTLY NEEDS PASSING VALID USER CONFIGURATION (can have incorrect values, as long as types are correct, should improve this...).

<div class="separator_line"></div>

6. Run inv gp2 -a validate (to see if the configuration is properly filled)

<div class="separator_line"></div>

7. The user configurations is passing! Double check it! Do have a coffee break!

<div class="separator_line"></div>

8. Run the preprocessing pipeline: inv gp2 -a preprocessing

<div class="separator_line"></div>

9. (optional) Set "save_raster_file: True" to all exposure data sources, and inspect the created exposure rasters! Especially if using vector data!

<div class="separator_line"></div>

10. Run preprocessing again if needed. When exposure rasters seem good run: inv gp2 -a "all -uc". Note! Remember to configure e.g. keep_geometry correctly for the needs.

<div class="separator_line"></div>

11. Inspect the results. If keep geometry is True, open the paths in QGIS and inspect.

<div class="separator_line"></div>

12. Use resulting file to do further post analysing of the exposures!

<div class="separator_line"></div>

13. Travel safe and healthy!

