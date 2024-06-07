from mptcp.split_trace import split_trace
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.read_uplink import read_uplink
import subprocess
from config import parent_folder
import numpy as np

def create_commands(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_duration, command_type, ref, kernel):
    command1 = "mm-multipath 14 "+ parent_folder +"AdvNet/traces/"+ lt_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder +"packet-logs/ "+ parent_folder +"AdvNet/traces/"+ lt_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"packet-logs-2/ --uplink-queue-1=droptail --uplink-queue-args-1=packets=10 --uplink-queue-2=droptail --uplink-queue-args-2=packets=10"
    if kernel == "6":
        command3 = "mptcpize run iperf -c 100.64.0.1 -Z "+ ref +" -t " + str(tot_duration / 1000)
        if command_type == 1:
            command2 = "sudo ip mptcp endpoint add 100.64.0.3 subflow 100.64.0.4"
        elif command_type == 2:
            command2 = ":"

        commands = f"""
            {command1}
            {command2}
            {command3}
        """
    elif kernel == "5":
        command2 = "sleep 0.5"
        command3 = "sudo sysctl -w net.ipv4.tcp_congestion_control="+ref
        command4 = "iperf -c 100.64.0.1 -t " + str(tot_duration / 1000)

        commands = f"""
            {command1}
            {command2}
            {command3}
            {command4}
        """
    return commands

def run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_duration, command_type, ref, kernel):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    commands = create_commands(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_duration, command_type, ref, kernel)
    output, errors = shell.communicate(commands)

    tot_bytes_1, duration_1 = read_uplink(parent_folder + "packet-logs/queue-service-log-uplink")
    if command_type == 1:
        tot_bytes_2, duration_2 = read_uplink(parent_folder + "packet-logs-2/queue-service-log-uplink")
        return (tot_bytes_1 + tot_bytes_2) * 8 * 1000 / (np.max([duration_1, duration_2]) * 1024 * 1024), np.max([duration_1, duration_2])
    elif command_type == 2:
        return tot_bytes_1 * 8 * 1000 / (duration_1 * 1024 * 1024), duration_1

def get_maximum_throughput(bw_file, actual_duration):
    # tot_data = 0
    # tot_time = 0
    # for bandwidth, duration in zip(bandwidths, durations):
    #     tot_data += bandwidth * duration / 1000
    #     tot_time += duration
    
    # return tot_data / tot_time
    saved_actual_duration = actual_duration
    with open(parent_folder + "AdvNet/traces/"+bw_file) as f:
        lines = f.read().split('\n')[:-1]
        duration_reached = False
        tot_bytes = 0
        while not duration_reached:
            for line in lines:
                if float(line) <= actual_duration:
                    tot_bytes += 1500
                else:
                    duration_reached = True
                    break
            actual_duration -= float(lines[-1])
    return tot_bytes * 8 * 1000
    

def evaluate(trace, ref, n_evals, mptcp_type, kernel, log = False):
    bandwidths_1, latencies_1, durations_1, bandwidths_2, latencies_2, durations_2 = split_trace(trace)

    bw_file_1 = create_bandwidth_trace(bandwidths_1, durations_1)
    lt_file_1 = create_delay_trace(latencies_1, durations_1)

    bw_file_2 = create_bandwidth_trace(bandwidths_2, durations_2)
    lt_file_2 = create_delay_trace(latencies_2, durations_2)

    results = []
    for _ in range(n_evals):
        throughput_mptcp, duration = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, np.max([sum(durations_1), sum(durations_2)]), 1, ref, kernel)
        if mptcp_type == 2:
            throughput_baseline = (get_maximum_throughput(bw_file_1, duration) + get_maximum_throughput(bw_file_2, duration)) / (duration * 1024 * 1024)
            results.append((throughput_baseline - throughput_mptcp) / throughput_baseline)
        elif mptcp_type == 3:
            throughput_mptcp_single_link, duration = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, sum(durations_1), 2, ref, kernel)
            results.append((throughput_mptcp_single_link - throughput_mptcp) / throughput_mptcp_single_link)
    return np.median(results)
