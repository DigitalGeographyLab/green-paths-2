# QUICKSTART

```{important}
Remember to check the installation prerequisites:
- All OS: Miniconda or Anaconda
- Windows: Microsoft Visual Build Tools C++ 14.0 or greater
See instructions from the [Installation](#installation) section for more details.
```

```{hint}
For a successfull run see also [Data requirements](#data_requirements) and instructions on how to fill the [User configurations](#user_configurations)!
```

1. Clone the repository from GitHub:

        git clone https://github.com/DigitalGeographyLab/green-paths-2

2. Navigate to the Green Paths 2 root folder:

        cd green-paths-2

3. Install Green Paths 2. Remember to run the CLI as administrator. Run the installation script from the root folder:
        
        Windows:
        install_green_paths_2.bat

        Mac / Linux:
        ./install_green_paths_2.sh

```{note}
NOTE: If the installation script has errors, please check the prerequisites!
Remember to deactivate the conda environment before installing and re-activate it after installation!
and check the prerequisites for the installation from the installation section!
```

4. Activate the conda environment:
        
        conda activate green_paths_2

5. Fill in the user configurations in the **user/config.yml** file.

```{tip}
For help use the **Descriptor**, which will help to find the possible values for the user configurations.
    inv gp2 --args="describe"
```

6. Validate the user configurations before running the pipeline.

        inv gp2 --args="validate"

7. Run the Green Paths 2.0 CLI commands:

        inv gp2 --args="all"

8. See the results in the output folder.

        results_output

9. Travel safe and healthy!

