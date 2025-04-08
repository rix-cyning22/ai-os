#!/bin/bash
# This script organizes AI models and datasets based on usage patterns

MODEL_DIR="$HOME/ai_models"
DATASET_DIR="$HOME/datasets"
LOG_FILE="$HOME/.model_usage_log"

# Create directories if they don't exist
mkdir -p "$MODEL_DIR/frequently_used"
mkdir -p "$MODEL_DIR/archived"

# Function to track model usage
track_model_usage() {
    local model_file=$1
    echo "$(date +%s) $model_file" >> "$LOG_FILE"
}

# Function to analyze model usage and reorganize
analyze_model_usage() {
    # Find models used in the last 7 days
    RECENT_MODELS=$(grep -l "$(date -d '7 days ago' +%s)" "$LOG_FILE" | sort | uniq)
    
    # Move frequently used models to quick-access directory
    for model in $RECENT_MODELS; do
        if [ -f "$MODEL_DIR/$model" ]; then
            ln -sf "$MODEL_DIR/$model" "$MODEL_DIR/frequently_used/"
            echo "Marked $model as frequently used"
        fi
    done
    
    # Archive models not used in 30 days
    find "$MODEL_DIR" -type f -name "*.h5" -o -name "*.pt" -mtime +30 \
        -not -path "$MODEL_DIR/archived/*" -exec mv {} "$MODEL_DIR/archived/" \;
}

# Add model tracking hooks to common Python shells
echo 'alias python="track_model_usage \$2; python"' >> "$HOME/.bashrc"

# Run analysis weekly through cron
(crontab -l 2>/dev/null; echo "0 0 * * 0 $HOME/scripts/analyze_model_usage.sh") | crontab -