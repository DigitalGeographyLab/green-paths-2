""" Raster processing module. """

from rasterstats import zonal_stats

# import rasterio
import geopandas as gpd


# Not used yet, check if needed
def get_raster_stats(
    gdf_edges: gpd.GeoDataFrame, raster_file_path: str, stats: str = "mean"
):
    """
    get raster stats for buffered edges
    Stats that can be used: "mean", "median", "max", "min", "count", "sum". Mean is default.
    """
    return zonal_stats(gdf_edges["buffer"], raster_file_path, stats=stats)
