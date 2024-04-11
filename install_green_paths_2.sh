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
    conda env remove -n dgl_gp2
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

# # Export Poetry dependencies to requirements.txt
# poetry export -f requirements.txt --output requirements.txt --without-hashes

# # Install dependencies via Conda when possible and fallback to pip for the rest
# # Note: You might need to manually specify some dependencies here if they need to be installed via Conda for better compatibility
# pip install -r requirements.txt

echo ''
echo "Installation and setup are complete."
echo "Please activate the Conda environment." 
echo ''
echo "Please run: conda activate dgl_gp2"
echo ''

# END OF THE INSTALL SCRIPT
