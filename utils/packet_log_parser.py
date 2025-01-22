from config import parent_folder
import numpy as np

def compute_convergence(times, bytes, delays):
    last_time = times[-1]
    throughputs = []
    chunk_no = 1
    chunk_interval = 2000
    chunks_to_consider = 5
    index = len(times)
    end_time = times[-1]
    tot_bytes = 0
    tot_delay = 0
    avg_delays = []
    count = 0

    while index >= 0 and len(throughputs) < chunks_to_consider:
        index -= 1
        curr_time = times[index]
        curr_byte = bytes[index]
        curr_delay = delays[index]
        if curr_time >= end_time - chunk_no * chunk_interval:
            tot_bytes += curr_byte
            count += 1
            tot_delay += curr_delay
        else:
            throughputs.append(tot_bytes)# * 8 * 1000/ (chunk_interval * 1024 * 1024))
            if count != 0:
                avg_delays.append(tot_delay / count)
            else:
                avg_delays.append(0)
            tot_delay = 0
            tot_bytes = 0
            chunk_no += 1
            count = 0
    if tot_bytes != 0:
        throughputs.append(tot_bytes * 8 * 1000/ (chunk_interval * 1024 * 1024))
        avg_delays.append(tot_delay / count)
    # for i in range(chunks_to_consider):
    #     print(throughputs[i], avg_delays[i])
    return np.sum(throughputs), np.std(avg_delays) / np.mean(avg_delays)

def parse(ref_port, tar_port):
    ref_packet_sizes_in_bytes = []
    ref_times = []
    ref_packet_delays = []
    tar_packet_sizes_in_bytes = []
    tar_times = []
    tar_packet_delays = []
    with open(parent_folder + "packet-logs/packet-log-output-uplink") as f:
        lines = f.readlines()[:-1]
        for line in lines:
            line = line.split('\t')
            # if ':' in line[2]:
                # port = int(line[2].split(':')[-1])
            port = int(line[-2])
            if port == ref_port:
                ref_packet_sizes_in_bytes.append(int(line[4]))
                ref_times.append(int(line[1]))
                ref_packet_delays.append(int(line[0]))
            if port == tar_port:
                tar_packet_sizes_in_bytes.append(int(line[4]))
                tar_times.append(int(line[1]))
                tar_packet_delays.append(int(line[0]))
    # print("Reference")
    ref_bytes, ref_delay_cv = compute_convergence(ref_times, ref_packet_sizes_in_bytes, ref_packet_delays)
    # print("Target")
    tar_bytes, tar_delay_cv = compute_convergence(tar_times, tar_packet_sizes_in_bytes, tar_packet_delays)

    print("CV of delay:", ref_delay_cv, tar_delay_cv)
    if (ref_delay_cv > 0.1 or tar_delay_cv > 0.1) and False:
        return 0, 0
    else:
        return ref_bytes, tar_bytes

def parse_mptcp(ref_port, tar_port):
    ref_packet_sizes_in_bytes = []
    tar_packet_sizes_in_bytes = []
    with open(parent_folder + "packet-logs/packet-log-uplink") as f:
        lines = f.readlines()[1:-1]
        for line in lines:
            line = line.split('\t')
            if ':' in line[2]:
                port = int(line[2].split(':')[-1])
                if port == ref_port:
                    ref_packet_sizes_in_bytes.append(int(line[5]))
                if port == tar_port:
                    tar_packet_sizes_in_bytes.append(int(line[5]))
    with open(parent_folder + "packet-logs-2/packet-log-uplink") as f:
        lines = f.readlines()[1:-1]
        for line in lines:
            line = line.split('\t')
            if ':' in line[2]:
                port = int(line[2].split(':')[-1])
                if port == ref_port:
                    ref_packet_sizes_in_bytes.append(int(line[5]))
                if port == tar_port:
                    tar_packet_sizes_in_bytes.append(int(line[5]))
    return sum(ref_packet_sizes_in_bytes), sum(tar_packet_sizes_in_bytes)