from single_cc.split_trace import split_trace
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
import subprocess
import re
import threading
from time import sleep
import os

def read_uplink():
    with open("/home/shehaba2/packet-logs/uplink") as f:
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

def run_iperf_client(server_ip, duration, alg, bw_file, lt_file):
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
    os.system("mm-delay-link-rrc 10 ~/AdvNet/traces/"+lt_file+" ~/AdvNet/traces/"+bw_file+" ~/AdvNet/traces/"+bw_file+" ~/packet-logs/ --uplink-log=/home/shehaba2/packet-logs/uplink --downlink-log=/home/shehaba2/packet-logs/downlink --uplink-queue=droptail --uplink-queue-args=packets=10 sudo iperf -c " + server_ip + " -Z " + alg + " -t " + str(duration / 1000))
    tot_bytes, duration = read_uplink()
    return tot_bytes * 8 * 1000 / (duration * 1024 * 1024), duration

def get_throughput(bw_file, lt_file, tot_duration, alg):
    # Run iperf client
    server_ip = '100.64.0.1'  # Change to the IP address of your server
    result, duration = run_iperf_client(server_ip, tot_duration, alg, bw_file, lt_file)
    return result, duration

def get_maximum_throughput(bw_file, actual_duration):
    # tot_data = 0
    # tot_time = 0
    # for bandwidth, duration in zip(bandwidths, durations):
    #     tot_data += bandwidth * duration / 1000
    #     tot_time += duration
    
    # return tot_data / tot_time
    saved_actual_duration = actual_duration
    with open("/home/shehaba2/AdvNet/traces/"+bw_file) as f:
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

def evaluate(trace, ref, n_evals, log = False):
    bandwidths, latencies, durations = split_trace(trace)
    tot_duration = sum(durations)

    bw_file = create_bandwidth_trace(bandwidths, durations)
    lt_file = create_delay_trace(latencies, durations)
    
    results = []
    logs = []

    for i in range(n_evals):
        throughput_ref, actual_duration = get_throughput(bw_file, lt_file, tot_duration, ref)
        throughput_baseline = get_maximum_throughput(bw_file, actual_duration)
        logs.append((throughput_ref, throughput_baseline))
        results.append((throughput_baseline - throughput_ref) / throughput_baseline)
    
    if log:
        print(logs)

    return sum(results) / n_evals

if __name__ == "__main__":
    evaluate([3415.6695905,1011.86631287,18.69001926,16.15368375,1125.13704318,1472.97282379], "cubic", 3)