#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import psutil
import GPUtil
from datetime import datetime
import csv
import matplotlib.pyplot as plt
import io
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store resource history
resource_history = []

def get_gpu_usage():
    gpus = GPUtil.getGPUs()
    return [
        {
            "id": gpu.id,
            "name": gpu.name,
            "memoryUsed": gpu.memoryUsed,
            "memoryTotal": gpu.memoryTotal,
            "load": gpu.load * 100,  # This will be the GPU usage percentage
        } for gpu in gpus
    ] if gpus else []

@app.get("/api/resources")
def get_resources():
    # Collect resource data
    cpu_usage = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    network = psutil.net_io_counters()

    gpu_data = get_gpu_usage()

    resource_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": {
            "usage": cpu_usage,
            "cores": psutil.cpu_count(logical=True)
        },
        "memory": {
            "used": memory.used,
            "total": memory.total,
            "percent": memory.percent
        },
        "disk": {
            "used": disk.used,
            "total": disk.total,
            "percent": disk.percent
        },
        "network": {
            "sent": network.bytes_sent,
            "recv": network.bytes_recv
        },
        "gpu": gpu_data
    }

    # Store the resource data in history
    resource_history.append(resource_data)
    return resource_data

@app.get("/download_log")
def download_log():
    # Create a CSV log from the resource history
    log_filename = "resource_log.csv"
    if not resource_history:
        return {"error": "No data to log."}
    
    fieldnames = ['timestamp', 'cpu_usage', 'memory_used', 'memory_total', 'memory_percent', 'disk_used', 'disk_total', 'disk_percent', 'network_sent', 'network_recv', 'gpu']

    with open(log_filename, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for entry in resource_history:
            gpu_names = ", ".join([gpu['name'] for gpu in entry['gpu']]) if entry['gpu'] else "No GPU"
            writer.writerow({
                'timestamp': entry['timestamp'],
                'cpu_usage': entry['cpu']['usage'],
                'memory_used': entry['memory']['used'],
                'memory_total': entry['memory']['total'],
                'memory_percent': entry['memory']['percent'],
                'disk_used': entry['disk']['used'],
                'disk_total': entry['disk']['total'],
                'disk_percent': entry['disk']['percent'],
                'network_sent': entry['network']['sent'],
                'network_recv': entry['network']['recv'],
                'gpu': gpu_names
            })
    
    return FileResponse(log_filename, media_type='text/csv', filename=log_filename)

@app.get("/plot_graph")
def plot_graph():
    # Plot resource usage over time
    if not resource_history:
        return {"error": "No data to plot."}

    # Extract data
    timestamps = [entry['timestamp'] for entry in resource_history]
    timestamps = [datetime.strptime(ts, "%Y-%m-%d %H:%M:%S") for ts in timestamps]
    cpu_usage = [entry['cpu']['usage'] for entry in resource_history]
    memory_percent = [entry['memory']['percent'] for entry in resource_history]
    disk_percent = [entry['disk']['percent'] for entry in resource_history]
    
    # Assuming GPU data is available in each resource entry
    gpus = [entry['gpu'] for entry in resource_history]  # List of GPU data for each entry
    
    # Create a 2x2 subplot grid (2 rows, 2 columns)
    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.tight_layout(pad=5.0)  # Add padding between subplots

    # Plot CPU usage in the first subplot (top-left)
    axs[0, 0].plot(timestamps, cpu_usage, label="CPU Usage (%)", color='red', marker='o')
    axs[0, 0].set_title("CPU Usage Over Time")
    axs[0, 0].set_xlabel("Timestamp")
    axs[0, 0].set_ylabel("Usage (%)")
    axs[0, 0].set_xticklabels([ts.strftime("%H:%M:%S") for ts in timestamps], rotation=45, ha='right')
    axs[0, 0].legend()
    axs[0, 0].set_ylim(0, 100)

    # Plot Memory usage in the second subplot (top-right)
    axs[0, 1].plot(timestamps, memory_percent, label="Memory Usage (%)", color='blue', marker='o')
    axs[0, 1].set_title("Memory Usage Over Time")
    axs[0, 1].set_xlabel("Timestamp")
    axs[0, 1].set_ylabel("Usage (%)")
    axs[0, 1].set_xticklabels([ts.strftime("%H:%M:%S") for ts in timestamps], rotation=45, ha='right')
    axs[0, 1].legend()
    axs[0, 1].set_ylim(0, 100)

    # Plot Disk usage in the third subplot (bottom-left)
    axs[1, 0].plot(timestamps, disk_percent, label="Disk Usage (%)", color='green', marker='o')
    axs[1, 0].set_title("Disk Usage Over Time")
    axs[1, 0].set_xlabel("Timestamp")
    axs[1, 0].set_ylabel("Usage (%)")
    axs[1, 0].set_xticklabels([ts.strftime("%H:%M:%S") for ts in timestamps], rotation=45, ha='right')
    axs[1, 0].legend()
    axs[1, 0].set_ylim(0, 100)

    # Plot GPU usage in the fourth subplot (bottom-right)
    # If there are multiple GPUs, we will plot them in the same graph
    for gpu_index in range(len(gpus[0])):  # Assuming multiple GPUs
        gpu_data = [gpu[gpu_index]['load'] for gpu in gpus]  # Extract GPU load (usage) for each GPU
        axs[1, 1].plot(timestamps, gpu_data, label=f"GPU {gpu_index+1} Usage (%)", marker='o')
    
    axs[1, 1].set_title("GPU Usage Over Time")
    axs[1, 1].set_xlabel("Timestamp")
    axs[1, 1].set_ylabel("Usage (%)")
    axs[1, 1].set_xticklabels([ts.strftime("%H:%M:%S") for ts in timestamps], rotation=45, ha='right')
    axs[1, 1].legend()
    axs[1, 1].set_ylim(0, 100)

    # Save plot to a BytesIO buffer
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # Return the plot as a StreamingResponse
    return StreamingResponse(buf, media_type="image/png")


@app.get("/", response_class=HTMLResponse)
def dashboard_ui():
    with open("dashboard/bin/index.html", "r") as f:
        return HTMLResponse(content=f.read(), status_code=200)
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info", reload=False)