""" roope todo """
from rasterstats import zonal_stats

# import rasterio
import geopandas as gpd


def get_raster_stats(
    gdf_edges: gpd.GeoDataFrame, raster_file_path: str, stats: str = "mean"
):
    """
    get raster stats for buffered edges
    Stats that can be used: "mean", "median", "max", "min", "count", "sum". Mean is default.
    """
    return zonal_stats(gdf_edges["buffer"], raster_file_path, stats=stats)

    # def extract_raster_value(self, src, geom):
    #     mid_point = geom.interpolate(0.5, normalized=True)
    #     row_idx, col_idx = src.index(mid_point.x, mid_point.y)
    #     return src.read(1)[row_idx, col_idx]

    # def extract_raster_values(self, road_network_gdf, raster_file_path):
    #     with rasterio.open(raster_file_path) as raster:
    #         raster_data = raster.read(1)
    #         road_network_gdf["raster_value"] = road_network_gdf.geometry.apply(
    #             lambda geom: self.extract_raster_value(raster_data, geom)
    #         )


# # gpt created...
# import rasterio
# import geopandas as gpd

# def extract_raster_values(road_gdf, raster_path):
#     with rasterio.open(raster_path) as src:
#         for index, road in road_gdf.iterrows():
#             # Example: Extract raster values for the midpoint of the road segment
#             mid_point = road.geometry.interpolate(0.5, normalized=True)
#             row_idx, col_idx = src.index(mid_point.x, mid_point.y)
#             road_gdf.at[index, 'raster_value'] = src.read(1)[row_idx, col_idx]

#     return road_gdf

# # Usage
# road_network_gdf = gpd.read_file('/path/to/road_network.gpkg')
# raster_file_path = '/path/to/raster.tif'
# road_network_gdf = extract_raster_values(road_network_gdf, raster_file_path)
