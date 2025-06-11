from multiflow.split_trace import split
from multiflow.convert import convert
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.packet_log_parser import parse
import subprocess
from config import parent_folder
import os
import numpy as np
import threading
from utils.create_toy_server import create_server

def extract_ports_from_log():
    with open(parent_folder+"packet-logs/packet-log-uplink") as f:
        lines = f.readlines() 
        ports = []
        for line in lines:
            line = line.split('\t')
            src_ip = line[2].split(':')[0]
            dst_ip = line[3]
            if src_ip == "100.64.0.2" and dst_ip == "100.64.0.1:12000":
                port = int(line[2].split(':')[1])
                if len(ports) == 0 or ports[0] != port:
                    ports.append(port)
                if len(ports) == 2:
                    break
    return ports

def run(bw_file, lt_file, queue_length, ref, tar, durations):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.system("sleep 1")
    command1 = "mm-delay-link-rrc 10 "+parent_folder +"AdvNet/traces/"+lt_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder+"packet-logs/ --uplink-log="+parent_folder+"packet-logs/uplink --downlink-log="+parent_folder+"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)
    command3 = "sudo tcpdump -i ingress host 100.64.0.1 and port 12000 -w "+ref+"_"+tar+".pcap &"
    commands = f"""
        {command1}
        sleep 1
        {parent_folder}picoquic/client_toy 1 999999999 {parent_folder}AdvNet/a {ref} & sleep 0.05 & {parent_folder}picoquic/client_toy 1 999999999 {parent_folder}AdvNet/b {tar}
    """
    stop_event = threading.Event()
    os.system("sleep 1")
    server_process = threading.Thread(target=create_server, args=(False,stop_event))
    server_process.start()
    os.system("sleep 1")
    try:
        output, errors = shell.communicate(commands, timeout=sum(durations) / 1000 + 1)
        print(output, errors)

    except subprocess.TimeoutExpired:
        print("ekhane")
        shell.kill()
        os.system("sudo pkill -9 mm")
        # os.system("sleep " + str(sum(durations) / 1000))
        os.system("sudo pkill -9 client_toy")

    stop_event.set()
    ref_port, tar_port = extract_ports_from_log()

    return parse(ref_port, tar_port)

def evaluate(trace, ref, n_evals, tar, log = False):
    bandwidths, latencies, durations, queue_length = split(trace)
    bandwidths, latencies, durations, queue_length = convert(bandwidths, latencies, durations, queue_length)

    bandwidths.append(bandwidths[0])
    latencies.append(latencies[0])
    durations.append(80 * 1000)

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
            logs.append((ref_bytes, tar_bytes, ref_bytes / (ref_bytes + tar_bytes)))
        if ref_bytes == 0:
            scores.append(-np.inf)
        else:
            # scores.append((ref_bytes - tar_bytes) / ref_bytes)
            scores.append(ref_bytes / (ref_bytes + tar_bytes))
    os.system("rm " + parent_folder+"AdvNet/traces/"+bw_file)
    os.system("rm " + parent_folder+"AdvNet/traces/"+lt_file)
    if log:
        # logs.append(np.var(scores))
        return logs
    else:
        if np.var(scores) > 0.05:
            return -np.inf
        else:
            return sum(scores) / n_evals