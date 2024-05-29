import argparse
from single_cc.evaluate import evaluate
from single_cc.problem import SingleCCProblem
from mptcp.evaluate import evaluate as evaluate_mptcp
from random_generator.random_generator import RandomGeneration
import os, subprocess
from GA.ga import AdvNetGA
# from BO.bo import AdvNetBO
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int, default=0, help="0 for single_cc, 1 for mptcp")
    parser.add_argument('--alg', type=int, default=0, help="0 for random generation, 1 for GA, 2 for BO")
    parser.add_argument('--trace_length', type=int, default=3)
    parser.add_argument('--seed', type=int, default=10)
    parser.add_argument('--l_bounds', nargs='+', type=int, default=[3], help='Lower bounds')
    parser.add_argument('--u_bounds', nargs='+', type=int, default=[12], help='Upper bounds')
    parser.add_argument('--ref', type=str, default="cubic", help='Reference algorithm')
    parser.add_argument('--tar', type=str, default="reno", help='Target algorithm')
    parser.add_argument('--n_eval', type=int, default=1, help='How many times to evaluate per trace')
    parser.add_argument('--pop_size', type=int, default=15, help='Number of individuals for GA')
    parser.add_argument('--n_iter', type=int, default=5, help='Number of iterations for GA')
    parser.add_argument('--total_time', type=float, default=5, help='Total time to run the emulation')
    parser.add_argument('--n_calls', type=int, default=50, help='Number of calls to the expensive evaluation function for BO')
    parser.add_argument('--fuzzing', action='store_true', help='Whether to enable link fuzzing of cc-fuzz or not')
    args = parser.parse_args()

    if args.type == 0: #Single CC
        # server_process = subprocess.Popen(['iperf', '-s'], stdout=subprocess.PIPE, text=True)
        #Update the bounds for link fuzzing
        if args.fuzzing:
            args.l_bounds = [args.l_bounds[0] for _ in range(args.trace_length)]
            args.u_bounds = [args.u_bounds[0] for _ in range(args.trace_length)]
        os.system("iperf -s &")
        if args.alg == 0: #Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate, args.ref, args.n_eval, args.fuzzing)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)

        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = SingleCCProblem(args.trace_length, args.l_bounds, args.u_bounds, args.ref, args.n_eval, evaluate, args.seed, args.fuzzing, start_time, args.total_time)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            print(result.F, result.X, time.perf_counter() - start_time)
            problem.save()

        # elif args.alg == 2: #BO
        #     bo = AdvNetBO(args.trace_length, args.l_bounds, args.u_bounds, evaluate, args.n_eval, args.ref, args.seed)
        #     res = bo.run(args.n_calls)         
        #     score = evaluate(res.x, args.ref, 1, True)
        #     print(score)
        os.system("pkill -9 iperf")
    
    elif args.type == 1: #mptcp
        # os.system("mptcpize run iperf -s &")
        evaluate_mptcp([1000,10,1000,1020,15,500],1)
    
    os.system("rm traces/*")