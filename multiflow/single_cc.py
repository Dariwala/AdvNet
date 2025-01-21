from multiflow.split_trace import split
from multiflow.convert import convert
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.packet_log_parser import parse
import subprocess
from config import parent_folder
import os
import numpy as np

def extract_ports_from_log(lines):
    ports = []
    for line in lines:
        if 'port' in line and '[' in line:
            port = int(line.split()[-6])
            ports.append(port)
    return ports

def run(bw_file, lt_file, queue_length, ref, tar, durations):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.system("sudo pkill -9 iperf")
    os.system("sleep 0.1")
    os.system("iperf -s &")
    os.system("sleep 0.1")
    command1 = "mm-delay-link-rrc 10 "+parent_folder +"AdvNet/traces/"+lt_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder+"packet-logs/ --uplink-log="+parent_folder+"packet-logs/uplink --downlink-log="+parent_folder+"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)
    commands = f"""
        {command1}
        sleep 0.1
        sudo iperf -c 100.64.0.1 -Z {ref} -t {str(sum(durations) / 1000)} &
        sudo iperf -c 100.64.0.1 -Z {tar} -t {str(sum(durations) / 1000)}
        exit
    """
    output, errors = shell.communicate(commands)
    ref_port, tar_port = extract_ports_from_log(output.split('\n'))

    return parse(ref_port, tar_port)

def evaluate(trace, ref, n_evals, tar, log = False):
    bandwidths, latencies, durations, queue_length = split(trace)
    bandwidths, latencies, durations, queue_length = convert(bandwidths, latencies, durations, queue_length)

    bandwidths.append(bandwidths[0])
    latencies.append(latencies[0])
    durations.append(100 * 1000)

    bw_file = create_bandwidth_trace(bandwidths, durations)
    lt_file = create_delay_trace(latencies, durations)

    scores = []
    logs = []

    for i in range(n_evals):
        if i%2 == 0:
            ref_bytes, tar_bytes = run(bw_file, lt_file, queue_length, ref, tar, durations)
        else:
            tar_bytes, ref_bytes = run(bw_file, lt_file, queue_length, tar, ref, durations)
        
        if log:
            logs.append((ref_bytes, tar_bytes, (ref_bytes - tar_bytes) / ref_bytes))
        if ref_bytes == 0:
            scores.append(-np.inf)
        else:
            scores.append((ref_bytes - tar_bytes) / ref_bytes)
    if log:
        # logs.append(np.var(scores))
        return logs
    else:
        if np.var(scores) > 0.5:
            return -np.inf
        else:
            return sum(scores) / n_evals