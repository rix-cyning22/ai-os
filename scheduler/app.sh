#!/bin/bash

# Activate the conda environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$OSENV"

python3 scheduler/bin/schedule.py
conda deactivate