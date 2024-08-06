from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
import subprocess
import os
import copy
from config import parent_folder
from picoquic.convert import convert
from picoquic.split_trace import split
from utils.kill_process import find_and_kill_process
from utils.create_toy_server import create_server
import multiprocessing, threading

def create_commands(bw_file_1, bw_file_2, lt_file_1, lt_file_2, data_size, command_type, queue_length, ref):
    # os.system("iperf -s &")
    # os.system("sleep 0.5")
    if command_type == 1:
        command1 = "mm-delay-link-rrc 10 "+ parent_folder +"AdvNet/traces/"+lt_file_1+" "+ parent_folder +"AdvNet/traces/"+bw_file_1+" "+ parent_folder +"AdvNet/traces/"+bw_file_1+" "+ parent_folder +"packet-logs/ --uplink-log="+ parent_folder +"packet-logs/uplink --downlink-log="+ parent_folder +"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)#+" sudo iperf -c 100.64.0.1 -Z " + ref + " -t " + str(tot_duration / 1000)
        command3 = parent_folder + "picoquic/client_toy 1 " + str(data_size) + " " + parent_folder + "AdvNet/a " + ref
        is_mp = False
    elif command_type == 2:
        command1 = "mm-multipath 14 "+ parent_folder +"AdvNet/traces/"+ lt_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder +"packet-logs/ "+ parent_folder +"AdvNet/traces/"+ lt_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"packet-logs-2/ --uplink-queue-1=droptail --uplink-queue-args-1=packets="+str(queue_length)+" --uplink-queue-2=droptail --uplink-queue-args-2=packets="+str(queue_length)
        command3 = parent_folder + "picoquic/client_toy_mp 1 " + str(data_size) + " " + parent_folder + "AdvNet/a " + ref
        is_mp = True
    command2 = "sleep 2"

    commands = f"""
            {command1}
            {command2}
            {command3}
        """
    stop_event = threading.Event()
    os.system("sleep 2")
    server_process = threading.Thread(target=create_server, args=(is_mp,stop_event))
    server_process.start()
    # os.system("sleep 0.1")
    return commands, stop_event

def measure_time(bw_file_1, bw_file_2, lt_file_1, lt_file_2, data_size, queue_length, command_type, ref):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    commands,stop_event = create_commands(bw_file_1, bw_file_2, lt_file_1, lt_file_2, data_size, command_type, queue_length, ref)
    output, errors = shell.communicate(commands)
    # find_and_kill_process('toy')
    stop_event.set()
    if command_type == 2:
        return float(output.split('\n')[-8].split("=")[1].split()[0])
    elif command_type == 1:
        return float(output.split('\n')[-2].split("=")[1].split()[0])
    return 0

def evaluate(trace, exp_type, ref, tar, n_evals, log = False):
    # if len(trace) == 6: #handling single timestep
    #     trace = copy.deepcopy(trace)
    #     trace = [trace[0], trace[0], trace[1], trace[1], trace[2], trace[2], trace[3], trace[3]] + trace[4:]
    trace = convert(trace, exp_type)

    if exp_type == 1:
        bandwidths_1, bandwidths_2, latencies_1, latencies_2, durations, data, queue_length = split(trace, 1)

        bw_file_1 = create_bandwidth_trace(bandwidths_1, durations)
        bw_file_2 = create_bandwidth_trace(bandwidths_2, durations)
        lt_file_1 = create_delay_trace(latencies_1, durations)
        lt_file_2 = create_delay_trace(latencies_2, durations)

        values = []
        for _ in range(n_evals):
            values.append(measure_time(bw_file_1, bw_file_2, lt_file_1, lt_file_2, data, queue_length, 2, ref))
        exec_time_mpquic = sum(values) / n_evals
        values = []
        for _ in range(n_evals):
            values.append(measure_time(bw_file_1, bw_file_2, lt_file_1, lt_file_2, data, queue_length, 1, ref))
        exec_time_quic = sum(values) / n_evals
        if log:
            print(bandwidths_1, bandwidths_2, latencies_1, latencies_2, durations, data, queue_length, ref)
            print(exec_time_mpquic, exec_time_quic)
        return (exec_time_mpquic - exec_time_quic) / exec_time_mpquic
    elif exp_type == 2:
        bandwidths, latencies, durations, data, queue_length = split(trace, 2)

        bw_file = create_bandwidth_trace(bandwidths, durations)
        lt_file = create_delay_trace(latencies, durations)

        values = []
        for _ in range(n_evals):
            values.append(measure_time(bw_file, None, lt_file, None, data, queue_length, 1, tar))
        exec_time_tar = sum(values) / n_evals
        values = []
        for _ in range(n_evals):
            values.append(measure_time(bw_file, None, lt_file, None, data, queue_length, 1, ref))
        exec_time_ref = sum(values) / n_evals
        if log:
            print(bandwidths_1, bandwidths_2, latencies_1, latencies_2, durations, data, queue_length, ref)
            print(exec_time_mpquic, exec_time_quic)
        return (exec_time_tar - exec_time_ref) / exec_time_tar