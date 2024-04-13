from single_cc.split_trace import split_trace
from utils.generate_bandwidth_trace import create_trace as create_bandwidth_trace
from utils.generate_delay_trace import create_trace as create_delay_trace
import subprocess
import re
import threading

def run_iperf_server(timeout, throughputs):
    # Start iperf server and capture output
    server_process = subprocess.Popen(['iperf', '-s'], stdout=subprocess.PIPE, text=True)
    server_output, _ = server_process.communicate(timeout=timeout + 1)

    # Extract throughput from server output
    throughput_match = re.search(r'\d+\.\d+ (\w+bit/sec)', server_output)
    if throughput_match:
        # return throughput_match.group(0)
        throughputs.append(throughput_match.group(0))
    else:
        throughputs.append("Throughput not found")

def run_iperf_client(server_ip, duration):
    # Run iperf client and capture output
    result = subprocess.run(['iperf', '-c', server_ip, '-t', str(duration)], stdout=subprocess.PIPE, text=True)
    return result.stdout

def evaluate(trace):
    bandwidths, latencies, durations = split_trace(trace)
    tot_duration = sum(durations)

    bw_file = create_bandwidth_trace(bandwidths, durations)
    lt_file = create_delay_trace(latencies, durations)
    
    results = []
    server_thread = threading.Thread(target=run_iperf_server, args=(tot_duration,results))
    server_thread.start()

    # Run iperf client
    server_ip = '127.0.0.1'  # Change to the IP address of your server
    _ = run_iperf_client(server_ip, tot_duration)

    # Wait for iperf server thread to finish
    server_thread.join()

    # Get server throughput from the result list
    server_throughput = results[0] if results else "Throughput not found"

    print(server_throughput)

if __name__ == "__main__":
    evaluate(1000, 10, 1000)