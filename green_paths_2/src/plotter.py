""" Used to do simple plots from GeoDataFrames to see what's going on in the data. """

import os
import geopandas as gpd
import matplotlib.pyplot as plt

PLOT_DESTINATION_PATH = "src/visualizations"


def simple_plot_gdfs(
    gdf: gpd.GeoDataFrame, title: str = None, geometry_column_names: list = None
) -> None:
    """
    Plot GeoDataFrames with multiple geometry columns.

    :param gdf: GeoDataFrame to plot.
    :param title: Title of the plot.
    :param geometry_column_names: List of geometry column names to plot.

    :return: None
    """
    _, ax = plt.subplots(figsize=(10, 10))

    # list of color names
    colors = [
        "blue",
        "red",
        "green",
        "orange",
        "yellow",
        "purple",
        "brown",
        "pink",
        "gray",
        "olive",
        "cyan",
    ]

    new_dfs = []
    plot_name = ""

    for geometry_column_name in geometry_column_names:
        new_dfs.append(gpd.GeoDataFrame(gdf, geometry=geometry_column_name))
        plot_name += f"{geometry_column_name}_"

    for i, new_df in enumerate(new_dfs):
        new_df.plot(ax=ax, color=colors[i], alpha=0.5)

    ax.set_title(title)
    ax.set_xlabel("long")
    ax.set_ylabel("lat")

    # Set equal scaling by length
    plt.axis("equal")

    plot_full_name = f"{plot_name}{title}.png"
    save_path = os.path.join(PLOT_DESTINATION_PATH, plot_full_name)
    plt.savefig(save_path, dpi=300)
    plt.close()


# e.g. use example

# from .plotter import simple_plot_gdf

# simple_plot_gdf(
#     spatially_joined_edges_with_polygons,
#     "network_data",
#     ["geometry_network"],
# )
