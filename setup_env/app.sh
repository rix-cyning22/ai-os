#!/bin/bash

# Get conda path
CONDAPATH=$(which conda)

# Activate the conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$OSENV"

python3 setup_env/install_script.py
conda deactivate