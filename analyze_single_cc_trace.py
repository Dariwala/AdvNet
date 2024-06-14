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
    parser.add_argument('--fuzzing', action='store_true', help='Whether to enable link fuzzing of cc-fuzz or not')
    args = parser.parse_args()
    os.system("iperf -s &")
    with open("log", "w") as f:
        for _ in range(100):
            score = evaluate(args.trace, args.ref, 1, True, args.fuzzing)
            print(score)
            print(score[0][0], score[0][1], file = f)
    os.system("pkill -9 iperf")

    os.system("cp /home/shehaba2/packet-logs/uplink results/uplink_" + args.uplink_file_name)

    bandwidths = get_continuous_throughput("results/uplink_" + args.uplink_file_name)

    # for time, bandwidth, throughput in bandwidths:
    #     print(time, bandwidth, throughput)