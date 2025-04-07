#!/usr/bin/env python3
import pickle
import psutil
import pandas as pd

import warnings

# Silence sklearn unpickle & feature‐name warnings
warnings.filterwarnings("ignore",
    message="Trying to unpickle estimator.*version.*",
    category=UserWarning)
warnings.filterwarnings("ignore",
    message="X does not have valid feature names.*",
    category=UserWarning)

perf_metrics = [
    'CPU capacity provisioned [MHZ]', 
    'Memory capacity provisioned [KB]', 
    'Memory usage [KB]', 
    'Disk write throughput [KB/s]', 
    'CPU cores'
]
with open("scheduler/bin/process-scheduler.pkl", "rb") as f:
    state = pickle.load(f)
    
scaler = state["scaler"]
model = state["model"]

def get_values():
    cpu_freq = psutil.cpu_freq()
    cpu_capacity_mhz = cpu_freq.current if cpu_freq else None
    cpu_cores = psutil.cpu_count(logical=True)
    process_metrics = {}
    initial_disk_io = {}
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.pid
            name = proc.info['name']
            mem_info = proc.memory_info()
            memory_usage_kb = mem_info.rss 
            memory_capacity_kb = mem_info.vms / 1024  
            io_counters = proc.io_counters() if hasattr(proc, 'io_counters') else None
            write_bytes = io_counters.write_bytes if io_counters else None
            process_metrics[pid] = {
                'pid': pid,
                'name': name,
                'Memory usage [KB]': memory_usage_kb,
                'Memory capacity provisioned [KB]': memory_capacity_kb,
                'CPU capacity provisioned [MHZ]': cpu_capacity_mhz,
                'CPU cores': cpu_cores,
                'Disk write throughput [KB/s]': 0 
            }
            initial_disk_io[pid] = write_bytes
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    # time.sleep(1)
    for proc in psutil.process_iter(['pid']):
        pid = proc.pid
        try:
            io_counters = proc.io_counters() if hasattr(proc, 'io_counters') else None
            current_write_bytes = io_counters.write_bytes if io_counters else None
            initial_write_bytes = initial_disk_io.get(pid, None)
            
            if current_write_bytes is not None and initial_write_bytes is not None:
                delta_bytes = current_write_bytes - initial_write_bytes
                disk_write_throughput_kb_s = delta_bytes / 1024  # Convert to KB/s
            else:
                disk_write_throughput_kb_s = None
            if pid in process_metrics:
                process_metrics[pid]['Disk write throughput [KB/s]'] = disk_write_throughput_kb_s
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    metrics_df = pd.DataFrame.from_dict(process_metrics, orient='index')
    return metrics_df[
        [
            'name',
            *perf_metrics
        ]
    ]

metrics = get_values()
scaled_values = scaler.transform(metrics[perf_metrics])
pred = model.predict(scaled_values)
metrics["predicted burst time (ms)"] = metrics["CPU capacity provisioned [MHZ]"] / pred * 10
metrics.sort_values(by=["predicted burst time (ms)"], inplace=True)
print(metrics)
