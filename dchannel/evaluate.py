from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from dchannel.split_trace import split
import subprocess
import os
import copy
from config import parent_folder
from dchannel.convert import convert
from dchannel.split_trace import split
import numpy as np

def create_commands(bw_file_1, bw_file_2, lt_file, ll_latency, data_size, heuristic, queue_length):
    # os.system("iperf -s &")
    # os.system("sleep 0.5")
    if heuristic != "pkt-state-rewards":
        command1 = "mm-adv-delay-link-rrc 12 "+heuristic+" "+parent_folder+"AdvNet/traces/"+lt_file+" "+str(ll_latency)+" "+parent_folder+"packet-logs"+" "+parent_folder+"AdvNet/traces/"+bw_file_1+" "+parent_folder+"AdvNet/traces/"+bw_file_1+" "+parent_folder+"AdvNet/traces/"+bw_file_2+" "+parent_folder+"AdvNet/traces/"+bw_file_2+" --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)
    else:
        command1 = "mm-adv-delay-link-rrc 15 "+heuristic+" --enable-buffer-uplink --enable-buffer-downlink --constant-x=0.75 "+parent_folder+"AdvNet/traces/"+lt_file+" "+str(ll_latency)+" "+parent_folder+"packet-logs"+" "+parent_folder+"AdvNet/traces/"+bw_file_1+" "+parent_folder+"AdvNet/traces/"+bw_file_1+" "+parent_folder+"AdvNet/traces/"+bw_file_2+" "+parent_folder+"AdvNet/traces/"+bw_file_2+" --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)
        # print(command1)
    command2 = "sleep 1"
    command3 = "/usr/bin/time -f \"%e\" iperf -c 100.64.0.1 -n "+str(data_size)+"K"
    command4 = "exit"
    command5 = "pkill -9 iperf"

    os.system("pkill -9 iperf")
    os.system("sleep 0.1;iperf -s &")

    print(command1)
    print(command2)
    print(command3)

    commands = f"""
            {command1}
            {command2}
            {command3}
        """
    return commands

def measure_time(bw_file_1, bw_file_2, lt_file, ll_latency, data_size, queue_length, heuristic):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    commands = create_commands(bw_file_1, bw_file_2, lt_file, ll_latency, data_size, heuristic, queue_length)
    output, errors = shell.communicate(commands)
    return float(errors)

def evaluate(trace, exp_type, n_evals = 1, log = False):
    if len(trace) == 7: #handling single timestep
        trace = copy.deepcopy(trace)
        trace = [trace[0], trace[0], trace[1], trace[1], trace[2], trace[2], trace[3], trace[3]] + trace[4:]
    trace = convert(trace)
    bandwidths_1, bandwidths_2, latencies, durations, ll_latency, queue_length, data = split(trace)
    print(bandwidths_1, bandwidths_2, latencies, durations, ll_latency, queue_length, data)

    bw_file_1 = create_bandwidth_trace(bandwidths_1, durations)
    bw_file_2 = create_bandwidth_trace(bandwidths_2, durations)
    lt_file = create_delay_trace(latencies, durations)

    print(bw_file_1, bw_file_2, lt_file)

    if exp_type == 1:
        exec_time_dc = measure_time(bw_file_1, bw_file_2, lt_file, ll_latency, data, queue_length, "pkt-state-rewards")
        os.system("cp "+parent_folder+"packet-logs/packet-log-uplink "+parent_folder+"/packet-logs/tar_packet-log-uplink")
        os.system("cp "+parent_folder+"packet-logs/packet-log-output-uplink "+parent_folder+"/packet-logs/tar_packet-log-output-uplink")
        os.system("cp "+parent_folder+"packet-logs/packet-log-downlink "+parent_folder+"/packet-logs/tar_packet-log-downlink")
        os.system("cp "+parent_folder+"packet-logs/packet-log-output-downlink "+parent_folder+"/packet-logs/tar_packet-log-output-downlink")
        exec_time_hb = measure_time(bw_file_1, bw_file_2, lt_file, ll_latency, data, queue_length, "all-hb")
        if log:
            print(bandwidths_1, bandwidths_2, latencies, durations, ll_latency, queue_length, data)
            print(exec_time_dc, exec_time_hb)
        return (exec_time_dc - exec_time_hb) / exec_time_dc
    elif exp_type == 2:
        exec_time_ll = measure_time(bw_file_1, bw_file_2, lt_file, ll_latency, data, queue_length, "all-ll")
        exec_time_dc = measure_time(bw_file_1, bw_file_2, lt_file, ll_latency, data, queue_length, "pkt-state-rewards")
        if log:
            print(bandwidths_1, bandwidths_2, latencies, durations, ll_latency, queue_length, data)
            print(exec_time_dc, exec_time_ll)
        return (exec_time_dc - exec_time_ll) / exec_time_dc
    elif exp_type == 3:
        os.system("cd "+parent_folder+"mahimahi-cdn/;git checkout 0ac7309e73a16d0e0316e5bc15aef57a5fccc4a9")
        old_version_execs = []
        for _ in range(n_evals):
            exec_time_dc_2 = measure_time(bw_file_1, bw_file_2, lt_file, ll_latency, data, queue_length, "pkt-state-rewards")
            old_version_execs.append(exec_time_dc_2)
        print(old_version_execs)
        exec_time_dc_2 = np.median(old_version_execs)
        os.system("cd "+parent_folder+"mahimahi-cdn/;git checkout 6f2e4158dbd99f6c2d78776c0f9ea13c189866ac")
        new_version_execs = []
        for _ in range(n_evals):
            exec_time_dc_1 = measure_time(bw_file_1, bw_file_2, lt_file, ll_latency, data, queue_length, "pkt-state-rewards")
            new_version_execs.append(exec_time_dc_1)
        print(new_version_execs)
        exec_time_dc_1 = np.median(new_version_execs)
        return (exec_time_dc_1 - exec_time_dc_2) / exec_time_dc_1