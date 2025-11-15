import matplotlib.pyplot as plt
from collections import defaultdict

# Function to plot data
def plot_data_with_queue_lengths(time_series_1, values_1, label_1, 
                                 time_series_2, values_2, label_2, 
                                 time_series_3, values_3, label_3, 
                                 time_queue_ref, queue_ref, label_queue_ref,
                                 time_queue_tar, queue_tar, label_queue_tar,
                                 time_network_delay, values_network_delay, label_network_delay,
                                 time_ref_delay, values_ref_delay, label_ref_delay,
                                 time_tar_delay, values_tar_delay, label_tar_delay):
    fig, axs = plt.subplots(3, 1, figsize=(8, 8), sharex=False)

    # Plot bandwidth and throughput
    # axs[0].plot(time_series_1, values_1, label=label_1, color="#4285f4", linewidth=2)
    # axs[0].fill_between(time_series_1, values_1, color="#4285f4", alpha=0.3)
    axs[0].plot(time_series_2, values_2, label=label_2, color="#34a853", linewidth=2)
    axs[0].fill_between(time_series_2, values_2, color="#34a853", alpha=0.3)
    axs[0].plot(time_series_3, values_3, label=label_3, color="#ea4335", linewidth=2)
    axs[0].fill_between(time_series_3, values_3, color="#ea4335", alpha=0.3)
    axs[0].set_title("Bandwidth and Throughput Over Time", fontsize=14)
    axs[1].set_xlabel("Time (seconds)", fontsize=12)
    axs[0].set_ylabel("Value (Mbps)", fontsize=12)
    axs[0].grid(True, linestyle='--', alpha=0.7)
    axs[0].legend(fontsize=10)

    # Plot queue lengths
    axs[1].plot(time_queue_ref, queue_ref, label=label_queue_ref, color="#34a853", linewidth=2)
    axs[1].plot(time_queue_tar, queue_tar, label=label_queue_tar, color="#ea4335", linewidth=2)
    axs[1].set_title("Queue Lengths Over Time", fontsize=14)
    axs[1].set_xlabel("Time (seconds)", fontsize=12)
    axs[1].set_ylabel("Queue Length (packets)", fontsize=12)
    axs[1].grid(True, linestyle='--', alpha=0.7)
    axs[1].legend(fontsize=10)

    # Plot delays
    # axs[2].plot(time_network_delay, values_network_delay, label=label_network_delay, color="#4285f4", linewidth=2)
    axs[2].plot(time_ref_delay, values_ref_delay, label=label_ref_delay, color="#34a853", linewidth=2)
    axs[2].plot(time_tar_delay, values_tar_delay, label=label_tar_delay, color="#ea4335", linewidth=2)
    axs[2].set_title("Packet Delays Over Time", fontsize=14)
    axs[2].set_xlabel("Time (seconds)", fontsize=12)
    axs[2].set_ylabel("Delay (ms)", fontsize=12)
    axs[2].grid(True, linestyle='--', alpha=0.7)
    axs[2].legend(fontsize=10)

    # Adjust layout
    plt.tight_layout()
    plt.show()

file_prefix = "adversarial_traces/bbr_vs_hybla"
#metadata: bbr vs cubic
# avg delay: 161.52137203166228, 165.02420439264904

#meta: dctcp vs vegas
# avg delay: 149.58949032003162, 148.4213313161876

def uplink_parse():
    bandwidth_ref = {}
    bandwidth_tar = {}
    throughput_ref = {}
    throughput_tar = {}
    with open(file_prefix+"_ref_uplink") as f:
        lines = f.readlines()
        lines = lines[4:]
        for line in lines:
            line = line[:-1]
            if line != '':
                line = line.split()
                time_s = round(float(line[0]) / 1000, 1)
                time_s = (int(line[0]) // 500) * 0.5
                packet_Mb = float(line[2]) * 8 / (1024 * 1024)
                if '#' in line:
                    if time_s not in bandwidth_ref: 
                        bandwidth_ref[time_s] = 0
                    bandwidth_ref[time_s] += packet_Mb
                if '-' in line:
                    if time_s not in throughput_ref: 
                        throughput_ref[time_s] = 0
                    throughput_ref[time_s] += packet_Mb
    with open(file_prefix+"_tar_uplink") as f:
        lines = f.readlines()
        lines = lines[4:]
        for line in lines:
            line = line[:-1]
            if line != '':
                line = line.split()
                time_s = round(float(line[0]) / 1000, 1)
                time_s = (int(line[0]) // 500) * 0.5
                packet_Mb = float(line[2]) * 8 / (1024 * 1024)
                if '#' in line:
                    if time_s not in bandwidth_tar: 
                        bandwidth_tar[time_s] = 0
                    bandwidth_tar[time_s] += packet_Mb
                if '-' in line:
                    if time_s not in throughput_tar: 
                        throughput_tar[time_s] = 0
                    throughput_tar[time_s] += packet_Mb
    return bandwidth_ref, bandwidth_tar, throughput_ref, throughput_tar

def log_output_uplink_parse():
    queue_length_ref = defaultdict(int)
    count_queue_ref = {}
    delay_from_trace_ref = {}
    actual_delay_ref = {}
    throughput_ref = {}
    with open(file_prefix+"_ref_packet_log") as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-1]
            line = line.split('\t')
            time_when_packet_sent = int(line[1]) - int(line[0])
            time_when_packet_received = int(line[1])
            time_when_packet_sent_rounded = (time_when_packet_sent // 100) * 0.1
            time_when_packet_received_rounded = (time_when_packet_received // 100) * 0.1
            if time_when_packet_sent_rounded not in queue_length_ref:
                queue_length_ref[time_when_packet_sent_rounded] = 0
                count_queue_ref[time_when_packet_sent_rounded] = 0
                delay_from_trace_ref[time_when_packet_sent] = int(line[9])
            if time_when_packet_received_rounded not in queue_length_ref:
                queue_length_ref[time_when_packet_received_rounded] = 0
                count_queue_ref[time_when_packet_received_rounded] = 0
                actual_delay_ref[time_when_packet_received_rounded] = 0
            if round(time_when_packet_received / 1000, 1) not in throughput_ref:
                throughput_ref[round(time_when_packet_received / 1000, 1)] = 0
            queue_length_ref[time_when_packet_sent_rounded] += int(line[7])
            count_queue_ref[time_when_packet_sent_rounded] += 1
            queue_length_ref[time_when_packet_received_rounded] += int(line[8])
            count_queue_ref[time_when_packet_received_rounded] += 1
            actual_delay_ref[time_when_packet_received_rounded] += int(line[0])
            throughput_ref[round(time_when_packet_received / 1000, 1)] += int(line[4]) * 80 / (1024 * 1024)
    
    queue_length_tar = defaultdict(int)
    count_length_tar = {}
    delay_from_trace_tar = {}
    actual_delay_tar = {}
    throughput_tar = {}
    with open(file_prefix+"_tar_packet_log") as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-1]
            line = line.split('\t')
            time_when_packet_sent = int(line[1]) - int(line[0])
            time_when_packet_received = int(line[1])
            time_when_packet_sent_rounded = (time_when_packet_sent // 100) * 0.1
            time_when_packet_received_rounded = (time_when_packet_received // 100) * 0.1
            if time_when_packet_sent_rounded not in queue_length_tar:
                queue_length_tar[time_when_packet_sent_rounded] = 0
                count_length_tar[time_when_packet_sent_rounded] = 0
                delay_from_trace_tar[time_when_packet_sent_rounded] = int(line[9])
            if time_when_packet_received_rounded not in queue_length_tar:
                queue_length_tar[time_when_packet_received_rounded] = 0
                count_length_tar[time_when_packet_received_rounded] = 0
                actual_delay_tar[time_when_packet_received_rounded] = 0
            if round(time_when_packet_received / 1000, 1) not in throughput_tar:
                throughput_tar[round(time_when_packet_received / 1000, 1)] = 0
            queue_length_tar[time_when_packet_sent_rounded] += int(line[7])
            count_length_tar[time_when_packet_sent_rounded] += 1
            queue_length_tar[time_when_packet_received_rounded] += int(line[8])
            count_length_tar[time_when_packet_received_rounded] += 1
            actual_delay_tar[time_when_packet_received_rounded] += int(line[0])
            throughput_tar[round(time_when_packet_received / 1000, 1)] += int(line[4]) * 80 / (1024 * 1024)

    return queue_length_ref, delay_from_trace_ref, actual_delay_ref, queue_length_tar, delay_from_trace_tar, actual_delay_tar, count_queue_ref, count_length_tar

if __name__ == "__main__":
    bandwidth_ref, bandwidth_tar, throughput_ref, throughput_tar = uplink_parse()
    queue_length_ref, delay_from_trace_ref, actual_delay_ref, queue_length_tar, delay_from_trace_tar, actual_delay_tar, count_length_ref, count_length_tar = log_output_uplink_parse()

    # Prepare data for bandwidth and throughput
    time_bandwidth_ref = sorted(bandwidth_ref.keys())
    values_bandwidth_ref = [bandwidth_ref[time] for time in time_bandwidth_ref]
    time_throughput_ref = sorted(throughput_ref.keys())
    values_throughput_ref = [throughput_ref[time] for time in time_throughput_ref]
    time_bandwidth_tar = sorted(bandwidth_tar.keys())
    values_bandwidth_tar = [bandwidth_tar[time] for time in time_bandwidth_tar]
    time_throughput_tar = sorted(throughput_tar.keys())
    values_throughput_tar = [throughput_tar[time] for time in time_throughput_tar]

    # Prepare data for queue lengths
    time_queue_ref = [i for i in sorted(queue_length_ref.keys())]
    queue_ref = [queue_length_ref[time] / count_length_ref[time] for time in time_queue_ref]
    time_queue_tar = [i for i in sorted(queue_length_tar.keys())]
    queue_tar = [queue_length_tar[time] / count_length_tar[time] for time in time_queue_tar]

    print(count_length_tar)
    #Prepare data for latency
    time_actual_delay_ref = [i for i in sorted(actual_delay_ref.keys())]
    values_actual_delay_ref = [actual_delay_ref[time] / count_length_ref[time] for time in time_actual_delay_ref]
    time_actual_delay_tar = [i for i in sorted(actual_delay_tar.keys())]
    values_actual_delay_tar = [actual_delay_tar[time] / count_length_tar[time] for time in time_actual_delay_tar]
    time_delay_from_trace_ref = [i/1000 for i in sorted(delay_from_trace_ref.keys())]
    values_delay_from_trace_ref = [delay_from_trace_ref[round(time * 1000, 0)] for time in time_delay_from_trace_ref]
    time_delay_from_trace_tar = [i for i in sorted(delay_from_trace_tar.keys())]
    values_delay_from_trace_tar = [delay_from_trace_tar[time] / count_length_tar[time] for time in time_delay_from_trace_tar]

    # Call the plot function
    plot_data_with_queue_lengths(time_bandwidth_tar, values_bandwidth_tar, "Bandwidth",
                                 time_throughput_ref, values_throughput_ref, "Throughput: bbr",
                                 time_throughput_tar, values_throughput_tar, "Throughput: hybla",
                                 time_queue_ref, queue_ref, "Queue Length: bbr",
                                 time_queue_tar, queue_tar, "Queue Length: hybla",
                                 time_delay_from_trace_tar, values_delay_from_trace_tar, "Network Delay",
                                 time_actual_delay_ref, values_actual_delay_ref, "Actual Delay: bbr",
                                 time_actual_delay_tar, values_actual_delay_tar, "Actual Delay: hybla")
