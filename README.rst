=============
Green Paths 2.0
=============

**GREEN PATHS 2 IS UNDER CONSTRUCTION**



.. image:: https://img.shields.io/pypi/v/green_paths_2.svg
        :target: https://pypi.python.org/pypi/green_paths_2

.. image:: https://img.shields.io/travis/roopehub/green_paths_2.svg
        :target: https://travis-ci.com/roopehub/green_paths_2

.. image:: https://readthedocs.org/projects/green-paths-2/badge/?version=latest
        :target: https://green-paths-2.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status











Green Paths 2 Framework
----------

Green Paths 2 consist of 3 different modules which can be run separately or together as pipeline. For general use, the whole (all) pipeline should be used. If running modules separately,
user should have run the required previoud modules using cache.

Green Paths 2 is heavily dependent on user configurations and data specifications. The user should have a good understanding of the data being used and configurations before using Green Paths 2.
Currently Green Paths 2 support client user interface via terminal / cmd.

See more on Green paths 2 framework and modules in the Green Paths 2 Modules and components section.









Detailed description of the commands:
----------

Preprocessing
- Preprocessing pipeline for processing and calculating exposure values for the OSM road network.

Routing
- Routing pipeline for using the preprocessing reusults for Multi-objective routing.

Analysing
- Analysing pipeline for analysing the results of the routing. The results are saved to the output folder as gpkg of csv files, depending if the results have geometries or not.

OSM network segmenter
- Segmenting the OSM road network into smaller segments to enable accurate exposure calculations. Natively OSM roads (ways) are expanding over multiple nodes (intersections),
and this is why they need to be split to smaller segments. Will save the segmented network to the cache folder. The cached file will be used in the preprocessing and all pipelines if found.
Will run segmenting for each different osm network file found from the user configurations.

Validator 
- User configurations validator for validating the user configuration yml file attributes. This should be ran before the pipe to enable successful run.

Descriptor
- Descriptor for describint the datas from user configurations. This functionality aims to help in filling the correct parameters to the user configuration yml file.


OSM network downloader
- Downloading the OSM road network data from the OSM API. User most likely should download the OSM PBF from other sources for more accurate road networks,
but this is a quick way to get the data for testing or general use.


Running the commands
----------

For unified approach on running task no matter the OS, we are using invoke.

To run the commands with invoke in the terminal / cmd, use the following commands.
The main commands are listed first and then all the variations of using flags and arguments are listed.

Base command and info:
- inv gp2
- inv gp2 --help

**all pipeline**

*commands*
        ``inv gp2 --args="all"``
        
        ``inv gp2 --args="all -uc"``

        ``inv gp2 --args="all --use-cache"``

descriptions_
        - Run all the pipelines in the correct order. The user configurations are validated before the pipeline starts.
        - Run the all pipline with the use of cache. The cache is used in the preprocessing and routing pipelines if found.

**preprocessing pipeline**

commands_
        - inv gp2 --args="preprocessing"
descriptions_
        - Run the preprocessing pipeline. The user configurations are validated before the pipeline starts. Saving the results to cache via user_config parameter.

**routing pipeline**

commands_
        ``inv gp2 --args="routing"``

descriptions_
        - Run the routing pipeline. Will use cached files if ran separately, if cached files not found, dont route. Will prioritize parameter exposure values, these are inputted in all pipeline. 

**analysing pipeline**

commands_
        ``inv gp2 --args="analysing"``

descriptions_
        - Run the analysing pipeline. Will try to use cached files if ran separately, if cached files not found, dont analyse. Will prioritize parameter exposure values, these are inputted in all pipeline.


**validate user configurations**

commands_
        ``inv gp2 --args="validate"``

descriptions_
        - Validate the user configurations. The user configurations are validated before the pipeline starts. It is recommended to run this before running the pipelines!

**describe user configurations**

commands_
        ``inv gp2 --args="describe"``

descriptions_
        - Describe the user configurations. The descriptor will help to find the possible values for the user configurations.

**clear cache**

commands_
        ``inv gp2 --args="clear_cache -d"``

        ``inv gp2 --args="clear_cache --dirs"``


descriptions_
        - Clear the cache folder. This will remove all the cached files from the cache folder. Clear the wanted directories under cache. Use with caution!
        - Possible directories to clear: all, preprocessing, routing, analysing, final_exposure_results, osm_network_segmenter, osm_network_downloader

**osm network segmenter**

commands_
        ``inv gp2 --args="osm_network_segmenter"``

descriptions_
        - Segment the OSM road network into smaller segments to enable accurate exposure calculations. Will save the segmented network to the cache folder.

**osm network downloader**

commands_
        ``inv gp2 --args="osm_network_downloader"``

descriptions_
        - Download the OSM road network data from the OSM API. User most likely should download the OSM PBF from other sources for more accurate road networks,
        but this is a quick way to get the data for testing or general network use.
        - Recommended to use e.g. `bbbike.org https://extract.bbbike.org/` to download the OSM PBF. Try not to download extensive areas, as the processing times will increase as the network does. Use only needed areas.



Running the commands fallback for Windows
----------

If the inv command is not working, you can run the commands with poetry:

All commands are run with prefix

``poetry run python green_paths_2_cli.py --args="<commands -args>"``

_replace the <commands -args> with the actual command and arguments_

e.g. ``poetry run python green_paths_2_cli.py --args="routing -uc"``

See all possibilities from Running the commands section.



Running the commands fallback for Mac / Linux
----------

If the inv command is not working, you can run the commands with poetry or make:

In addition to poetry, cli can be used with make in unix based systems: 

``make gp2 ARGS="<command -args>"``



Description of Green Paths 2 Modules and components
----------


TODO: detailed descriptions go here...

User configurations



Data requirements



Green paths 2 consist of 3 main modules:

preprocessing:

        osm_processor
        - [ ] convert osm_processor to cli
        - [ ] put paths to confs
        - [ ] add tests for osm_processor

        etc...

routing:

        - [ ] todo todo
        etc...

analysing:

        - [ ] todo todo
        etc...


Saving the results
----------

The final exposure results are saved to the output folder as gpkg or csv files, depending if the results have geometries or not.

User can also choose to save:
- The raster from preprocessing by defining the save_raster parameter in the user configurations.
- The geometries from the routing by defining the save_geometries parameter in the user configurations.
- The 



Future developments and ideas
----------

- Currently the GP2 supports only cloning the repo and setting up conda environment. Should gp2 be pip installable or dockerized in the future?


For Developers
----------

After the first "prototype" version of GP2 is ready, the development will most likely not continue actively.
Developers can still contribute to the project by forking the repository and optionally creating a pull request.

Issues and bugs are also very welcome, and I will try to fix them as soon as possible, but no guarantees on the time frame.






* Free software: MIT license
* Documentation: https://green-paths-2.readthedocs.io.


Credits
-------

- r5
- r5py
- GP1

- cookiecutter
- poetry
- all other dependencies


References
----------

For details on the core methods implemented in Conveyal Analysis and R5, see:
- `Conway, Byrd, and van der Linden (2017) https://keep.lib.asu.edu/items/127809`.
- `Conway, Byrd, and van Eggermond (2018) https://www.jtlu.org/index.php/jtlu/article/view/1074`.
- `Conway and Stewart (2019) https://files.indicatrix.org/Conway-Stewart-2019-Charlie-Fare-Constraints.pdf`.








This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
