#!/bin/bash

# Activate the conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$OSENV"

python3 anomaly/bin/anomaly.py
conda deactivate