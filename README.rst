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




"In a galaxy of routes, the green path you must choose. Join the Greenside" - Yoda (gpt-4), "The Green Paths 2.0: The Return of the Greenery


**Green Paths 2.0 (GP2) a Multi-objective exposure routing for healthier paths choices**


GP2 uses OpenStreetMap (OSM) road network and user defined datas from flexible user_configurations.yml file to calculate the exposure values for the road network.
The exposure values are then used to route healthier paths with the help of Conveyal's `r5 https://github.com/conveyal/r5` routing engine
and python wrapper `r5py https://github.com/r5py/r5py`. It then calculates exposure results for the taken paths and returns the results in the final_exposure_results folder.

Green Paths 2 is the next iteration, and heavily depending on the current version: `Green Paths https://www.helsinki.fi/en/researchgroups/digital-geography-lab/green-paths` and `Github https://github.com/DigitalGeographyLab/green-path-server`,
developed by Joose Helle for his Geography masters thesis and for `Digital Geography Lab, University of Helsinki https://www.helsinki.fi/en/researchgroups/digital-geography-lab`.

Green Paths is a proof-of-concept bi-objective routing tool for Helsinki Metropolitan area, supporting: Greenery, hourly air quality and noise exposures.

The Green Paths 2 aims to enable more powerful masscalculations to use for flexible cities and datas. GP2 can thus be ran any where where there is OSM road network and exposure data available. The source has been written from scratch, excluding some functionalities from the original Green Paths.

See also the `Green Paths Web GUI https://green-paths.web.app/?map=streets`


        GP2 is using patched forks from r5 modified fork `R5_GP2 https://github.com/DigitalGeographyLab/r5/tree/gp2` and r5py modified fork `R5_GP2 https://github.com/DigitalGeographyLab/r5py_gp2`.


Quickstart for Green Paths 2.0
----------

Remember to check the prerequisites:
- All OS: Miniconda or Anaconda
- Windows: Microsoft Visual Build Tools C++ 14.0 or greater
See instructions from the installation section.

See also the data requirements and instructions on how to fill the user configurations!

1. Clone the repository from GitHub:

        ``git clone https://github.com/DigitalGeographyLab/green-paths-2``

2. Navigate to the Green Paths 2 root folder:

        ``cd green-paths-2``

3. Install Green Paths 2. Remember to run the CLI as administrator. Run the installation script from the root folder:
        
        Windows:
        ``install_green_paths_2.bat``

        Mac / Linux:
        ``./install_green_paths_2.sh``

        NOTE: If the installation script has errors, please check the prerequisites!

        Remember to deactivate the conda environment before installing and re-activate it after installation!

                and check the prerequisites for the installation from the installation section!


4. Activate the conda environment:
        
        ``conda activate green_paths_2``

5. Fill in the user configurations in the **user/config.yml** file.

        For help use the **Descriptor**, which will help to find the possible values for the user configurations.

        ``inv gp2 --args="describe"``

6. Validate the user configurations before running the pipeline.

        ``inv gp2 --args="validate"``

7. Run the Green Paths 2.0 CLI commands:

        ``inv gp2 --args="all"``

8. See the results in the output folder.

        green_paths_2/src/cache/final_exposure_results

9. Travel safe and healthy!


Data requirements
----------

Green Paths 2.0 supports most of the data formats of:
- raster
- vector

The data should have numerical values for the exposure calculations.

Data sources are filled in the user configurations file, and the datas need to be on the users local machine.
See the instructions on how to fill the user configurations in the user configurations section.


Green Paths 2 Framework
----------

Green Paths 2 consist of 3 different modules which can be run separately or together as pipeline. For general use, the whole (all) pipeline should be used. If running modules separately,
user should have run the required previoud modules using cache.

Green Paths 2 is heavily dependent on user configurations and data specifications. The user should have a good understanding of the data being used and configurations before using Green Paths 2.
Currently Green Paths 2 support client user interface via terminal / cmd.

See more on Green paths 2 framework and modules in the Green Paths 2 Modules and components section.



Installation:
----------

See the OS specific instructions for the installation.

Windows
----------

Prerequisites:
- Miniconda or Anaconda
- Microsoft Visual Build Tools C++ 14.0 or greater

`Install miniconda/anaconda https://docs.conda.io/en/latest/miniconda.html`
The installation has python included.
Conda should manually be added to the PATH or the conda prompt should be used, if problems with conda not found occur.

`Install Microsoft Visual Build Tools C++ 14.0 or greater https://visualstudio.microsoft.com/visual-cpp-build-tools/`
From Visual Studio Installer select the tab "Individual components" and from there select at least:
- C++ build tools (version 14.0 or greater)
- Windows 10 SDK
- C++ CMake tools for Windows

After installing the prerequisites, install Green Paths 2 to conda environment:
- Navigate to the Green Paths 2 root folder
- (optional) deactivete the conda environment if active by running:
        conda deactivate
- Run the following command in the terminal:
        install_green_paths_2.bat
- After successfull installation, activate the conda environment by running:
        conda activate green_paths_2
- Now you can start using Green Paths 2 by running the CLI commands in the terminal.


Mac / Linux
----------

Prerequisites:
- Miniconda or Anaconda

`Install miniconda/anaconda https://docs.conda.io/en/latest/miniconda.html`
The installation has python included.

After installing the prerequisites, install Green Paths 2 to conda environment:
- Navigate to the Green Paths 2 root folder
- (optional) deactivete the conda environment if active by running:
        conda deactivate
- Run the following command in the terminal:
        ./install_green_paths_2.sh
- After successfull installation, activate the conda environment by running:
        conda activate green_paths_2
- Now you can start using Green Paths 2 by running the CLI commands in the terminal.


**Remember to activate the conda environment after installation!**



CLI USER INTERFACE
----------

Green Paths 2 is operated via CLI. The CLI commands are run in the terminal / cmd. Here are all the supported commands:

- validate
- describe
- clear_cache
- preprocessing
- routing
- analysing
- all


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
