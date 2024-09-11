# INSTRUCTIONS:

# PRE-REQUISITES:
    # 1. Install Miniconda or Anaconda

# STEPS:

# first remember to deactivate the current conda env if active by runnning the following command:
    # conda deactivate

# 1. Run the following command in the terminal to give permission to the script:
    # chmod +x install_green_paths_2.sh
# 2. Run the following command in the terminal to init the conda env:
    # ./install_green_paths_2.sh
# 3. Run the following command in the terminal to activate the conda env:
    # source activate dgl_gp2

# 4. Then start using the GreenPaths 2.0 by e.g. running the following command:
    # make greenpaths2  ARGS="all"

    # See all the available commands from documentation or by running the following command:
    # make help



# START OF THE INSTALL SCRIPT

#!/bin/bash
echo ''
echo "Installing GreenPaths 2.0"
echo ''

# Check if Conda is installed by looking for the 'conda' command
if ! conda --version &> /dev/null; then
    echo "Conda is not installed. Please install Miniconda or Anaconda before proceeding."
    echo "See: https://conda.io/projects/conda/en/latest/user-guide/install/index.html"
    echo ''
    echo "NOTE: after conda install, some of the following can be needed:"
    echo "Restaring computer, adding conda to PATH, restarting terminal/cmd/etc., ..."
    echo "If these don't work, please use the conda/anaconda prompt installed with conda."
    echo ''
    exit 1
fi

# Check if the dgl_gp2 environment is currently active
# it is is activate, echo instructions to deactivate and exit
if [[ "$CONDA_DEFAULT_ENV" == "dgl_gp2" ]]; then
    echo 'ERROR: Conda environment already active.'
    echo ''
    echo "The 'dgl_gp2' environment is currently active. Please deactivate and re-run this script."
    echo "Please run: conda deactivate'"
    echo ''
    exit 1
fi

# Check if the dgl_gp2 environment already exists
if conda info --envs | grep 'dgl_gp2' > /dev/null; then
    echo "The Conda environment 'dgl_gp2' already exists. Removing..."
    conda env remove -n dgl_gp2 -y
    echo "'dgl_gp2' removed."
fi

# Create the Conda environment
conda create -n dgl_gp2 python=3.11 -y

# Activate the environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate dgl_gp2

# Install Java
conda install -c conda-forge openjdk=21 -y

# Set JAVA_HOME for the Conda environment
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
mkdir -p $CONDA_PREFIX/etc/conda/deactivate.d

echo "#!/bin/sh" > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo "export JAVA_HOME=\$(dirname \$(dirname \$(readlink -f \$(which javac))))" >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh

echo "#!/bin/sh" > $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh
echo "unset JAVA_HOME" >> $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh

chmod +x $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
chmod +x $CONDA_PREFIX/etc/conda/deactivate.d/env_vars.sh

# Activate environment again to ensure JAVA_HOME is set
conda activate dgl_gp2

# Install Poetry
pip install poetry

# Configure Poetry to not create virtual environments
poetry config virtualenvs.create false

poetry env use $(which python)

pip install invoke

# CREATE GP2 DATABASE ***

# Create database directory if it doesn't exist
DB_DIR="green_paths_2/src/database"
DB_PATH="$DB_DIR/gp2.db"
mkdir -p $DB_DIR

# Check if the database file exists, and create it if it doesn't
if [ ! -f "$DB_PATH" ]; then
    echo "Creating SQLite database at $DB_PATH"
    sqlite3 $DB_PATH "VACUUM;"
    echo "Database created."
else
    echo "Database already exists at $DB_PATH so remove it"
    rm "$DB_PATH"

    echo "Creating SQLite database at $DB_PATH"
    sqlite3 $DB_PATH "VACUUM;"
    echo "Database created."
fi

# Create TEST database directory if it doesn't exist
DB_TEST_DIR="green_paths_2/tests/database"
DB_TEST_PATH="$DB_TEST_DIR/gp2_testing.db"
mkdir -p $DB_TEST_DIR

# Check if the database file exists, and create it if it doesn't
if [ ! -f "$DB_TEST_PATH" ]; then
    echo "Creating SQLite database at $DB_TEST_PATH"
    sqlite3 $DB_TEST_PATH "VACUUM;"
    echo "Database created."
else
    echo "Test Database already exists at $DB_TEST_PATH so remove it"
    rm "$DB_TEST_PATH"

    echo "Creating Test SQLite database at $DB_TEST_PATH"
    sqlite3 $DB_TEST_PATH "VACUUM;"
    echo "Test Database created."
fi

# Installing these straight to the conda env, removes not found proj.db error when running preprocessing module
# conda install -c conda-forge proj geos fiona
conda install -c conda-forge gdal libpq -y


echo ''
echo "Installation and setup are complete."
echo "Please activate the Conda environment." 
echo ''
echo "Please run: conda activate dgl_gp2"
echo ''

# END OF THE INSTALL SCRIPT
