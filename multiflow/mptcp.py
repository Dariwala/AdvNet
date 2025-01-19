from multiflow.split_trace import split_mptcp as split
from multiflow.convert import convert_mptcp as convert
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.packet_log_parser import parse_mptcp as parse
from multiflow.single_cc import extract_ports_from_log
import subprocess
import os
from config import parent_folder
import numpy as np

def run(bw_file_1, lt_file_1, bw_file_2, lt_file_2, queue_length, ref, tar, durations):
    while True:
        shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        os.system("sudo pkill -9 iperf")
        os.system("sleep 0.1")
        os.system("iperf -s &")
        os.system("sleep 0.1")
        command1 = "mm-multipath 14 "+ parent_folder +"AdvNet/traces/"+ lt_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder +"packet-logs/ "+ parent_folder +"AdvNet/traces/"+ lt_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"packet-logs-2/ --uplink-queue-1=droptail --uplink-queue-args-1=packets="+str(queue_length)+" --uplink-queue-2=droptail --uplink-queue-args-2=packets="+str(queue_length)
        commands = f"""
            {command1}
            sleep 0.5
            sudo iperf -c 100.64.0.1 -Z {ref} -t {str(sum(durations) / 1000)} &
            sudo iperf -c 100.64.0.1 -Z {tar} -t {str(sum(durations) / 1000)}
            exit
        """
        try:
            output, errors = shell.communicate(commands, timeout = 10)
            break
        except subprocess.TimeoutExpired:
            shell.kill()
            os.system("sudo pkill -9 mm")
    ref_port, tar_port = extract_ports_from_log(output.split('\n'))

    return parse(ref_port, tar_port)


def evaluate(trace, ref, n_evals, tar, log = False):
    bandwidths_1, latencies_1, bandwidths_2, latencies_2, durations, queue_length = split(trace)
    bandwidths_1, latencies_1, bandwidths_2, latencies_2, durations, queue_length = convert(bandwidths_1, latencies_1, bandwidths_2, latencies_2, durations, queue_length)

    bw_file_1 = create_bandwidth_trace(bandwidths_1, durations)
    lt_file_1 = create_delay_trace(latencies_1, durations)
    bw_file_2 = create_bandwidth_trace(bandwidths_2, durations)
    lt_file_2 = create_delay_trace(latencies_2, durations)

    scores = []
    logs = []

    for i in range(n_evals):
        if i%2 == 0:
            ref_bytes, tar_bytes = run(bw_file_1, lt_file_1, bw_file_2, lt_file_2, queue_length, ref, tar, durations)
        else:
            tar_bytes, ref_bytes = run(bw_file_1, lt_file_1, bw_file_2, lt_file_2, queue_length, tar, ref, durations)
        
        if log:
            logs.append((ref_bytes, tar_bytes, (ref_bytes - tar_bytes) / ref_bytes))
    
        scores.append((ref_bytes - tar_bytes) / ref_bytes)
    if log:
        # logs.append(np.var(scores))
        return logs
    else:
        if np.var(scores) > 0.5:
            return -np.inf
        else:
            return sum(scores) / n_evals