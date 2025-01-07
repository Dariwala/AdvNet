from config import parent_folder

def parse(ref_port, tar_port):
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
    return sum(ref_packet_sizes_in_bytes), sum(tar_packet_sizes_in_bytes)