Welcome to Green Paths 2's documentation!
=========================================

*"In a galaxy of routes, the green path you must choose. Join the Greenside" - Yoda gpt-4, "The Green Paths 2.0: The Return of the Greenery.*

Modern route planning platforms do not really give us information on exposures during active travel, nor the possibility to choose healthier paths. They should!

Green Paths 2.0 (GP2) is a transferable multi-objective environmental exposure optimization path finding tool written in Python.

GP2 is meant to be used by experts, such as researchers, planners, and developers, and supports one-to-one, one-to-many, and many-to-many path finding.

Flexibility and transferability have been one of the main focus and thus the tools is designed to be usable in any city with some meaningfull exposure data and OSM pbf available.

It gets its efficient path finding using `Conveyal’s R5: Rapid Realistic Routing on Real-world and Reimagined networks <https://github.com/conveyal/r5>`_ via python interface of `r5py: Rapid Realistic Routing with R5 in Python <https://github.com/r5py/r5py>`_.


.. image:: _static/img/hki_health_map.png
   :alt: A map showing Health index created from the Helsinki metropolitan area
   :width: 750px
   :height: 500px
   :align: center
   :scale: 75

*A health index map created with environmental exposures of gvi, aqi and noise using Green Paths 2.0*

.. toctree::
   :maxdepth: 3
   :caption: Documentation:
   :hidden:

   Overview <overview>
   Modules and Components <modules_and_components> 
   Credits License and Affiliations <credits_license_and_citations>

.. toctree::
   :maxdepth: 3
   :caption: User Guide:
   :hidden:

   Quickstart <quickstart>
   Installation <installation>
   Data Requirements <data_requirements>
   User Configurations <user_configurations>
   User Interface <cli_user_interface>
   Use Cases <use_cases>
   Step by Step Example <step_by_step_examples>

.. Indices and tables
.. ==================
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
