#!/bin/bash
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$OSENV"

PID=$(lsof -ti:8000)
if [ -n "$PID" ]; then
    echo "Killing process on port 8000 (PID: $PID)"
    kill -9 $PID
fi


python3 dashboard/bin/dashboard.py &
python3 dashboard/bin/display.py

conda deactivate