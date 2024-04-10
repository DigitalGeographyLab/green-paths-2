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
    conda env remove -n dgl_gp2
    echo "'dgl_gp2' removed."
fi

# Create the Conda environment
conda create -n dgl_gp2 python=3.11 -y

# Activate the environment
source $(conda info --base)/etc/profile.d/conda.sh
conda activate dgl_gp2

# Install Java
conda install -c conda-forge openjdk -y

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

# install poetry for the current conda environment
pip install poetry

# Use the full path to call Poetry for setup and installation
poetry --version
poetry config virtualenvs.create false
poetry install

echo ''
echo "Installation and setup are complete."
echo "Please activate the Conda environment." 
echo ''
echo "Please run: conda activate dgl_gp2"
echo ''

# END OF THE INSTALL SCRIPT