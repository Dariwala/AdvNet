import argparse
from single_cc.evaluate import evaluate
from mptcp.evaluate import evaluate as evaluate_mptcp
from picoquic.evaluate import evaluate as evaluate_picoquic
from dchannel.evaluate import evaluate as evaluate_dchannel
import os
from config import parent_folder

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to evaluate')
    parser.add_argument('--trace_file', type=str, default="trace file")
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--tar', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--mptcp_type', type=int)
    parser.add_argument('--n_evals_each_trace', type=int)
    parser.add_argument('--threshold', type=float)
    parser.add_argument('--mptcp', action='store_true', help='Whether it is mptcp or not')
    parser.add_argument('--picoquic', action='store_true', help='Whether it is picoquic or not')
    parser.add_argument('--single_cc', action='store_true', help='Whether it is single_cc or not')
    parser.add_argument('--dchannel', action='store_true', help='Whether it is dchannel or not')
    args = parser.parse_args()
    
    effective_traces_count = 0
    logs = []
    if args.single_cc:
        os.system("iperf -s &")
        with open(args.trace_file) as f:
            lines = f.readlines()

            for line in lines:
                trace = [int(t) for t in line[1:-2].split(',')]
                count = 0
                for _ in range(args.n_evals_each_trace):
                    score = evaluate(trace, args.ref, 1)
                    if score > args.threshold:
                        count += 1
                if count / args.n_evals_each_trace >= 0.8:
                    effective_traces_count += 1
                logs.append(count / args.n_evals_each_trace)
                # break
            # print(score[0][0], score[0][1], file = f)
            # os.system("sleep 0.5")
        os.system("pkill -9 iperf")
    elif args.mptcp:
        os.system("iperf -s &")
        with open(args.trace_file) as f:
            lines = f.readlines()

            for line in lines:
                # line = ''.join(line.split()[:-1])
                trace = [int(t) for t in line[1:-2].split(',')]
                count = 0
                for _ in range(args.n_evals_each_trace):
                    score = evaluate_mptcp(trace, args.ref, 1, args.mptcp_type, "5", args.tar)
                    if score > args.threshold:
                        count += 1
                if count / args.n_evals_each_trace >= 0.8:
                    effective_traces_count += 1
                logs.append(count / args.n_evals_each_trace)
                # break
            # print(score[0][0], score[0][1], file = f)
            # os.system("sleep 0.5")
        os.system("pkill -9 iperf")
    elif args.dchannel:
        with open(args.trace_file) as f:
            lines = f.readlines()

            for line in lines:
                trace = [int(t) for t in line[1:-2].split(',')]
                count = 0
                for _ in range(args.n_evals_each_trace):
                    score = evaluate_dchannel(trace, 1)
                    if score > args.threshold:
                        count += 1
                if count / args.n_evals_each_trace >= 0.8:
                    effective_traces_count += 1
                logs.append(count / args.n_evals_each_trace)
                # break
            # print(score[0][0], score[0][1], file = f)
            # os.system("sleep 0.5")
    elif args.picoquic:
        if args.mptcp_type == 1:
            score = evaluate_picoquic(args.trace, args.mptcp_type, args.ref, args.tar, 1, True)
            bandwidths_1 = get_continuous_throughput(parent_folder + "packet-logs/queue-service-log-downlink", get_start_time("queue-service-log-downlink", "queue-service-log-downlink"))
            bandwidths_2 = get_continuous_throughput(parent_folder + "packet-logs-2/queue-service-log-downlink", get_start_time("queue-service-log-downlink", "queue-service-log-downlink"))
            bandwidths_sptcp = get_continuous_throughput(parent_folder + "packet-logs/downlink")
            x = []
            y1 = []
            y2 = []
            ys_1 = []

            for time, bandwidth, throughput in bandwidths_1:
                x.append(time)
                y1.append(bandwidth)
                y2.append(throughput)
            ys_1 = [y1, y2]
            print(x)
            print(ys_1)

            x = []
            y1 = []
            y2 = []
            ys_2 = []

            for time, bandwidth, throughput in bandwidths_2:
                x.append(time)
                y1.append(bandwidth)
                y2.append(throughput)
            ys_2 = [y1, y2]
            print(x)
            print(ys_2)

            x = []
            y1 = []
            y2 = []
            ys_sp = []

            for time, bandwidth, throughput in bandwidths_sptcp:
                x.append(time)
                y1.append(bandwidth)
                y2.append(throughput)
            ys_sp = [y1, y2]
            print(x)
            print(ys_sp)
        if args.mptcp_type == 2:
            score = evaluate_picoquic(args.trace, args.mptcp_type, args.ref, args.tar, 1, True)
            bandwidths_ref = get_continuous_throughput(parent_folder + "packet-logs/temp")#, get_start_time("queue-service-log-uplink", "queue-service-log-uplink"))
            bandwidths_tar = get_continuous_throughput(parent_folder + "packet-logs/downlink")#, get_start_time("queue-service-log-uplink", "queue-service-log-uplink"))

            x = []
            y1 = []
            y2 = []
            ys_1 = []

            for time, bandwidth, throughput in bandwidths_ref:
                x.append(time)
                y1.append(bandwidth)
                y2.append(throughput)
            ys_1 = [y1, y2]
            print(x)
            print(ys_1)

            x = []
            y1 = []
            y2 = []
            ys_2 = []

            for time, bandwidth, throughput in bandwidths_tar:
                x.append(time)
                y1.append(bandwidth)
                y2.append(throughput)
            ys_2 = [y1, y2]
            print(x)
            print(ys_2)
    print(effective_traces_count)
    for l in logs:
        print(l)