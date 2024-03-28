""" TODO """

# just a note to myself

# need probably do something like this to save the network to the API's memory to be able to use it in the routing, not having to create it every time

# also TODO: figure out if wanna use flask?!

# from flask import Flask
# import r5py

# app = Flask(__name__)

# # Global variable to store the network
# custom_cost_network = None

# @app.before_first_request
# def initialize_network():
#     global custom_cost_network
#     # Logic to create and configure your CustomCostTransportNetwork
#     custom_cost_network = r5py.CustomCostTransportNetwork(...)

# @app.route('/route', methods=['GET'])
# def route():
#     # Use custom_cost_network for routing
#     # Ensure to handle the case where custom_cost_network might be None
#     if custom_cost_network is not None:
#         # Perform routing
#         pass
#     else:
#         # Handle error or try to reinitialize the network
#         pass
#     return ...

# if __name__ == '__main__':
#     app.run(debug=True)
