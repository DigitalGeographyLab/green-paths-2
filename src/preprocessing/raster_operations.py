""" Raster processing module. """

import rasterio
import geopandas as gpd
from rasterstats import zonal_stats

from src.config import GDF_BUFFERED_GEOMETRY_NAME


# Not used yet, check if needed
def get_raster_stats(
    gdf_edges: gpd.GeoDataFrame, raster_file_path: str, stats: str = "mean"
):
    """
    get raster stats for edges
    Stats that can be used: "mean", "median", "max", "min", "count", "sum". Mean is default.
    """
    return zonal_stats(
        gdf_edges[GDF_BUFFERED_GEOMETRY_NAME], raster_file_path, stats=stats
    )


# def extract_raster_value(self, src, geom):
#         mid_point = geom.interpolate(0.5, normalized=True)
#         row_idx, col_idx = src.index(mid_point.x, mid_point.y)
#         return src.read(1)[row_idx, col_idx]

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


# new new new

# def aggregate_values(values, method='mean'):
#     if method == 'mean':
#         return sum(values) / len(values)
#     elif method == 'max':
#         return max(values)
#     elif method == 'min':
#         return min(values)
#     else:
#         raise ValueError("Unknown aggregation method")

# # create sampling points for each road segment
# # create points in start, middle and end of the road segment
# import geopandas as gpd
# from shapely.geometry import Point

# def generate_sampling_points(line):
#     return [Point(line.coords[0]),  # Start point
#             Point(line.interpolate(0.5, normalized=True)),  # Midpoint
#             Point(line.coords[-1])]  # End point

# # Apply the function to each road segment in your GeoDataFrame
# roads_gdf['sampling_points'] = roads_gdf['geometry'].apply(generate_sampling_points)

# import rasterio
# from rasterio.transform import from_origin
# from rasterio.sample import sample

# # Open your raster file
# with rasterio.open('your_raster_file.tif') as src:
#     # Example usage
#     for index, row in roads_gdf.iterrows():
#         points = [(pt.x, pt.y) for pt in row['sampling_points']]
#         values = list(sample(src, points))
#         aggregated_value = aggregate_values(values, method='mean')  # Or 'max', 'min'
#         # Update your GeoDataFrame or store this value as needed


import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin

def rasterize_vector_data():


# Load your vector data (assuming it's already loaded into `vector_data`)
# vector_data = gpd.read_file('your_vector_data.gpkg')

# Define raster transformation and size
cell_size = 10  # meters
bounds = vector_data.total_bounds
width = int((bounds[2] - bounds[0]) / cell_size)
height = int((bounds[3] - bounds[1]) / cell_size)
transform = from_origin(bounds[0], bounds[3], cell_size, cell_size)

# Initialize numpy arrays for raster
value_sum_raster = np.zeros((height, width))
count_raster = np.zeros((height, width))

# Function to convert geometries to raster indices (adjusted for your transform)
def geo_to_raster_index(geom, transform, bounds):
    col, row = ~transform * (geom.x, geom.y)  # Inverse transform to get row, col indices
    return int(row), int(col)

# Rasterize vector data
for index, row in vector_data.iterrows():
    geom = row.geometry.centroid  # Simplification for point data; adjust as needed for polygons
    row_idx, col_idx = geo_to_raster_index(geom, transform, bounds)
    if 0 <= row_idx < height and 0 <= col_idx < width:
        value_sum_raster[row_idx, col_idx] += row['value_attribute']
        count_raster[row_idx, col_idx] += 1

# Calculate mean values raster
mean_values_raster = np.divide(value_sum_raster, count_raster, where=count_raster!=0)

from shapely.geometry import Point

roads_gdf['sampling_points'] = roads_gdf['geometry'].apply(lambda x: [
    Point(x.coords[0]),
    Point(x.interpolate(0.5, normalized=True)),
    Point(x.coords[-1])
])

def aggregate_values(values, method='mean'):
    if method == 'mean':
        return np.mean(values)
    elif method == 'max':
        return np.max(values)
    elif method == 'min':
        return np.min(values)

# Iterate over road segments and sample the raster
for index, row in roads_gdf.iterrows():
    values = []
    for geom in row['sampling_points']:
        row_idx, col_idx = geo_to_raster_index(geom, transform, bounds)
        if 0 <= row_idx < height and 0 <= col_idx < width:
            values.append(mean_values_raster[row_idx, col_idx])
    
    # Aggregate sampled values
    aggregated_value = aggregate_values(values, method='mean')  # Or 'max', 'min'
    # Here, you could store this aggregated_value back into roads_gdf or another structure



# save the raster
    
import rasterio
from rasterio.transform import from_origin

# Define your output raster file path
output_raster_path = 'output_raster.tif'

# Define the raster metadata
raster_meta = {
    'driver': 'GTiff',
    'dtype': 'float32',
    'nodata': None,  # You can specify a nodata value here if you want
    'width': width,
    'height': height,
    'count': 1,  # Number of bands; we're creating a single-band raster
    'crs': '+proj=longlat +datum=WGS84 +no_defs',  # Update this to match your raster's CRS
    'transform': transform
}

# Save the raster
with rasterio.open(output_raster_path, 'w', **raster_meta) as dst:
    dst.write(mean_values_raster, 1)  # Write the mean_values_raster array to the first band



