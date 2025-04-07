#!/usr/bin/env python3
import psutil
import time
import argparse
from datetime import datetime
import GPUtil

def get_cpu_usage():
    return {
        "usage": psutil.cpu_percent(),
        "total": psutil.cpu_count(logical=True)
    }

def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        "total": mem.total,
        "used": mem.used,
        "percent": mem.percent
    }

def get_disk_usage():
    disk = psutil.disk_usage('/')
    return {
        "total": disk.total,
        "used": disk.used,
        "percent": disk.percent
    }

def get_network_usage():
    net = psutil.net_io_counters()
    return {
        "bytes_sent": net.bytes_sent,
        "bytes_received": net.bytes_recv
    }

def get_gpu_usage():
    gpus = GPUtil.getGPUs()
    if not gpus:
        return "No GPU detected"
    return "\n".join(
        [
            f"{gpu.id} ({gpu.name}):\tUsed: {gpu.memoryUsed} MB / {gpu.memoryTotal} MB (Load: {gpu.load * 100:.2f}%)"
            for gpu in gpus
        ]
    )

def monitor_resources(interval=3, log_file=None):
    print("Monitoring system resources... Press Ctrl+C to stop.")
    try:
        while True:
            print("\033[H\033[J", end="")  # Clear screen using ANSI escape sequence
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cpu = get_cpu_usage()
            memory = get_memory_usage()
            disk = get_disk_usage()
            network = get_network_usage()
            gpu = get_gpu_usage()
            
            log_entry = f"""
Timestamp:\t{timestamp}
CPU Usage:\t{cpu['usage']}% ({cpu['total']} cores)
Memory Usage:\t{memory['used'] / (1024**3):.2f} GB / {memory['total'] / (1024**3):.2f} GB ({memory['percent']}%)
Disk Usage:\t{disk['used'] / (1024**3):.2f} GB / {disk['total'] / (1024**3):.2f} GB ({disk['percent']}%)
Network:\tSent={network['bytes_sent'] / (1024**2):.2f} MB\tReceived={network['bytes_received'] / (1024**2):.2f} MB
GPU Usage:\n{gpu}
            """
            print(log_entry)
            
            if log_file:
                with open(log_file, "a") as f:
                    f.write(log_entry + "\n")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor system resources.")
    parser.add_argument("--interval", "-i", type=int, default=3, help="Monitoring interval in seconds (default: 3)")
    parser.add_argument("--log", "-lf", type=str, default=None, help="Path to log file (default: None)")
    args = parser.parse_args()
    
    monitor_resources(interval=args.interval, log_file=args.log)
