import argparse
from single_cc.evaluate import evaluate
from random_generator.random_generator import RandomGeneration
import os, subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int, default=0, help="0 for single_cc")
    parser.add_argument('--alg', type=int, default=0, help="0 for random generation")
    parser.add_argument('--trace_length', type=int, default=3)
    parser.add_argument('--seed', type=int, default=10)
    parser.add_argument('--l_bounds', nargs='+', type=int, default=[1000,5,1000], help='Lower bounds')
    parser.add_argument('--u_bounds', nargs='+', type=int, default=[4000,20,3000], help='Upper bounds')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--tar', type=str, default="reno", help='Target algorithm')
    parser.add_argument('--n_eval', type=int, default=1, help='How many times to evaluate per trace')
    args = parser.parse_args()

    if args.type == 0:
        # server_process = subprocess.Popen(['iperf', '-s'], stdout=subprocess.PIPE, text=True)
        os.system("iperf -s &")
        if args.alg == 0:
            RandomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed)
            for _ in range(1):
                trace = RandomGenerator.generate_trace()
                score = evaluate(trace, args.ref, args.n_eval)                    
                print(trace, score)
                
        os.system("rm traces/*")
        # os.system("rm temp")
        os.system("pkill -9 iperf")