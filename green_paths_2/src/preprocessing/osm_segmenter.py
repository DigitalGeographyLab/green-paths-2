""" Segment the OSM network into segments between intersections. """

import datetime
import os
import osmium

from green_paths_2.src.config import (
    DATA_CACHE_DIR_PATH,
    OSM_CACHE_DIR_NAME,
    OSM_CACHE_SEGMENTED_DIR_NAME,
    OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION,
)
from green_paths_2.src.logging import setup_logger, LoggerColors
from green_paths_2.src.timer import time_logger

LOG = setup_logger(__name__, LoggerColors.RED.value)


class IntersectionCollector(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.node_refs = set()
        self.intersection_nodes = set()

    def way(self, w):
        for node in w.nodes:
            if node.ref in self.node_refs:
                self.intersection_nodes.add(node.ref)
            else:
                self.node_refs.add(node.ref)


# Check if a node is a cutting point
def is_cutting_point(node, intersection_nodes):
    return node.ref in intersection_nodes


# Create a new unique ID for the segment
# minus sign is used to avoid conflicts with existing IDs
# and to indicate that these are not real OSM IDs from the OSM database
def generate_new_id(counter):
    return -1_000_000_000_000 - counter


class SegmentCreator(osmium.SimpleHandler):
    def __init__(self, intersection_nodes):
        osmium.SimpleHandler.__init__(self)
        self.intersection_nodes = intersection_nodes
        self.segments = []

    def way(self, w):
        current_segment_nodes = []
        for node in w.nodes:
            # Store node references
            current_segment_nodes.append(node.ref)
            if is_cutting_point(node, self.intersection_nodes):
                if len(current_segment_nodes) > 1:
                    # Deep-copy tags into a Python dict
                    tags_dict = {tag.k: tag.v for tag in w.tags}
                    parent_id_tag = {"parent_id": str(w.id)}
                    merged_tags = {**tags_dict, **parent_id_tag}
                    # tags_dict["parent_id"] = w.id
                    self.segments.append(
                        {
                            "nodes": current_segment_nodes.copy(),
                            "tags": merged_tags,
                        }
                    )
                current_segment_nodes = [node.ref]

        # Handle the last segment
        if len(current_segment_nodes) > 1:
            tags_dict = {tag.k: tag.v for tag in w.tags}
            parent_id_tag = {"parent_id": str(w.id)}
            merged_tags = {**tags_dict, **parent_id_tag}
            self.segments.append(
                {
                    "nodes": current_segment_nodes.copy(),
                    "tags": merged_tags,
                }
            )


# Handler to copy nodes
class NodeCopyHandler(osmium.SimpleHandler):
    def __init__(self, writer):
        super().__init__()
        self.writer = writer

    def node(self, n):
        self.writer.add_node(n)


@time_logger
def segment_or_use_cache_osm_network(osm_source_path: str) -> str:
    """
    Segment the OSM network into segments between intersections.
    The name is taken from the source path if not provided.

    Preprocessing pipeline will search for the segmented OSM network from the cache directory.
    Using name pattern <filename>_segmented.osm.pbf.

    :param osm_source_path: Path to the OSM PBF file.
    :param name: Name for the segmented OSM PBF file. If not provided, the default name is used.
    :return: Path to the segmented OSM PBF file.
    """
    LOG.info(f"Starting to segment the OSM network.")
    LOG.info(f"Using file from path: {osm_source_path}")
    # use user provided name or
    # get 'filename' from the path
    network_name_no_extension = os.path.basename(osm_source_path).rsplit(".osm.pbf", 1)[
        0
    ]
    if not "_segmented" in network_name_no_extension:
        osm_network_name = (
            network_name_no_extension + OSM_SEGMENTED_DEFAULT_FILE_NAME_EXTENSION
        )
    else:
        osm_network_name = network_name_no_extension + ".osm.pbf"

    # format path from config
    OSM_PROCESSED_NETWORK_PATH = os.path.join(
        DATA_CACHE_DIR_PATH,
        OSM_CACHE_DIR_NAME,
        OSM_CACHE_SEGMENTED_DIR_NAME,
        osm_network_name,
    )

    LOG.info(
        f"Checking cache for segmented OSM network from {OSM_PROCESSED_NETWORK_PATH}"
    )

    if os.path.exists(OSM_PROCESSED_NETWORK_PATH):
        LOG.info(f"Found segmented OSM network from cache. Skipping segmentation.")
        return OSM_PROCESSED_NETWORK_PATH

    LOG.info(f"Segmenting the OSM network to path: {OSM_PROCESSED_NETWORK_PATH}")
    # Initialize writer for the new OSM PBF file
    writer = osmium.SimpleWriter(OSM_PROCESSED_NETWORK_PATH)
    node_handler = NodeCopyHandler(writer)
    # Process the OSM file with the node handler
    node_handler.apply_file(osm_source_path)

    # Load intersection nodes
    collector = IntersectionCollector()
    collector.apply_file(osm_source_path)
    intersection_nodes = collector.intersection_nodes

    # Create segments based on the collected intersection nodes
    creator = SegmentCreator(intersection_nodes)
    creator.apply_file(osm_source_path)

    for i, segment in enumerate(creator.segments):
        unique_new_id = generate_new_id(i)
        way = osmium.osm.mutable.Way(
            segment,
            id=unique_new_id,
            version=1,
            visible=True,
            changeset=1,
            timestamp=datetime.datetime.now(),
            uid=1,
            user="GreenPaths2",
            tags=dict(segment["tags"]),
            nodes=list(segment["nodes"]),
        )

        # write the way to the new OSM PBF file
        writer.add_way(way)
    writer.close()
    LOG.info(f"Segmenting the OSM network finished.")
