#!/usr/bin/env python3
import argparse
import pickle
import psutil
import pandas as pd
import time

import warnings

# Silence sklearn unpickle & feature‐name warnings
warnings.filterwarnings("ignore",
    message="Trying to unpickle estimator.*version.*",
    category=UserWarning)
warnings.filterwarnings("ignore",
    message="X does not have valid feature names.*",
    category=UserWarning)

# Load your saved anomaly detector and scaler
with open("anomaly/bin/anomaly-detector.pkl", "rb") as f:
    state = pickle.load(f)
iso_forest = state["model"]
scaler     = state["scaler"]

# Features your model expects
perf_metrics = [
    'CPU usage [%]',
    'Memory usage [KB]',
    'Disk write throughput [KB/s]',
    'Network received throughput [KB/s]',
    'Network transmitted throughput [KB/s]'
]

def get_process_metrics():
    """Collect per-process metrics with a 1s I/O snapshot."""
    baseline, info = {}, {}
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.pid
            info[pid] = {
                'name': proc.info['name'],
                'CPU usage [%]': proc.cpu_percent(interval=None),
                'Memory usage [KB]': proc.memory_info().rss / 1024.0
            }
            io = proc.io_counters() if hasattr(proc, 'io_counters') else None
            net = proc.net_io_counters() if hasattr(proc, 'net_io_counters') else None
            baseline[pid] = {
                'disk_write': io.write_bytes if io else 0,
                'net_recv':   net.bytes_recv  if net else 0,
                'net_sent':   net.bytes_sent  if net else 0
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    time.sleep(1.0)

    for proc in psutil.process_iter(['pid']):
        pid = proc.pid
        if pid not in info:
            continue
        try:
            io = proc.io_counters() if hasattr(proc, 'io_counters') else None
            net = proc.net_io_counters() if hasattr(proc, 'net_io_counters') else None
            curr = {
                'disk_write': io.write_bytes if io else 0,
                'net_recv':   net.bytes_recv  if net else 0,
                'net_sent':   net.bytes_sent  if net else 0
            }
            base = baseline.get(pid, {'disk_write':0,'net_recv':0,'net_sent':0})
            info[pid].update({
                'Disk write throughput [KB/s]':      (curr['disk_write'] - base['disk_write']) / 1024.0,
                'Network received throughput [KB/s]': (curr['net_recv']   - base['net_recv'])   / 1024.0,
                'Network transmitted throughput [KB/s]': (curr['net_sent'] - base['net_sent']) / 1024.0
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            info.pop(pid, None)

    df = pd.DataFrame.from_dict(info, orient='index')
    return df.dropna(subset=perf_metrics)

def detect(df):
    """Annotate df with anomaly flag & score."""
    X = scaler.transform(df[perf_metrics].values)
    labels = iso_forest.predict(X)          # -1 anomaly, 1 normal
    scores = iso_forest.decision_function(X)
    df['is_anomaly']    = (labels == -1)
    df['anomaly_score'] = scores
    return df

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c","--continuous", action="store_true",
                        help="Run continuously and only print on anomalies")
    parser.add_argument("-i","--interval", type=float, default=5.0,
                        help="Seconds between checks (continuous mode)")
    parser.add_argument("-n","--top", type=int, default=5,
                        help="Max anomalies to show when printing")
    args = parser.parse_args()

    if args.continuous:
        print(f"Monitoring for anomalies every {args.interval}s. Ctrl-C to stop.")
        try:
            while True:
                df = get_process_metrics()
                df = detect(df)
                anoms = df[df['is_anomaly']]
                if not anoms.empty:
                    # sort by score ascending (most anomalous first)
                    anoms = anoms.nsmallest(args.top, 'anomaly_score')
                    print(f"\n[{time.strftime('%H:%M:%S')}] Detected {len(anoms)} anomalous process(es):")
                    print(anoms[['name','anomaly_score']])
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\nStopped.")
    else:
        df = get_process_metrics()
        df = detect(df)
        df_sorted = df.sort_values(['is_anomaly','anomaly_score'],
                                   ascending=[False, True])
        print(df_sorted[['name', *perf_metrics, 'is_anomaly','anomaly_score']])

if __name__ == "__main__":
    main()
