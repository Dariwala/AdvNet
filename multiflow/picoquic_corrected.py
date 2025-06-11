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

def extract_ports_from_log(expected_number_of_ports):
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
                if len(ports) == expected_number_of_ports:
                    break
    return ports

def run(bw_file, lt_file, queue_length, ref, tar, durations):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    os.system("sleep 1")
    command1 = "mm-delay-link-rrc 10 "+parent_folder +"AdvNet/traces/"+lt_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder +"AdvNet/traces/"+bw_file+" "+parent_folder+"packet-logs/ --uplink-log="+parent_folder+"packet-logs/uplink --downlink-log="+parent_folder+"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)
    # command3 = "sudo tcpdump -i ingress host 100.64.0.1 and port 12000 -w "+ref+"_"+tar+".pcap &"
    if ref is not None:
        command4 = parent_folder+"picoquic/client_toy 1 999999999 "+parent_folder+"AdvNet/a "+ref+" & sleep 0.05 & "+parent_folder+"picoquic/client_toy 1 999999999 "+parent_folder+"AdvNet/b "+tar
        expected_number_of_ports = 2
    else:
        command4 = parent_folder+"picoquic/client_toy 1 999999999 "+parent_folder+"AdvNet/a "+tar
        expected_number_of_ports = 1
    commands = f"""
        {command1}
        sleep 1
        {command4}
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
    if expected_number_of_ports == 2:
        ref_port, tar_port = extract_ports_from_log(expected_number_of_ports)
        print(ref_port, tar_port)
        return parse(ref_port, tar_port)
    else:
        tar_port, = extract_ports_from_log(expected_number_of_ports)
        print(tar_port)
        return parse(tar_port, -1)

def evaluate(trace, ref1, ref2, n_evals, tar, log = False):
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
        if True:
            ref1_bytes, tar1_bytes = run(bw_file, lt_file, queue_length, ref1, tar, durations)
            os.system("cp "+parent_folder+"packet-logs/uplink "+parent_folder+"/packet-logs/tar_uplink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-output-uplink "+parent_folder+"/packet-logs/tar_packet-log-output-uplink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-uplink "+parent_folder+"/packet-logs/tar_packet-log-uplink")
            os.system("cp "+parent_folder+"packet-logs/downlink "+parent_folder+"/packet-logs/tar_downlink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-output-downlink "+parent_folder+"/packet-logs/tar_packet-log-output-downlink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-downlink "+parent_folder+"/packet-logs/tar_packet-log-downlink")
            tar1_only_bytes, _ = run(bw_file, lt_file, queue_length, None, tar, durations)
            # os.system("cp "+parent_folder+"packet-logs/uplink "+parent_folder+"/packet-logs/only_uplink")
            # os.system("cp "+parent_folder+"packet-logs/packet-log-output-uplink "+parent_folder+"/packet-logs/only_packet-log-output-uplink")
            # os.system("cp "+parent_folder+"packet-logs/packet-log-uplink "+parent_folder+"/packet-logs/only_packet-log-uplink")
            # os.system("cp "+parent_folder+"packet-logs/downlink "+parent_folder+"/packet-logs/only_downlink")
            # os.system("cp "+parent_folder+"packet-logs/packet-log-output-downlink "+parent_folder+"/packet-logs/only_packet-log-output-downlink")
            # os.system("cp "+parent_folder+"packet-logs/packet-log-downlink "+parent_folder+"/packet-logs/only_packet-log-downlink")

            ref2_bytes, tar2_bytes = run(bw_file, lt_file, queue_length, ref2, tar, durations)
            os.system("cp "+parent_folder+"packet-logs/uplink "+parent_folder+"/packet-logs/ref_uplink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-output-uplink "+parent_folder+"/packet-logs/ref_packet-log-output-uplink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-uplink "+parent_folder+"/packet-logs/ref_packet-log-uplink")
            os.system("cp "+parent_folder+"packet-logs/downlink "+parent_folder+"/packet-logs/ref_downlink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-output-downlink "+parent_folder+"/packet-logs/ref_packet-log-output-downlink")
            os.system("cp "+parent_folder+"packet-logs/packet-log-downlink "+parent_folder+"/packet-logs/ref_packet-log-downlink")
            # tar2_only_bytes, _ = run(bw_file, lt_file, queue_length, None, tar, durations)
        else:
            tar1_bytes, ref1_bytes = run(bw_file, lt_file, queue_length, tar, ref1, durations)
            tar1_only_bytes, _ = run(bw_file, lt_file, queue_length, None, tar, durations)

            tar2_bytes, ref2_bytes = run(bw_file, lt_file, queue_length, tar, ref2, durations)
            # tar2_only_bytes, _ = run(bw_file, lt_file, queue_length, None, tar, durations)
        
        # scores.append((ref_bytes - tar_bytes) / ref_bytes)
        # ref1_score = (ref1_bytes) / (ref1_bytes + tar1_bytes) - 0.1 * (1 - tar1_only_bytes/(ref1_bytes + tar1_bytes))
        # ref2_score = (ref2_bytes) / (ref2_bytes + tar2_bytes) - 0.1 * (1 - tar1_only_bytes/(ref2_bytes + tar2_bytes))
        # score = (ref1_score - ref2_score) / ref1_score #higher score means bad, so we are searching for scenarios where ref1 is more unfair
        # score = ( - tar1_bytes + tar2_bytes) / (tar1_only_bytes - tar1_bytes)
        score = ( - tar1_bytes + tar2_bytes) / tar2_bytes
        scores.append(score)
        if True:
            # logs.append([score, ref1_bytes, ref2_bytes, tar1_bytes, tar2_bytes, tar1_only_bytes])
            logs.append([score, ref1_bytes, ref2_bytes, tar1_bytes, tar2_bytes])
    os.system("rm " + parent_folder+"AdvNet/traces/"+bw_file)
    os.system("rm " + parent_folder+"AdvNet/traces/"+lt_file)
    if log:
        # logs.append(np.var(scores))
        return logs
    else:
        print(np.var(scores))
        print(logs)
        if np.var(scores) > 0.1:
            return -100
        else:
            return sum(scores) / n_evals