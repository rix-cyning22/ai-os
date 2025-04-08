#!/bin/bash
# This script is for monitoring GPU memory usage and optimizing TensorFlow/PyTorch memory allocation

# Set threshold for GPU memory intervention as 85 percent
THRESHOLD=85

while true; do
    # Get current GPU usage percentage
    # The NVIDIA System Management Interface (nvidia-smi) is a command line utility, based on top of the NVIDIA Management Library (NVML), intended to aid in the management and monitoring of NVIDIA GPU devices.
    GPU_USAGE=$(nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits | awk '{print $1}')
    
    # Check if usage exceeds threshold
    if [ "$GPU_USAGE" -gt "$THRESHOLD" ]; then
        # Identify top GPU-consuming processes
        PROCESS_IDS=$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)
        
        for PID in $PROCESS_IDS; do
            # Check if process is TensorFlow or PyTorch
	# The ps command in Linux shows information about running processes, including their status, IDs, and resource usage.
            if ps -p $PID -o command | grep -q "python"; then
                if ps -p $PID -o command | grep -E "tensorflow|torch"; then
                    # Send SIGUSR1 to trigger memory cleanup in supported Python AI apps
                    # This would require adding a signal handler in your Python applications
                    kill -SIGUSR1 $PID
                    echo "$(date): Triggered memory optimization for AI process $PID"
                fi
            fi
        done
    fi
    
    # Sleep for 30 seconds before checking again
    sleep 30
done