import argparse
from single_cc.evaluate import evaluate
from mptcp.evaluate import evaluate as evaluate_mptcp
from picoquic.evaluate import evaluate as evaluate_picoquic
from multiflow.single_cc import evaluate as evaluate_multiflow_single_cc
import os
from config import parent_folder
from stable_baselines3 import PPO
from RL.single_agent_rl import RLlibEnv
from mptcp.evaluate import rl_evaluate

def get_start_time(file_1, file_2):
    with open(parent_folder + "packet-logs/"+file_1) as f:
        lines = f.read().split('\n')[4:-1]
        for line in lines:
            line = line.split()
            if (line[1] == '-' or line[1] == '+') and int(line[2]) > 500:
                candidate_1 = int(line[0])
                break
    with open(parent_folder + "packet-logs-2/"+file_2) as f:
        lines = f.read().split('\n')[4:-1]
        for line in lines:
            line = line.split()
            if (line[1] == '-' or line[1] == '+') and int(line[2]) > 500:
                candidate_2 = int(line[0])
                break
    if candidate_1 < candidate_2:
        return candidate_1
    else:
        return candidate_2

def get_continuous_throughput(file_name, start_time = 0):
    bandwidths = []
    with open(file_name) as f:
        output = f.read()
        lines = output.split('\n')[4:-1]
        end_time = 100
        tot_bytes = 0
        tot_bytes_sent = 0
        sum_tot_bytes = 0
        for line in lines:
            line = line.split()
            duration = int(line[0])
            if duration - start_time > end_time:
                bandwidths.append((end_time / 1000, tot_bytes * 80 / (1024 * 1024), tot_bytes_sent * 80 / (1024 * 1024)))
                sum_tot_bytes += tot_bytes
                tot_bytes = 0
                tot_bytes_sent = 0
                end_time += 100
            if line[1] == '#':
                tot_bytes += int(line[2])
            elif line[1] == '-':
                tot_bytes_sent += int(line[2])
    print("Tot bytes", sum_tot_bytes)
    return bandwidths

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', nargs='+', type=int, default=[4000,20,3000], help='Trace to evaluate')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--tar', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--mptcp_type', type=int)
    parser.add_argument('--n_processes', type=int)
    parser.add_argument('--model', type=str, default="", help='RL model to load')
    # parser.add_argument('--uplink_file_name', type = str, help = "Uplink file name")
    parser.add_argument('--fuzzing', action='store_true', help='Whether to enable link fuzzing of cc-fuzz or not')
    parser.add_argument('--mptcp', action='store_true', help='Whether it is mptcp or not')
    parser.add_argument('--multiprocessing', action='store_true', help='Whether it is multiprocessing or not')
    parser.add_argument('--picoquic', action='store_true', help='Whether it is picoquic or not')
    parser.add_argument('--multiflow', action='store_true', help='Whether it is multiflow or not')
    parser.add_argument('--RL', action='store_true', help='Whether it is RL or not')
    parser.add_argument('--log', action='store_true', help='Whether logging enabled or not')
    args = parser.parse_args()
    #os.system("iperf -s &")
    if not args.mptcp and not args.picoquic and not args.multiflow and not args.RL:
        with open("log", "w") as f:
            for _ in range(1):
                # score = evaluate_picoquic(args.trace, 3, args.ref, args.tar, 1, True)
                score = evaluate(args.trace, args.ref, 1, True, args.fuzzing)
                print(score)
                # print(score[0][0], score[0][1], file = f)
                # os.system("sleep 0.5")
        os.system("sudo pkill -9 iperf")

        # os.system("cp /home/shehaba2/packet-logs/uplink results/uplink_" + args.uplink_file_name)

        bandwidths = get_continuous_throughput(parent_folder + "packet-logs/uplink")

        x = []
        y1 = []
        y2 = []
        ys = []

        for time, bandwidth, throughput in bandwidths:
            x.append(time)
            y1.append(bandwidth)
            y2.append(throughput)
        ys = [y1, y2]
        print(x)
        print(ys)
    elif args.mptcp:
        if args.multiprocessing:
            import multiprocessing
            with multiprocessing.Manager() as manager:
                lock = manager.Lock()
                core_number = manager.Value('i', 0)  # 'i' for int
                res = []
                for _ in range(1):
                    param_list = [(args.trace, args.ref, 1, args.mptcp_type, "5", args.tar, False, lock, core_number) for _ in range(args.n_processes)]

                    with multiprocessing.Pool(processes=args.n_processes) as pool:
                        scores = pool.starmap(evaluate_mptcp, param_list)
                    for score in scores:
                        res.append(score)
            # for r in res:
                # print(r[0][0], r[0][1], r[0][2], r[0][3], sep="\t")
                # print(r, sep="\t")
            print(sum(res) / 10)
        else:
            scores = []
            for _ in range(1):
                score = evaluate_mptcp(args.trace, args.ref, 5, args.mptcp_type, "5", args.tar, False)
                if args.log:
                    for s in score:
                        scores.append(s)
                else:
                    print(score)
                    scores.append(score)
            if args.log:
                print("Ref")
                for s in scores:
                    print(s[0], s[2], s[4])
                print("Tar")
                for s in scores:
                    print(s[1], s[3])
            else:
                # print(sum(scores) / 5)
                print(score)
                pass
            if args.mptcp_type == 1:
                bandwidths_1 = get_continuous_throughput(parent_folder + "packet-logs/queue-service-log-uplink", get_start_time("queue-service-log-uplink", "queue-service-log-uplink"))
                bandwidths_2 = get_continuous_throughput(parent_folder + "packet-logs-2/queue-service-log-uplink", get_start_time("queue-service-log-uplink", "queue-service-log-uplink"))
                bandwidths_sptcp = get_continuous_throughput(parent_folder + "packet-logs/uplink")
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
            elif args.mptcp_type == 5:
                bandwidths_1_ref = get_continuous_throughput(parent_folder + "packet-logs/queue-service-log-uplink", get_start_time("queue-service-log-uplink", "queue-service-log-uplink"))
                bandwidths_2_ref = get_continuous_throughput(parent_folder + "packet-logs-2/queue-service-log-uplink", get_start_time("queue-service-log-uplink", "queue-service-log-uplink"))
                bandwidths_1_tar = get_continuous_throughput(parent_folder + "packet-logs/temp_1", get_start_time("temp_1", "temp_2"))
                bandwidths_2_tar = get_continuous_throughput(parent_folder + "packet-logs-2/temp_2", get_start_time("temp_1", "temp_2"))
                x = []
                y1 = []
                y2 = []
                ys_1 = []

                for time, bandwidth, throughput in bandwidths_1_ref:
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

                for time, bandwidth, throughput in bandwidths_2_ref:
                    x.append(time)
                    y1.append(bandwidth)
                    y2.append(throughput)
                ys_2 = [y1, y2]
                print(x)
                print(ys_2)

                x = []
                y1 = []
                y2 = []
                ys_1 = []

                for time, bandwidth, throughput in bandwidths_1_tar:
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

                for time, bandwidth, throughput in bandwidths_2_tar:
                    x.append(time)
                    y1.append(bandwidth)
                    y2.append(throughput)
                ys_2 = [y1, y2]
                print(x)
                print(ys_2)
            elif args.mptcp_type == 6:
                bandwidths_sptcp_ref = get_continuous_throughput(parent_folder + "packet-logs/uplink")
                bandwidths_sptcp_tar = get_continuous_throughput(parent_folder + "packet-logs/tar_uplink")
                x = []
                y1 = []
                y2 = []
                ys_1 = []

                for time, bandwidth, throughput in bandwidths_sptcp_ref:
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

                for time, bandwidth, throughput in bandwidths_sptcp_tar:
                    x.append(time)
                    y1.append(bandwidth)
                    y2.append(throughput)
                ys_2 = [y1, y2]
                print(x)
                print(ys_2)
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
    elif args.multiflow:
        logs = evaluate_multiflow_single_cc(args.trace, args.ref, 3, args.tar, True)
        print(logs)
    elif args.RL:
        vals = []
        model = PPO.load("RL/models/"+args.model)
        gym_env = RLlibEnv([1, 1, 10, 10], [1200, 50, 41, 91], 1, rl_evaluate, 1, args.ref, args.tar, 7, "5", 6, 1, 10, 0.99)
        for _ in range(5):
            obs, _ = gym_env.reset()   # get initial observation
            done = False
            # trace = []

            while not done:
                action, _states = model.predict(obs, deterministic=False)  # greedy action
                obs, reward, done, truncated, info = gym_env.step(action)
            print("Trace:", gym_env.trace)

            scores = []
            for _ in range(5):
                score = evaluate_mptcp(gym_env.trace, args.ref, 1, 7, "5", args.tar, False)
                scores.append(score)
            print(sum(scores) / 5)
            vals.append(sum(scores) / 5)
        print(vals)
        print(sum(vals) / 1)