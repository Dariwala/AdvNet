from single_cc.split_trace import split_trace
from single_cc.preprocess_trace_fuzzing import preprocess_trace_fuzzing
from single_cc.convert import convert
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace, create_trace_fuzzing as create_bandwidth_trace_fuzzing
from utils.generate_delay_trace import create_trace as create_delay_trace, create_trace_fuzzing as create_delay_trace_fuzzing
import subprocess
import re
import threading
from time import sleep
import os
import numpy as np
from config import parent_folder

def read_uplink():
    with open(parent_folder + "packet-logs/uplink") as f:
        output = f.read()
        # throughput = output.split("\n")[-2].split()[-4]
        # unit = output.split("\n")[-2].split()[-3]
        # # print("HOHOH", output)
        # if unit == "MBytes":
        #     return float(throughput)
        # elif unit == "KBytes":
        #     return float(throughput) / 1024
        tot_bytes = 0
        duration = 0
        lines = output.split('\n')[4:-1]
        for line in lines:
            line = line.split()
            duration = int(line[0])
            if line[1] == '-':
                tot_bytes += int(line[2])
    return tot_bytes, duration

def read_packet_log_output_uplink():
    with open(parent_folder + "packet-logs/packet-log-output-uplink") as f:
        output = f.read()
        lines = output.split('\n')[:-1]
        tot_delay = 0.0
        count = 0
        for line in lines:
            if line != '':
                line = line.split('\t')
                tot_delay += float(line[0])
                count += 1
        return tot_delay / count

def run_iperf_client(server_ip, duration, alg, bw_file, lt_file, queue_length = 860):
    # Run iperf client and capture output
    # while True:
    #     result = subprocess.run(['iperf', '-c', server_ip, '-t', str(duration / 1000), '-Z', alg], stdout=subprocess.PIPE, text=True)
    #     if result.stdout == "":
    #         # print("Hihi")
    #         sleep(0.1)
    #         continue
    #     else:
    #         return result.stdout
    # print("mm-delay-link-rrc 8 ~/AdvNet/traces/"+lt_file+" ~/AdvNet/traces/"+bw_file+" ~/AdvNet/traces/"+bw_file+" ~/packet-logs/ --uplink-queue=droptail --uplink-queue-args=packets=100 iperf -c " + server_ip + " -Z " + alg + " -t " + str(duration / 1000) + " >> temp")
    os.system("pkill -9 iperf")
    os.system("iperf -s &")
    os.system("sleep 0.9")
    # os.system("mm-delay-link-rrc 10 "+ parent_folder +"AdvNet/traces/"+lt_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"packet-logs/ --uplink-log="+ parent_folder +"packet-logs/uplink --downlink-log="+ parent_folder +"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+ str(queue_length) +" sudo iperf -c " + server_ip + " -Z " + alg + " -t " + str(duration / 1000))
    shell = subprocess.Popen("/bin/bash", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    command1 = "mm-delay-link-rrc 10 "+ parent_folder +"AdvNet/traces/"+lt_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"AdvNet/traces/"+bw_file+" "+ parent_folder +"packet-logs/ --uplink-log="+ parent_folder +"packet-logs/uplink --downlink-log="+ parent_folder +"packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets="+ str(queue_length)
    command2 = "sudo iperf -c " + server_ip + " -Z " + alg + " -t " + str(duration / 1000)
    command3 = "sudo tcpdump -i ingress host 100.64.0.1 and port 5001 -w "+alg+".pcap &"
    # command3 = "sudo python3 tcp_seq_extractor.py &"# > " + alg + "_ebpf"
    print(command1)
    commands = f"""
            {command1}
            {'sleep 0.5'}
            {command3}
            {command2}
        """
    output, errors = shell.communicate(commands)
    print(output, errors)
    tot_bytes, duration = read_uplink()
    return tot_bytes * 8 * 1000 / (duration * 1024 * 1024), duration

def get_throughput(bw_file, lt_file, tot_duration, alg, queue_length):
    # Run iperf client
    server_ip = '100.64.0.1'  # Change to the IP address of your server
    result, duration = run_iperf_client(server_ip, tot_duration, alg, bw_file, lt_file, queue_length)
    return result, duration

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
    return tot_bytes * 8 * 1000 / (saved_actual_duration * 1024 * 1024)

def evaluate(trace, ref, n_evals, log = False, fuzzing = False):
    if not fuzzing:
        # trace = convert(trace)
        bandwidths, latencies, durations, queue_length = convert(trace)
        l = []
        if log:
            for i, _ in enumerate(latencies):
                l.append([latencies[i], durations[i]])
            print(l)
        tot_duration = sum(durations)
        
        bw_file = create_bandwidth_trace(bandwidths, durations)
        lt_file = create_delay_trace(latencies, durations)
    else:
        trace, tot_duration = preprocess_trace_fuzzing(trace)
        bw_file = create_bandwidth_trace_fuzzing(trace)
        lt_file = create_delay_trace_fuzzing()
        queue_length = 5000
    
    results = []
    logs = []

    for i in range(n_evals):
        throughput_ref, actual_duration = get_throughput(bw_file, lt_file, tot_duration, ref, queue_length)
        throughput_baseline = get_maximum_throughput(bw_file, actual_duration)
        logs.append((throughput_ref, throughput_baseline))
        results.append((throughput_baseline - throughput_ref) / throughput_baseline)
    
    if log:
        print(np.median(np.array(results)))
        return logs

    return np.median(np.array(results))#sum(results) / n_evals

if __name__ == "__main__":
    evaluate([3415.6695905,1011.86631287,18.69001926,16.15368375,1125.13704318,1472.97282379], "cubic", 3)