import argparse
from single_cc.evaluate import evaluate
from GA.problem import CCProblem
from mptcp.evaluate import evaluate as evaluate_mptcp
from dchannel.evaluate import evaluate as evaluate_dchannel
from picoquic.evaluate import evaluate as evaluate_picoquic
from random_generator.random_generator import RandomGeneration
import os, subprocess
from GA.ga import AdvNetGA
# from BO.bo import AdvNetBO
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int, default=0, help="0 for single_cc, 1 for mptcp, 2 for dchannel")
    parser.add_argument('--mptcp_type', type=int, default=2, help='1 for mptcp vs tcp, 2 for mptcp vs baseline, 3 for mptcp one vs two links')
    parser.add_argument('--dchannel_exp_type', type=int, default=1, help='1 for all-hb vs pkt-state')
    parser.add_argument('--picoquic_exp_type', type=int, default=1)
    parser.add_argument('--kernel', type=str, default=6, help='5/6 for kernel version 5/6.4.x')
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
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate, args.type, args.ref, args.n_eval, args.fuzzing)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)

        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.fuzzing)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            print(result.F, result.X, time.perf_counter() - start_time)
            problem.save()

        # elif args.alg == 2: #BO
        #     bo = AdvNetBO(args.trace_length, args.l_bounds, args.u_bounds, evaluate, args.n_eval, args.ref, args.seed)
        #     res = bo.run(args.n_calls)         
        #     score = evaluate(res.x, args.ref, 1, True)
        #     print(score)
    
    elif args.type == 1: #mptcp
        if args.kernel == "6":
            os.system("mptcpize run iperf -s &")
        elif args.kernel == "5":
            os.system("iperf -s &")
        if args.alg == 0: #Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_mptcp, args.type, args.ref, args.n_eval, args.mptcp_type, args.kernel)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)
            randomGenerator.save()
        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_mptcp, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.mptcp_type, args.kernel)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            with open("mptcp_results", "a") as f:
                print(args.ref, args.seed, -result.F[0], result.X, time.perf_counter() - start_time, file = f)
            problem.save()
        # score = evaluate_mptcp([2061,20,2844, 1648, 16, 2596], args.ref, args.n_eval, args.mptcp_type, args.kernel, True)
        # print(score)
    elif args.type == 2: #dchannel
        os.system("iperf -s &")
        if args.alg == 0: #Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_dchannel, args.type, args.dchannel_exp_type)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)
        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_dchannel, args.seed, start_time, args.total_time, args.type, args.dchannel_exp_type)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            with open("dchannel_results", "a") as f:
                print(-result.F[0], result.X, time.perf_counter() - start_time, file = f)
    elif args.type == 3: #picoquic
        if args.alg == 0: #Random
            pass
        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_picoquic, args.seed, start_time, args.total_time, args.type, args.picoquic_exp_type, args.ref, args.tar, args.n_eval)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            with open("picoquic_results", "a") as f:
                print("BBR1 vs BBR", (args.trace_length - 2) // 3, "timesteps", args.ref, -result.F[0], result.X, time.perf_counter() - start_time, file = f)
        # score = evaluate_picoquic([186, 10, 7, 7, 21, 3, 17], 1, args.ref, args.tar, args.n_eval)
        # print(score)
    
    os.system("rm traces/*")
    os.system("pkill -9 iperf")
    