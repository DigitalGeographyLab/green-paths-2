import datetime
import os
import osmium
import sys

OSM_PROCESSED_NETWORK_DIR_PATH = "src/preprocessing/osm_processing/processed_network"
OSM_PROCESSED_NETWORK_NAME = "processed_network_helsinki.osm.pbf"
OSM_PROCESSED_NETWORK_PATH = os.path.join(
    OSM_PROCESSED_NETWORK_DIR_PATH, OSM_PROCESSED_NETWORK_NAME
)


# First, we need a handler to collect intersection nodes.
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


def generate_new_id(counter):
    return -1000000000 - counter


class SegmentCreator(osmium.SimpleHandler):
    def __init__(self, intersection_nodes):
        osmium.SimpleHandler.__init__(self)
        self.intersection_nodes = intersection_nodes
        self.segments = []

    def way(self, w):
        current_segment_nodes = []
        for node in w.nodes:
            current_segment_nodes.append(node.ref)  # Store node references
            if is_cutting_point(node, self.intersection_nodes):
                if len(current_segment_nodes) > 1:
                    # Deep-copy tags into a Python dict
                    tags_dict = {tag.k: tag.v for tag in w.tags}
                    parent_id_tag = {"parent_id": str(w.id)}
                    merged_tags = {**tags_dict, **parent_id_tag}
                    # tags_dict["parent_id"] = w.id
                    self.segments.append(
                        {
                            "nodes": current_segment_nodes.copy(),  # Make a copy of the list
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


TEST_OSM_FILE_PATH = "/Users/hcroope/omat/GP2/r5py_gp2/src/elias_article/helsinki_test_files_from_elias/Helsinki.osm.pbf"


# Handler to copy nodes
class NodeCopyHandler(osmium.SimpleHandler):
    def __init__(self, writer):
        super().__init__()
        self.writer = writer

    def node(self, n):
        self.writer.add_node(n)


# Initialize writer for the new OSM PBF file
writer = osmium.SimpleWriter(OSM_PROCESSED_NETWORK_PATH)

# Create an instance of the handler, passing the writer to it
node_handler = NodeCopyHandler(writer)

# Use the handler to process the file
node_handler.apply_file(TEST_OSM_FILE_PATH)


# Load intersection nodes
collector = IntersectionCollector()
collector.apply_file(TEST_OSM_FILE_PATH)
intersection_nodes = collector.intersection_nodes

# Create segments based on the collected intersection nodes
creator = SegmentCreator(intersection_nodes)
creator.apply_file(TEST_OSM_FILE_PATH)


# Now, write these segments to a new PBF file with PyOsmium
# writer = osmium.SimpleWriter(OSM_PROCESSED_NETWORK_PATH)

for i, segment in enumerate(creator.segments):
    print(segment)
    print(segment["tags"])

    unique_new_id = generate_new_id(i)
    # segment["id"] = unique_new_id
    way = osmium.osm.mutable.Way(
        segment,
        id=unique_new_id,
        version=1,
        visible=True,
        changeset=1,
        timestamp=datetime.datetime.now(),
        uid=1,
        user="YourUserName",
        tags=dict(segment["tags"]),
        nodes=list(segment["nodes"]),
    )

    # Setting basic attributes
    # way.version = 1
    # way.visible = True
    # way.changeset = 1
    # way.timestamp = datetime.datetime.now()
    # way.uid = 1  # Use an appropriate user ID
    # way.user = "YourUserName"

    # way.replace(
    #     tags=dict(segment["tags"]), nodes=list(segment["nodes"]), id=unique_new_id
    # )

    # way.tags.add("highway", "residential")
    # way.tags = segment["tags"]

    # Setting node references
    # for ref in :
    # way.nodes = segment["nodes"]

    # way.nodes = [osmium.osm.NodeRef(ref) for ref in segment["nodes"]]

    # way = osmium.osm.Way()
    # print(way)
    # print(way.id)
    # print(way.tags)
    # # Add tags to the way
    # for k, v in segment["tags"].items():
    #     way.tags.add(k, v)

    # print(way.tags)
    # writer.add_way(segment)
    # exit()

    # # Add the 'parent_id' tag
    # way.tags.add("parent_id", str(segment["parent_id"]))

    # exit()
    # way.id = generate_new_id(i)
    # for k, v in segment["tags"].items():
    #     way.tags.add(k, v)
    # way.tags.add("parent_id", str(segment["parent_id"]))

    # # Write the way to the file
    writer.add_way(way)
    # for node in segment["nodes"]:
    #     writer.add_node(node)  # osmium.osm.NodeRef(ref=node)
# reader.close()
writer.close()
