from mptcp.split_trace import split_trace, split_trace_simplify
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
from utils.scale_up import scale_up
from utils.read_uplink import read_uplink, read_uplink_mp
import subprocess
from config import parent_folder
import numpy as np
import os
from single_cc.evaluate import run_iperf_client as run_iperf_client_single_cc
from mptcp.convert import convert

def create_commands(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_duration, command_type, ref, kernel, queue_length):
    if command_type == 1 or command_type == 2 or command_type == 3:
        command1 = "mm-multipath 14 "+ parent_folder +"AdvNet/traces/"+ lt_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder + "AdvNet/traces/" + bw_file_1 +" "+ parent_folder +"packet-logs/ "+ parent_folder +"AdvNet/traces/"+ lt_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"AdvNet/traces/"+ bw_file_2 +" "+ parent_folder +"packet-logs-2/ --uplink-queue-1=droptail --uplink-queue-args-1=packets="+str(queue_length)+" --uplink-queue-2=droptail --uplink-queue-args-2=packets="+str(queue_length)
    elif command_type == 4:
        command1 = "mm-delay-link-rrc 10 "+ parent_folder +"AdvNet/traces/"+lt_file_1+" "+ parent_folder +"AdvNet/traces/"+bw_file_1+" "+ parent_folder +"AdvNet/traces/"+bw_file_1+" "+ parent_folder +"packet-logs/ --uplink-log="+ parent_folder +"packet-logs/uplink --downlink-log="+ parent_folder +"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+str(queue_length)#+" sudo iperf -c 100.64.0.1 -Z " + ref + " -t " + str(tot_duration / 1000)
    if kernel == "6":
        if command_type == 1 or command_type == 2:
            command3 = "mptcpize run iperf -c 100.64.0.1 -Z "+ ref +" -t " + str(tot_duration / 1000)
        elif command_type == 3:
            command3 = "mptcpize run /usr/bin/time -f \"%e\" iperf -c 100.64.0.1 -Z "+ ref +" -n " + str(tot_duration) + "K" #tot_duration is tot_size here
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
        command2 = "sleep 1"
        command3 = "sudo sysctl -w net.ipv4.tcp_congestion_control="+ref
        if command_type == 1 or command_type == 2:
            command4 = "iperf -c 100.64.0.1 -t " + str(tot_duration / 1000)
        elif command_type == 3 or command_type == 4:
            command4 = "/usr/bin/time -f \"%e\" iperf -c 100.64.0.1 -n " + str(tot_duration) + "K" #tot_duration is tot_size here
        command5 = "pkill -9 iperf"
        command6 = "iperf -s &"
        os.system(command5)
        os.system(command6)
        commands = f"""
            {command1}
            {command2}
            {command3}
            {command4}
        """
    return commands

def run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_duration, command_type, ref, kernel, queue_length):
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    commands = create_commands(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_duration, command_type, ref, kernel, queue_length)
    output, errors = shell.communicate(commands)
    print(errors)

    if command_type == 1 or command_type == 2:
        tot_bytes_1, duration_1 = read_uplink_mp(parent_folder + "packet-logs/queue-service-log-uplink")
        if command_type == 1:
            tot_bytes_2, duration_2 = read_uplink_mp(parent_folder + "packet-logs-2/queue-service-log-uplink")
            return (tot_bytes_1 + tot_bytes_2) * 8 * 1000 / (np.max([duration_1, duration_2]) * 1024 * 1024), np.max([duration_1, duration_2])
        elif command_type == 2:#obsolete
            return tot_bytes_1 * 8 * 1000 / (duration_1 * 1024 * 1024), duration_1
    elif command_type == 3 or command_type == 4:
        return float(errors)

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
    

def evaluate(trace, ref, n_evals, mptcp_type, kernel, tar, log = False, simplify = False, index = -1):
    if not simplify:
        trace = convert(trace)
        bandwidths_1, latencies_1, durations, bandwidths_2, latencies_2, queue_length = split_trace(trace)
        durations_1 = durations
        durations_2 = durations
        if mptcp_type == 4:
            tot_size = durations[0]
            durations = [1000]
    else:
        print(trace, index)
        bandwidths_1, latencies_1, durations_1, bandwidths_2, latencies_2, durations_2, queue_length = split_trace_simplify(trace, index)

    bw_file_1 = create_bandwidth_trace(bandwidths_1, durations_1)
    lt_file_1 = create_delay_trace(latencies_1, durations_1)

    bw_file_2 = create_bandwidth_trace(bandwidths_2, durations_2)
    lt_file_2 = create_delay_trace(latencies_2, durations_2)

    results = []
    logs = []
    for _ in range(n_evals):
        if mptcp_type == 2 or mptcp_type == 3:
            throughput_mptcp, duration = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, max(sum(durations_1), sum(durations_2)), 1, ref, kernel, queue_length)
        elif mptcp_type == 4:
            finish_time_mptcp = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_size, 3, ref, kernel, queue_length)
            finish_time_single_link = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, tot_size, 4, ref, kernel, queue_length)
            results.append((finish_time_mptcp - finish_time_single_link) / finish_time_mptcp)
            logs.append([finish_time_mptcp, finish_time_single_link])
        if mptcp_type == 2:
            throughput_baseline = (get_maximum_throughput(bw_file_1, duration) + get_maximum_throughput(bw_file_2, duration)) / (duration * 1024 * 1024)
            results.append((throughput_baseline - throughput_mptcp) / throughput_baseline)
            logs.append([throughput_baseline, throughput_mptcp])
        elif mptcp_type == 3:
            throughput_mptcp_single_link, duration = run_iperf_client_single_cc("100.64.0.1", sum(durations_1), ref, bw_file_1, lt_file_1, queue_length)
            results.append((throughput_mptcp_single_link - throughput_mptcp) / throughput_mptcp_single_link)
            logs.append([throughput_mptcp_single_link, throughput_mptcp])
    if mptcp_type == 1:
        throughput_mptcp_max = -1.0
        throughput_mptcp_single_link_max = -1.0
        for _ in range(n_evals):
            throughput_mptcp, duration = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, max(sum(durations_1), sum(durations_2)), 1, ref, kernel, queue_length)
            if throughput_mptcp > throughput_mptcp_max:
                throughput_mptcp_max = throughput_mptcp
        os.system("sleep 1")
        for _ in range(n_evals):
            throughput_mptcp_single_link, duration = run_iperf_client_single_cc("100.64.0.1", sum(durations_1), ref, bw_file_1, lt_file_1, queue_length)
            if throughput_mptcp_single_link > throughput_mptcp_single_link_max:
                throughput_mptcp_single_link_max = throughput_mptcp_single_link
        logs.append([throughput_mptcp_single_link_max, throughput_mptcp_max])
    elif mptcp_type == 5:
        throughput_mptcp_ref_max = -1.0
        throughput_mptcp_tar_max = -1.0

        for _ in range(n_evals):
            throughput_mptcp_tar, duration = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, max(sum(durations_1), sum(durations_2)), 1, tar, kernel, queue_length)
            if throughput_mptcp_tar > throughput_mptcp_tar_max:
                throughput_mptcp_tar_max = throughput_mptcp_tar
        os.system("sleep 1;cp "+parent_folder+"packet-logs/queue-service-log-uplink "+parent_folder+"/packet-logs/temp_1")
        os.system("cp "+parent_folder+"packet-logs-2/queue-service-log-uplink "+parent_folder+"/packet-logs-2/temp_2")
        for _ in range(n_evals):
            throughput_mptcp_ref, duration = run_iperf3_client(bw_file_1, lt_file_1, bw_file_2, lt_file_2, max(sum(durations_1), sum(durations_2)), 1, ref, kernel, queue_length)
            if throughput_mptcp_ref > throughput_mptcp_ref_max:
                throughput_mptcp_ref_max = throughput_mptcp_ref
        logs.append([throughput_mptcp_ref_max, throughput_mptcp_tar_max])
    elif mptcp_type == 6:
        throughput_sptcp_ref_max = -1.0
        throughput_sptcp_tar_max = -1.0

        for _ in range(n_evals):
            throughput_sptcp_tar, duration = run_iperf_client_single_cc("100.64.0.1", sum(durations_1), tar, bw_file_1, lt_file_1, queue_length)
            if throughput_sptcp_tar > throughput_sptcp_tar_max:
                throughput_sptcp_tar_max = throughput_sptcp_tar
        os.system("sleep 1;cp "+parent_folder+"packet-logs/uplink "+parent_folder+"/packet-logs/temp_1")
        for _ in range(n_evals):
            throughput_sptcp_ref, duration = run_iperf_client_single_cc("100.64.0.1", sum(durations_1), ref, bw_file_1, lt_file_1, queue_length)
            if throughput_sptcp_ref > throughput_sptcp_ref_max:
                throughput_sptcp_ref_max = throughput_sptcp_ref
        logs.append([throughput_sptcp_ref_max, throughput_sptcp_tar_max])
    if log:
        return logs
    elif mptcp_type == 1:
        return (throughput_mptcp_single_link_max - throughput_mptcp_max) / throughput_mptcp_single_link_max
    elif mptcp_type == 5:
        return (throughput_mptcp_ref_max - throughput_mptcp_tar_max) / throughput_mptcp_ref_max
    elif mptcp_type == 6:
        return (throughput_sptcp_ref_max - throughput_sptcp_tar_max) / throughput_sptcp_ref_max
    else:
        # print("HHH", throughput_mptcp_single_link_max, throughput_mptcp_max)
        return np.median(results)