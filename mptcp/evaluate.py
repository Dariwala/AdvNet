from mptcp.split_trace import split_trace
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.read_uplink import read_uplink
import subprocess
from config import parent_folder

def create_commands(bw_file_1, lt_file_1, bw_file_2, lt_file_2):
    command1 = "mm-multipath 14 "+ parent_folder +"AdvNet/traces/"+ lt_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder +"packet-logs/ "+ parent_folder +"AdvNet/traces/"+ lt_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"packet-logs-2/ --uplink-queue-1=droptail --uplink-queue-args-1=packets=10 --uplink-queue-2=droptail --uplink-queue-args-2=packets=10"
    command2 = "sudo ip mptcp endpoint add 100.64.0.3 subflow 100.64.0.4"
    command3 = "mptcpize run iperf -c 100.64.0.1"

    commands = f"""
        {command1}
        {command2}
        {command3}
    """
    return commands

def run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    commands = create_commands(bw_file_1, lt_file_1, bw_file_2, lt_file_2)
    output, errors = shell.communicate(commands)

    tot_bytes_1, duration_1 = read_uplink(parent_folder + "packet-logs/queue-service-log-uplink")
    tot_bytes_2, duration_2 = read_uplink(parent_folder + "packet-logs-2/queue-service-log-uplink")

    print(tot_bytes_1, tot_bytes_2)
    print(duration_1, duration_2)
    

def evaluate(trace, n_evals, log = False):
    bandwidths_1, latencies_1, durations_1, bandwidths_2, latencies_2, durations_2 = split_trace(trace)

    bw_file_1 = create_bandwidth_trace(bandwidths_1, durations_1)
    lt_file_1 = create_delay_trace(latencies_1, durations_1)

    bw_file_2 = create_bandwidth_trace(bandwidths_2, durations_2)
    lt_file_2 = create_delay_trace(latencies_2, durations_2)

    run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2)