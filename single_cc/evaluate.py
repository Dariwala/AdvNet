from single_cc.split_trace import split_trace
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
import subprocess
import re
import threading
from time import sleep
import os

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
    # print("mm-delay-link-rrc 8 ~/network-traces/delay-trace ~/network-traces/bandwidth-trace ~/network-traces/bandwidth-trace ~/packet-logs/ --uplink-queue=droptail --uplink-queue-args=packets=100 iperf -c " + server_ip + " -Z " + alg + " -t " + str(duration / 1000) + " > temp")
    os.system("mm-delay-link-rrc 8 ~/AdvNet/traces/"+lt_file+" ~/AdvNet/traces/"+bw_file+" ~/AdvNet/traces/"+bw_file+" ~/packet-logs/ --uplink-queue=droptail --uplink-queue-args=packets=100 iperf -c " + server_ip + " -Z " + alg + " -t " + str(duration / 1000) + " >> temp")
    
    with open("temp") as f:
        output = f.read()
        throughput = output.split("\n")[-2].split()[-4]
        unit = output.split("\n")[-2].split()[-3]
        # print("HOHOH", output)
        if unit == "MBytes":
            return float(throughput)
        elif unit == "KBytes":
            return float(throughput) / 1024

def get_throughput(bw_file, lt_file, tot_duration, alg):
    # Run iperf client
    server_ip = '100.64.0.1'  # Change to the IP address of your server
    result = run_iperf_client(server_ip, tot_duration, alg, bw_file, lt_file)
    return result * 8000 / tot_duration
    # server_process.terminate()
    # return float(result.split("\n")[-2].split()[-4]) * 8000 / tot_duration

def evaluate(trace, ref, tar):
    bandwidths, latencies, durations = split_trace(trace)
    tot_duration = sum(durations)

    bw_file = create_bandwidth_trace(bandwidths, durations)
    lt_file = create_delay_trace(latencies, durations)
    
    throughput_ref = get_throughput(bw_file, lt_file, tot_duration, ref)
    throughput_tar = get_throughput(bw_file, lt_file, tot_duration, tar)
    print(throughput_ref - throughput_tar)

if __name__ == "__main__":
    evaluate(1000, 10, 1000)