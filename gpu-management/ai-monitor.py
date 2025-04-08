#!/usr/bin/env python3
# Save as /usr/local/bin/ai-monitor.py

import os
import time
import psutil
import subprocess
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Create history database
if not os.path.exists('~/ai_usage_history.csv'):
    pd.DataFrame(columns=['timestamp', 'cpu_usage', 'memory_usage', 'gpu_usage', 
                         'disk_io', 'network_io', 'ml_framework', 'runtime']).to_csv('~/ai_usage_history.csv')

history = pd.read_csv('~/ai_usage_history.csv')
model = RandomForestRegressor()

if len(history) > 10:
    # Train prediction model on historical data
    X = history[['cpu_usage', 'memory_usage', 'gpu_usage', 'disk_io', 'network_io']]
    y = history['runtime']
    model.fit(X, y)

def detect_ml_processes():
    """Detect running ML processes and frameworks"""
    ml_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'])
            if any(x in cmdline for x in ['tensorflow', 'torch', 'keras', 'sklearn']):
                ml_framework = next((x for x in ['tensorflow', 'torch', 'keras', 'sklearn'] if x in cmdline), 'unknown')
                ml_processes.append((proc.info['pid'], ml_framework))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return ml_processes

def predict_completion_time(metrics, framework):
    """Predict completion time based on system metrics"""
    if len(history) > 10:
        prediction = model.predict([metrics])[0]
        return prediction
    return None

def adjust_process_priority(pid, predicted_time):
    """Adjust process nice value based on predicted runtime"""
    try:
        current_nice = psutil.Process(pid).nice()
        if predicted_time > 3600:  # Long-running task
            os.system(f'renice -n 10 -p {pid}')  # Lower priority for long tasks
        else:
            os.system(f'renice -n -10 -p {pid}')  # Higher priority for short tasks
    except:
        pass

# Main monitoring loop
while True:
    ml_processes = detect_ml_processes()
    
    for pid, framework in ml_processes:
        # Collect system metrics
        metrics = [
            psutil.cpu_percent(),
            psutil.virtual_memory().percent,
            float(subprocess.getoutput("nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits")),
            psutil.disk_io_counters().read_bytes + psutil.disk_io_counters().write_bytes,
            psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        ]
        
        # Predict task completion
        predicted_time = predict_completion_time(metrics, framework)
        
        if predicted_time:
            # Adjust process priority based on prediction
            adjust_process_priority(pid, predicted_time)
            
            # Log data for future learning
            new_row = pd.DataFrame({
                'timestamp': time.time(),
                'cpu_usage': metrics[0],
                'memory_usage': metrics[1],
                'gpu_usage': metrics[2],
                'disk_io': metrics[3],
                'network_io': metrics[4],
                'ml_framework': framework,
                'runtime': 0  # Will be updated when process finishes
            }, index=[0])
            
            history = pd.concat([history, new_row])
            history.to_csv('~/ai_usage_history.csv', index=False)
    
    time.sleep(60)  # Check every minute