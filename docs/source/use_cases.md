# Use Cases

Green Paths 2.0 is designed to provide excessive amount of flexibility, which demands expertise from the users.

GP2 supports use cases of:

- one-to-one single routes
- one-to-many routes with single origin and multiple destinations
- many-to-many masscalculations from all origins to all destinations

```{hint}
A general version for basic users could be done by hosting a configured version of Green Paths 2.0 online.
```

## Where can I use GP2

Anywhere there is some reasonable exposure data available, and OSM PBF street network file.
Technically the exposure data can be anything, as long as it is georeferenced vector/raster, has numerical values and has enough coverage.

## Single route: One-to-one
For routing single paths. The input OD files should both have only 1 point each.

## Many routes from single point: One-to-many
For routing from one origin to multiple destinations or vice versa. The input OD files should one have single point and other mutliple points.

## From all origins to all destinations: Many-to-many
For routing form all origin points to all destinations. The input OD files should both have mutliple points.

```{tip}
This could be used in planning or research for creating raster / matrices of exposures by e.g. grouping result origin ID's and calculating averages.
```

 
