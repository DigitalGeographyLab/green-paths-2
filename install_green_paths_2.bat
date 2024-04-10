:: INSTRUCTIONS:

:: PRE-REQUISITES:
    :: 1. Install Miniconda or Anaconda

:: STEPS:

:: first remember to deactivate the current conda env if active by runnning the following command:
    :: conda deactivate

:: 1. Run the following command in the terminal to give permission to the script:
    :: chmod +x install_green_paths_2.sh
:: 2. Run the following command in the terminal to init the conda env:
    :: ./install_green_paths_2.sh
:: 3. Run the following command in the terminal to activate the conda env:
    :: source activate dgl_gp2

:: 4. Then start using the GreenPaths 2.0 by e.g. running the following command:
    :: make greenpaths2  ARGS="all"

    :: See all the available commands from documentation or by running the following command:
    :: make help



@echo off
echo:
echo Installing GreenPaths 2.0
echo:

:: Check if Conda is installed by attempting to run it
where conda >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Conda is not installed. Please install Miniconda or Anaconda before proceeding.
    echo See: https://conda.io/projects/conda/en/latest/user-guide/install/index.html
    exit /b 1
)

:: Check if the dgl_gp2 environment is currently active
call conda info | findstr "active env" | findstr "dgl_gp2" >nul
if not errorlevel 1 (
    echo ERROR: Conda environment already active.
    echo:
    echo The 'dgl_gp2' environment is currently active. Please deactivate and re-run this script.
    echo Please run: conda deactivate
    echo:
    exit /b 1
)

:: Check if the dgl_gp2 environment already exists
call conda env list | findstr "dgl_gp2" >nul
if not errorlevel 1 (
    echo The Conda environment 'dgl_gp2' already exists. Removing...
    call conda env remove -n dgl_gp2
    echo 'dgl_gp2' removed.
)

:: Create the Conda environment
call conda create -n dgl_gp2 python=3.11 -y

:: Activate the environment
call conda activate dgl_gp2

:: Install Java
call conda install -c conda-forge openjdk -y

:: Set JAVA_HOME for the Conda environment
:: Note: Setting JAVA_HOME permanently in Windows requires setting it in the system environment variables
:: This script sets it temporarily for the current session
for /f "tokens=*" %%i in ('where javac') do set JAVA_HOME=%%~dpi..
echo Setting JAVA_HOME to %JAVA_HOME%

:: Install Poetry for the current Conda environment
call pip install poetry

:: Use Poetry for setup and installation
call poetry --version
call poetry config virtualenvs.create false
call poetry install

echo:
echo Installation and setup are complete.
echo Please activate the Conda environment.
echo:
echo Please run: conda activate dgl_gp2
echo:
