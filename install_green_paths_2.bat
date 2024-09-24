:: INSTRUCTIONS:

:: PRE-REQUISITES:
    :: 1. Install Miniconda or Anaconda

:: WINDOWS
    :: Some of GP2 dependecy packages require Microsoft Visual C++ 14.0 or greater.
    :: Download and install Microsoft Visual C++ Build Tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/
    :: From Visual Studio Installer select the tab "Individual components" and from there select at least:
    ::  - C++ build tools 
    ::  - Windows 10 SDK
    :: - C++ CMake tools for Windows

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

    echo ''
    echo NOTE: after conda install, some of the following can be needed:
    echo Restaring computer, adding conda to PATH, restarting terminal/cmd/etc., ...
    echo If these don't work, please use the conda/anaconda prompt installed with conda.
    echo ''

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
    call conda env remove -n dgl_gp2 -y
    echo 'dgl_gp2' removed.
)

:: Create the Conda environment
call conda create -n dgl_gp2 python=3.11 -y

:: Activate the environment
call conda activate dgl_gp2

call conda install sqlite libsqlite -y

:: Install Java
call conda install -c conda-forge openjdk=21 -y

:: Create Conda's activate.d folder if it doesn't exist
if not exist "%CONDA_PREFIX%\etc\conda\activate.d" (
    mkdir "%CONDA_PREFIX%\etc\conda\activate.d"
)

:: Create a batch script to set JAVA_HOME in activate.d
@REM echo @echo off > "%CONDA_PREFIX%\etc\conda\activate.d\set_java_home.bat"
@REM echo for /f "tokens=*" %%%%i in ^('where javac'^) do set JAVA_HOME=%%%%~dpi.. >> "%CONDA_PREFIX%\etc\conda\activate.d\set_java_home.bat"
@REM echo echo Setting JAVA_HOME to %%JAVA_HOME%% >> "%CONDA_PREFIX%\etc\conda\activate.d\set_java_home.bat"
@REM echo set PATH=%%JAVA_HOME%%\bin;%%PATH%% >> "%CONDA_PREFIX%\etc\conda\activate.d\set_java_home.bat"

@REM :: Inform user the script has been created
@REM echo JAVA_HOME will be set automatically every time you activate the dgl_gp2 environment.


:: Set JAVA_HOME for the Conda environment
:: Note: Setting JAVA_HOME permanently in Windows requires setting it in the system environment variables
:: This script sets it temporarily for the current session
for /f "tokens=*" %%i in ('where javac') do set JAVA_HOME=%%~dpi..
echo Setting JAVA_HOME to %JAVA_HOME%

:: Install Poetry for the current Conda environment
call pip install poetry

call poetry config virtualenvs.create false

call poetry env use $(which python)

call pip install invoke

:: Use Poetry for setup and installation
call poetry --version
call poetry config virtualenvs.create false
call poetry install

:: CREATE GP2 DATABASE

:: Create database directory if it doesn't exist
set DB_DIR=green_paths_2\src\database
set DB_PATH=%DB_DIR%\gp2.db

if not exist %DB_DIR% (
    mkdir %DB_DIR%
)

:: Check if the database file exists, and create it if it doesn't
if not exist %DB_PATH% (
    echo Creating SQLite database at %DB_PATH%
    sqlite3 %DB_PATH% "VACUUM;"
    echo Database created.
) else (
    echo Database already exists at %DB_PATH% so remove it and create a new one
    :: Remove the existing SQLite3 database file
    DEL %DB_PATH%

    echo Creating SQLite database at %DB_PATH%
    sqlite3 %DB_PATH% "VACUUM;"
    echo Database created.

)

:: CREATE GP2 TEST DATABASE

:: Create database directory if it doesn't exist
set DB_TEST_DIR=green_paths_2\tests\database
set DB_TEST_PATH=%DB_TEST_DIR%\gp2_testing.db

if not exist %DB_TEST_DIR% (
    mkdir %DB_TEST_DIR%
)

:: Check if the database file exists, and create it if it doesn't
if not exist %DB_TEST_PATH% (
    echo Creating SQLite database at %DB_TEST_PATH%
    sqlite3 %DB_TEST_PATH% "VACUUM;"
    echo Database created.
) else (
    echo Database already exists at %DB_TEST_PATH% so remove it and create a new one
    :: Remove the existing SQLite3 database file
    DEL %DB_TEST_PATH%

    echo Creating SQLite database at %DB_TEST_PATH%
    sqlite3 %DB_TEST_PATH% "VACUUM;"
    echo Database created.
)

@REM Installing these straight to the conda env, removes not found proj.db error when running preprocessing module
call conda install -c conda-forge gdal libpq -y


echo:
echo Installation and setup are complete.
echo Please activate the Conda environment.
echo:
echo Please run: conda activate dgl_gp2
echo:
