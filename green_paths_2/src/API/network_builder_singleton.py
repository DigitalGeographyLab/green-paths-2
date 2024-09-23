from .network_builder import NetworkBuilder

# used to be able to use one instance of NetworkBuilder in the whole API
# probably not the best approach, but it is a quick fix for now

# Create a single instance of NetworkBuilder
network_builder_instance = NetworkBuilder()
