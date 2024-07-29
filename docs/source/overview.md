# Overview
Green Paths 2.0 finds environmental exposure optimized paths with flexibility for spatial-temporal extend and data sources. It can be used for single trip one-to-one path finding, or large masscalculations of one-to-many or many-to-many path findings.
Its usage requires at least moderate expertise in filling the configurations correctly, and being able to interpret the results.

## Background
Green Paths 2 is the next iteration, and heavily influenced on the previous version of [Green Paths](https://www.helsinki.fi/en/researchgroups/digital-geography-lab/green-paths)
developed by Joose Helle for his Geography masters thesis and for [Digital Geography Lab, University of Helsinki](https://www.helsinki.fi/en/researchgroups/digital-geography-lab), See also the [Green Paths Web GUI](https://green-paths.web.app/?map=streets). 

Where in Green Paths (1.0) worked in Helsinki Metropolitan Region with Air quality, greenery and noise environmental exposure data, Green Paths 2.0 can be transfered to different cities, it supports multiple different data sets and is relatively computationally powerful due to using R5 as its routing engine.


## Green Paths 2.0 Framework
Green Paths 2.0 uses users spatial data (vector, raster) to weighten the OSM street network segments. It then uses 

GP2 consists of three main modules (or pipelines):

- preprocessing
- routing
- exposure analysing

These modules separate the logic of calculating environmental exposure for OSM segments, routing with environmental weights, and analysing exposures during routes taken.

```{hint}
See more from [Modules and Components](#modules_and_components)
```

## User configurations
Green Paths 2.0 relies heavily on user configurations in order to work. All of the necessary tool configurations are filled in the [YAML](https://yaml.org/).

```{hint}
See more from [User Configurations](#user_configuration)
```

## Routing
The segment exposure values are then used to route healthier paths with the by using [Conveyal's R5: Rapid Realistic Routing on Real-world and Reimagined networks](https://github.com/conveyal/r5) via python interface of [r5py: Rapid Realistic Routing with R5 in Python](https://github.com/r5py/r5py). The routing returns lists of OSM ID's taken during routing, and uses those OSM ID's to combine and calculate segment exposure values (combined with Preprocessing raw exposure values).

GP2 is using patched forks from Digital Geography Lab's r5 [R5](https://github.com/DigitalGeographyLab/r5/tree/gp2) (branch GP2) and r5py modified fork [R5PY_GP2](https://github.com/DigitalGeographyLab/r5py_gp2).


## Geography Masters Thesis (outdated)
See detailed documentation also from the developers [Geography Masters Thesis](https://helda.helsinki.fi/items/5b77f6c3-2d2c-455f-bb8c-528b0ac136d8) made in University of Helsinki for the [Digital Geography Lab](https://www.helsinki.fi/en/researchgroups/digital-geography-lab).

The Green Paths 2.0 affiliate projects are: [Urban Air Quality 2.0 (UAQ2.0)](https://www.hsy.fi/en/hsy/hsys-projects/project-pages/urban-air-quality-2.0-project/) and [GREENTRAVEL](https://www.helsinki.fi/en/researchgroups/digital-geography-lab/projects/greentravel). GP2 was funded by UAQ2.0.

