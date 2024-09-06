# Overview
Green Paths 2.0 finds environmental exposure optimized paths with flexibility for spatial and temporal context and data sources. It can be used for single trip one-to-one path finding, or large mass calculations of one-to-many or many-to-many path findings.
Its usage requires at least moderate expertise in filling the configurations correctly, and being able to interpret the results.

## Background
Green Paths 2 is the next iteration, and heavily influenced on the previous version of [Green Paths](https://www.helsinki.fi/en/researchgroups/digital-geography-lab/green-paths)
developed by Joose Helle for his Geography masters thesis and for [Digital Geography Lab, University of Helsinki](https://www.helsinki.fi/en/researchgroups/digital-geography-lab). See also the [Green Paths Web GUI](https://green-paths.web.app/?map=streets). 

Where in Green Paths (1.0) worked in Helsinki Metropolitan Region with air quality, greenery and noise data, Green Paths 2.0 can be transfered to different cities, it supports multiple different data sets and formats and is relatively computationally powerful due to using the R5 software package as its routing engine.


## Green Paths 2.0 Framework
Green Paths 2.0 uses spatial data in multiple formats (vector, raster) to add exposure costs to the OSM street network segments. 

GP2 consists of three main modules (or pipelines):

- preprocessing
- routing
- exposure analysis

These modules separate the logic of calculating environmental exposure for OSM segments, routing with environmental weights, and analysing environmental exposures from the selected routes.

```{hint}
See more from [Modules and Components](#modules_and_components)
```

## User configurations
Green Paths 2.0 relies heavily on user configurations in order to work. All of the necessary tool configurations are filled in the [YAML](https://yaml.org/).

The user configurations: config.yaml can befound in /user/ directory in GP2 root directory.
In case a custom path for user configuration needs to be used, it can be passed in as argument, see [cli user interface](#cli_user_interface)

```{hint}
See more from [User Configurations](#user_configurations)
```
## Routing engine
The segment exposure values are then used to route healthier paths with the by using [Conveyal's R5: Rapid Realistic Routing on Real-world and Reimagined networks](https://github.com/conveyal/r5) via python interface of [r5py: Rapid Realistic Routing with R5 in Python](https://github.com/r5py/r5py). The routing returns lists of OSM ID's taken during routing, and uses those OSM ID's to combine and calculate segment exposure values (combined with Preprocessing raw exposure values).

GP2 is using patched forks from Digital Geography Lab's r5 [R5](https://github.com/DigitalGeographyLab/r5/tree/gp2) (branch GP2) and r5py modified fork [R5PY_GP2](https://github.com/DigitalGeographyLab/r5py_gp2).

## Output Results
The output results can befound in /results_output directory in the GP2 root directory.
Also the resulting exposure rasters will be located in this folder.


## Geography Masters Thesis (completed June 2024)
Green Paths 2.0 was part of the Master's thesis by Roope Heinonen made for the [Digital Geography Lab](https://www.helsinki.fi/en/researchgroups/digital-geography-lab) in the University of Helsinki.

See the detailed documentation for the sofrware [R. Heinonen's Geography Masters Thesis](https://helda.helsinki.fi/items/5b77f6c3-2d2c-455f-bb8c-528b0ac136d8) 

Heinonen, R., 2024. Green Paths 2.0: Developing a Transferable Multi-Objective Environmental Exposure Optimizing Route Planning tool for Active Travel (MSc thesis). University of Helsinki, Helsinki. (https://helda.helsinki.fi/items/5b77f6c3-2d2c-455f-bb8c-528b0ac136d8) 

The Green Paths 2.0 affiliated projects are: [Urban Air Quality 2.0 (UAQ2.0)](https://www.hsy.fi/en/hsy/hsys-projects/project-pages/urban-air-quality-2.0-project/) and [GREENTRAVEL](https://www.helsinki.fi/en/researchgroups/digital-geography-lab/projects/greentravel). GP2 was funded by UAQ2.0.

