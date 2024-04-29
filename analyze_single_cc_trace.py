import argparse
from single_cc.evaluate import evaluate
import os

def get_continuous_throughput(file_name):
    bandwidths = []
    with open(file_name) as f:
        output = f.read()
        lines = output.split('\n')[4:-1]
        end_time = 100
        tot_bytes = 0
        tot_bytes_sent = 0
        for line in lines:
            line = line.split()
            duration = int(line[0])
            if duration > end_time:
                bandwidths.append((end_time / 1000, tot_bytes * 80 / (1024 * 1024), tot_bytes_sent * 80 / (1024 * 1024)))
                tot_bytes = 0
                tot_bytes_sent = 0
                end_time += 100
            if line[1] == '#':
                tot_bytes += int(line[2])
            elif line[1] == '-':
                tot_bytes_sent += int(line[2])
    return bandwidths

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to evaluate')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--uplink_file_name', type = str, help = "Uplink file name")
    args = parser.parse_args()
    os.system("iperf -s &")
    score = evaluate(args.trace, args.ref, 1, True)
    print(score)
    os.system("pkill -9 iperf")

    os.system("cp /home/shehaba2//packet-logs/uplink results/uplink_" + args.uplink_file_name)

    bandwidths = get_continuous_throughput("results/uplink_" + args.uplink_file_name)

    for time, bandwidth, throughput in bandwidths:
        print(time, bandwidth, throughput)