""" TODO """

import os
import multiprocessing as mp
import pandas as pd
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.CYAN.value)


# TODO -_> set to confs
def determine_num_processes(gdf, small_threshold=50000, medium_threshold=200000):
    """determine number of processes to use for parallel processing"""
    num_cores = os.cpu_count()
    num_rows = len(gdf)
    if num_rows <= small_threshold:
        # use 1/4th of the cores for small datasets
        return max(1, num_cores // 4)
    elif small_threshold < num_rows <= medium_threshold:
        # 1/2 for medium
        return max(1, num_cores // 2)
    else:
        # use all -1 for large
        return num_cores - 1


def chunk_gdf(gdf, n):
    """createa a list of n equal chunks from a GeoDataFrame"""
    chunk_size = len(gdf) // n
    chunks = [gdf.iloc[i : i + chunk_size] for i in range(0, len(gdf), chunk_size)]
    for chunk in chunks:
        if not chunk.geometry.is_valid.all():
            LOG.info("After chunking, invalid geometry in gdf")
    return chunks


# @time_logger
def apply_parallel(gdf, func, num_processes=None, **func_kwargs):
    """apply a function to a GeoDataFrame in parallel"""
    # define number of cores to use based on gdf size
    # if num_processes is explicitly given, use that
    if not num_processes:
        num_processes = determine_num_processes(gdf)
    LOG.info(f"Using {num_processes} processes for parallel processing")
    # split geodataframe to chunks
    gdf_chunks = chunk_gdf(gdf, num_processes)
    LOG.info(f"Split GeoDataFrame to {len(gdf_chunks)} chunks")
    # create multiprocessing pool
    pool = mp.Pool(processes=num_processes or mp.cpu_count())
    LOG.info("Running parallel processing")
    # apply function to each chunk
    results = pool.starmap(func, [(chunk, func_kwargs) for chunk in gdf_chunks])

    # close the pool and wait for the work to finish
    pool.close()
    pool.join()

    # Concatenate the results back into a single GeoDataFrame
    return pd.concat(results)
