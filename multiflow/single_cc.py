from multiflow.split_trace import split
from multiflow.convert import convert
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.packet_log_parser import parse
import subprocess
from config import parent_folder
import os
import numpy as np
from NoiseHandler.noisehandler import NoiseHandler

def extract_ports_from_log(lines):
    ports = []
    for line in lines:
        if 'port' in line and '[' in line:
            port = int(line.split()[-7]) #-6 in older ubuntu
            ports.append(port)
    return ports

def run(bw_file, lt_file, queue_length, ref, bg_cc, durations):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.system("sudo pkill -9 iperf")
    os.system("sleep 0.1")
    os.system("taskset -c 0 iperf -s &")
    os.system("sleep 0.1")
    command1 = "taskset -c 1 mm-delay-link-rrc 10 "+parent_folder +"AdvNet/traces/"+lt_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder+"packet-logs/ --uplink-log= --downlink-log= --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)
    commands = f"""
        {command1}
        sleep 0.1
        taskset -c 2 sudo iperf -c 100.64.0.1 -Z {bg_cc} -t {str(sum(durations) / 1000)} &
        taskset -c 3 sudo iperf -c 100.64.0.1 -Z {ref} -t {str(sum(durations) / 1000)}
        exit
    """
    output, errors = shell.communicate(commands)
    bg_port, ref_port = extract_ports_from_log(output.split('\n'))

    return parse(ref_port, bg_port)

def evaluate(trace, ref, n_evals, tar, log = False):
    bandwidths, latencies, durations, queue_length = split(trace)
    bandwidths, latencies, durations, queue_length = convert(bandwidths, latencies, durations, queue_length)

    bandwidths.append(bandwidths[0])
    latencies.append(latencies[0])
    durations.append(60 * 1000)

    bw_file = create_bandwidth_trace(bandwidths, durations)
    lt_file = create_delay_trace(latencies, durations)

    scores = []
    logs = []

    for i in range(n_evals):
        ref_bytes, bg_bytes_ref = run(bw_file, lt_file, queue_length, ref, "cubic", durations)
        tar_bytes, bg_bytes_tar = run(bw_file, lt_file, queue_length, tar, "cubic", durations)
        
        if log:
            logs.append((ref_bytes, bg_bytes_ref, tar_bytes, bg_bytes_tar, (bg_bytes_ref - bg_bytes_tar) / bg_bytes_ref))
        if ref_bytes == 0:
            scores.append(-np.inf)
        else:
            ref_score = ref_bytes / (ref_bytes + bg_bytes_ref)
            tar_score = tar_bytes / (tar_bytes + bg_bytes_tar)
            scores.append((bg_bytes_ref - bg_bytes_tar) / bg_bytes_ref)
    if log:
        # logs.append(np.var(scores))
        return logs
    else:
        noiseHandler = NoiseHandler().lcb
        score = noiseHandler(scores)
        print(score)
        return score