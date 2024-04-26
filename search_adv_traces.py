import argparse
from single_cc.evaluate import evaluate
from single_cc.problem import SingleCCProblem
from random_generator.random_generator import RandomGeneration
import os, subprocess
from GA.ga import AdvNetGA
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int, default=0, help="0 for single_cc")
    parser.add_argument('--alg', type=int, default=0, help="0 for random generation, 1 for GA")
    parser.add_argument('--trace_length', type=int, default=3)
    parser.add_argument('--seed', type=int, default=10)
    parser.add_argument('--l_bounds', nargs='+', type=int, default=[1000,5,1000], help='Lower bounds')
    parser.add_argument('--u_bounds', nargs='+', type=int, default=[4000,20,3000], help='Upper bounds')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--tar', type=str, default="reno", help='Target algorithm')
    parser.add_argument('--n_eval', type=int, default=1, help='How many times to evaluate per trace')
    parser.add_argument('--pop_size', type=int, default=15, help='Number of individuals for GA')
    parser.add_argument('--n_iter', type=int, default=5, help='Number of iterations for GA')
    parser.add_argument('--total_time', type=float, default=5, help='Total time to run the emulation')
    args = parser.parse_args()

    if args.type == 0: #Single CC
        # server_process = subprocess.Popen(['iperf', '-s'], stdout=subprocess.PIPE, text=True)
        os.system("iperf -s &")
        if args.alg == 0: #Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate, args.ref, args.n_eval)
            # for _ in range(1):
            #     trace = randomGenerator.generate_trace()
                # trace = [3407,2565,19,11,1181,1600]
                # score = evaluate(trace, args.ref, args.n_eval, log = True)
                # score = evaluate(trace, args.ref, args.n_eval)                    
                # print(trace, score)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)
        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = SingleCCProblem(args.trace_length, args.l_bounds, args.u_bounds, args.ref, args.n_eval)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            print(result.F, result.X, time.perf_counter() - start_time)
            
        os.system("rm traces/*")
        os.system("pkill -9 iperf")