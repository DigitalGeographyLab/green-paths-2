""" Segment the OSM network into segments between intersections. """

import datetime
import os
import osmium

from ..data_utilities import construct_osm_segmented_network_name
from ..green_paths_exceptions import OsmSegmenterError
from ..logging import setup_logger, LoggerColors
from ..timer import time_logger

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
# Initialize the base OSM ID
base_osm_id = -1


def generate_new_id():
    global base_osm_id
    new_id = base_osm_id
    base_osm_id -= 1
    return new_id


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
    try:
        LOG.info(f"Starting to segment the OSM network.")
        LOG.info(f"Using file from path: {osm_source_path}")
        osm_segmented_network_path = construct_osm_segmented_network_name(
            osm_source_path
        )

        if os.path.exists(osm_segmented_network_path):
            LOG.info(f"Found segmented OSM network from cache, checking if valid.")
            if not osm_pbf_is_valid(osm_segmented_network_path, max_ways=1000):
                raise ValueError(
                    f"Segmented OSM network file {osm_segmented_network_path} is not valid."
                )
            LOG.info(
                f"Found valid segmented OSM network from cache. Skipping segmentation."
            )
            return osm_segmented_network_path

        LOG.info(f"Segmenting the OSM network to path: {osm_segmented_network_path}")
        # Initialize writer for the new OSM PBF file
        writer = osmium.SimpleWriter(osm_segmented_network_path)
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

        for _, segment in enumerate(creator.segments):
            unique_new_id = generate_new_id()

            segment["tags"]["gp2_osm_id"] = str(unique_new_id)

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
    except OsmSegmenterError as e:
        # if something goes wrong, remove the file
        if os.path.exists(osm_segmented_network_path):
            os.remove(osm_segmented_network_path)
        LOG.error(f"Segmentation failed with error: {e}")
        raise e

    # simple check that osm.pbf is valid
    # TODO: commented the validity check out...
    if not osm_pbf_is_valid(osm_segmented_network_path, max_ways=1000):
        raise OsmSegmenterError(
            f"Segmented OSM network file {osm_segmented_network_path} is not valid."
        )
    LOG.info(f"Segmenting the OSM network finished.")
    return osm_segmented_network_path


# OSM PBF SIMPLE VALIDATION

# TODO: remove this?


class OSMValidationHandler(osmium.SimpleHandler):
    def __init__(self, max_ways=1000):
        super().__init__()
        self.max_ways = max_ways
        self.num_ways_processed = 0
        self.is_valid = True

    def way(self, w):
        if self.num_ways_processed >= self.max_ways:
            # maximum number of ways reached
            return

        if not self.is_way_valid(w):
            self.is_valid = False
            return

        self.num_ways_processed += 1

    def is_way_valid(self, way):
        return (
            "gp2_osm_id" in way.tags and "parent_id" in way.tags and len(way.nodes) >= 2
        )

    def report(self):
        LOG.info(
            f"OSM PBF validator checked validity for: {self.num_ways_processed} ways."
        )


def osm_pbf_is_valid(filepath: str, max_ways=1000) -> bool:
    handler = OSMValidationHandler(max_ways=max_ways)
    handler.apply_file(filepath, locations=False)
    handler.report()
    return handler.is_valid
