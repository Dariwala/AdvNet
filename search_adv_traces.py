"""Entry point for searching adversarial network traces.

This script dispatches across evaluation domains (``--type``) and search
algorithms (``--alg``): Random Generation (RG), Genetic Algorithm (GA),
Bayesian Optimization (BO), an epsilon-greedy baseline (BL), and optional RL
agents. Each domain wires a domain-specific ``evaluate`` function into the
chosen optimizer. See the README for the full argument reference and for how to
add a new domain.
"""

import argparse
import logging
import os
import time

from single_cc.evaluate import evaluate
from GA.problem import CCProblem
from mptcp.evaluate import evaluate as evaluate_mptcp
from mptcp.evaluate import rl_evaluate as evaluate_mptcp_rl
from dchannel.evaluate import evaluate as evaluate_dchannel
from picoquic.evaluate import evaluate as evaluate_picoquic
from ns3_tcp.evaluate import evaluate as evaluate_ns3_tcp
from multiflow.single_cc import evaluate as evaluate_multiflow_single_cc
from multiflow.mptcp import evaluate as evaluate_multiflow_mptcp
from multiflow.picoquic_corrected import evaluate as evaluate_picoquic_multiflow_single_cc
from cache.evaluate import evaluate as evaluate_cache
from random_generator.random_generator import RandomGeneration
from GA.ga import AdvNetGA
from BO.bo import AdvNetBO
from BL.bl import AdvNetEpsGreedy
from RL.single_agent_rl import RLlibEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv
from stable_baselines3.common.vec_env import VecNormalize

# Best-trace summary files (gitignored via the "*_results" pattern).
UC1_RESULTS_FILE = "UC1_results"
FUZZ_RESULTS_FILE = "fuzz_results"
DCHANNEL_RESULTS_FILE = "dchannel_results"
PICOQUIC_RESULTS_FILE = "picoquic_results"


def get_top_individuals(filename, max_time, pop_size):
    """Return the top ``pop_size`` individuals (by score) from a log file.

    Parameters:
        filename (str): Path to the file.
        max_time (float): Maximum allowed time for filtering.
        pop_size (int): Number of top individuals to return.

    Returns:
        top_X (np.ndarray): Array of top individuals (shape: pop_size x n_vars)
        top_scores (np.ndarray): Array of their corresponding scores
    """
    import ast
    import numpy as np

    individuals = []
    scores = []

    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split(maxsplit=3)
            if len(parts) < 4:
                continue
            time = float(parts[1])
            score = float(parts[2])
            if time > max_time:
                break
            # convert string representation of list to actual list
            ind = ast.literal_eval(parts[3])
            individuals.append(ind)
            scores.append(score)

    if not individuals:
        return np.array([]), np.array([])

    # Convert to numpy arrays
    individuals = np.array(individuals)
    scores = np.array(scores)

    # Get indices of top scores (higher is better)
    top_indices = np.argsort(scores)[-pop_size:][::-1]  # descending order

    top_X = individuals[top_indices]
    top_scores = scores[top_indices]

    return top_X, top_scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int, default=0, help="0 for single_cc, 1 for mptcp, 2 for dchannel")
    parser.add_argument('--mptcp_type', type=int, default=2, help='1 for mptcp vs tcp, 2 for mptcp vs baseline, 3 for mptcp one vs two links')
    parser.add_argument('--dchannel_exp_type', type=int, default=1, help='1 for all-hb vs pkt-state')
    parser.add_argument('--picoquic_exp_type', type=int, default=1)
    parser.add_argument('--kernel', type=str, default=5, help='5/6 for kernel version 5/6.4.x')
    parser.add_argument('--initial_pop_file', type=str, default="None", help='Initial population file')
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
    parser.add_argument('--n_processes', type=int, default=50, help='How many processes to spawn to parallelize')
    parser.add_argument('--fuzzing', action='store_true', help='Whether to enable link fuzzing of cc-fuzz or not')
    parser.add_argument('--rl_steps', type=int, help='Number of steps in an episode in RL', default=2)
    parser.add_argument('--history_len', type=int, help='Number of previous steps to consider for observation in RL', default=1)
    parser.add_argument('--gamma', type=float, help='Discount factor in RL', default=0.99)
    parser.add_argument('--cache_size', type=str, default="absolute", help='Cache capacity for the cache domain: absolute (e.g. 100MB / 1GB), or "knob" to make the size a searchable fraction of the workload footprint (last trace element)')
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    if args.type == 0:  # Single CC
        # Update the bounds for link fuzzing.
        if args.fuzzing:
            args.l_bounds = [args.l_bounds[0] for _ in range(args.trace_length)]
            args.u_bounds = [args.u_bounds[0] for _ in range(args.trace_length)]
        os.system("iperf -s &")  # background iperf server used by the emulator
        if args.alg == 0:  # Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate, args.type, args.ref, args.n_eval, args.fuzzing)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)
            randomGenerator.save()
        elif args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.fuzzing)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            if not args.fuzzing:
                with open(UC1_RESULTS_FILE, "a") as f:
                    print(args.ref, (args.trace_length - 1) // 3, "timesteps", -result.F[0], result.X, time.perf_counter() - start_time, file=f)
            else:
                with open(FUZZ_RESULTS_FILE, "a") as f:
                    print(args.ref, args.trace_length, "timesteps", -result.F[0], result.X, time.perf_counter() - start_time, file=f)
            problem.save()

    elif args.type == 1:  # mptcp
        if args.kernel == "6":
            os.system("mptcpize run iperf -s &")
        elif args.kernel == "5":
            pass
        if args.alg == 0:  # Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_mptcp, args.type, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
            randomGenerator.run(args.total_time, args.n_iter)
        elif args.alg == 1:  # GA
            start_time = time.perf_counter()
            if args.initial_pop_file == "None":
                problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_mptcp, args.seed, start_time, args.total_time, args.type, None, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
                ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            else:
                initial_X, initial_F = get_top_individuals(args.initial_pop_file, 3600, args.pop_size)
                from pymoo.core.population import Population
                from pymoo.core.individual import Individual
                individuals = [Individual(X=x, F=f) for x, f in zip(initial_X, initial_F)]
                pop = Population(individuals)
                problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_mptcp, args.seed, start_time, args.total_time, args.type, pop, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
                ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter, pop)
            ga.run()
            problem.save()
        elif args.alg == 2:
            pass
        elif args.alg == 3:
            def make_env():
                gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_mptcp_rl, args.type, args.ref, args.tar, args.mptcp_type, args.kernel, args.rl_steps, args.history_len, args.seed, args.gamma)
                return gym_env
            # Wrap into a DummyVecEnv and normalize observations + rewards.
            venv = DummyVecEnv([make_env])
            venv = VecNormalize(venv, norm_obs=True, norm_reward=True, clip_obs=10.)
            model = PPO("MlpPolicy", venv, verbose=1, n_steps=128, batch_size=32, learning_rate=1e-4, gamma=args.gamma)
            model.learn(total_timesteps=args.n_iter)
            model.save("RL/models/"+args.ref+"_vs_"+args.tar+"_"+str(args.rl_steps)+"_timesteps_with_delay_"+str(args.n_eval)+"_eval_"+str(args.history_len)+"_history_"+str(args.gamma)+"_gamma")
            # Save VecNormalize stats alongside the model.
            venv.save("RL/models/"+args.ref+"_vs_"+args.tar+"_"+str(args.rl_steps)+"_timesteps_with_delay_"+str(args.n_eval)+"_eval_"+str(args.history_len)+"_history_"+str(args.gamma)+"_gamma.pkl")
        elif args.alg == 4:
            start_time = time.perf_counter()
            bo = AdvNetBO(args.trace_length, args.l_bounds, args.u_bounds, evaluate_mptcp, args.type, args.n_iter, args.seed, start_time, args.total_time, None, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
            bo.run()
        elif args.alg == 5:
            start_time = time.perf_counter()
            bo = AdvNetEpsGreedy(args.trace_length, args.l_bounds, args.u_bounds, evaluate_mptcp, args.type, args.n_iter, args.seed, start_time, args.total_time, None, 0.3, 10, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
            bo.run()

    elif args.type == 2:  # dchannel
        os.system("iperf -s &")
        if args.alg == 0:  # Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_dchannel, args.type, args.dchannel_exp_type)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)
        elif args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_dchannel, args.seed, start_time, args.total_time, args.type, args.dchannel_exp_type)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            with open(DCHANNEL_RESULTS_FILE, "a") as f:
                print(-result.F[0], result.X, time.perf_counter() - start_time, file=f)
        elif args.alg == 3:  # RL
            gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_dchannel, args.type, args.dchannel_exp_type)
            model = PPO("MlpPolicy", gym_env, verbose=1, n_steps=2, batch_size=2, learning_rate=1e-4)
            model.learn(total_timesteps=args.n_iter)
            model.save(args.ref+"_"+args.tar+"_PPO")
        score = evaluate_dchannel([282, 45, 10, 9, 24, 23, 41, 3, 45], 1, 1, True)  # cubic 0.75
        print(score)

    elif args.type == 3:  # picoquic
        if args.alg == 0:  # Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_picoquic, args.type, args.picoquic_exp_type, args.ref, args.tar, args.n_eval)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)
            randomGenerator.save()
        elif args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_picoquic, args.seed, start_time, args.total_time, args.type, args.picoquic_exp_type, args.ref, args.tar, args.n_eval)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            with open(PICOQUIC_RESULTS_FILE, "a") as f:
                print(args.ref, (args.trace_length - 2) // 3, "timesteps", args.tar, -result.F[0], result.X, time.perf_counter() - start_time, file=f)
        score = evaluate_picoquic([345, 284, 208, 173, 14, 22, 3306, 28], 2, args.ref, args.tar, args.n_eval, True)
        print(score)

    elif args.type == 4:  # multi-flow single cc
        if args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_multiflow_single_cc, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
        elif args.alg == 3:  # RL
            gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_multiflow_single_cc, args.type, args.ref, args.tar)
            model = PPO("MlpPolicy", gym_env, verbose=1, n_steps=2, batch_size=2, learning_rate=1e-4)
            model.learn(total_timesteps=args.n_iter)
            model.save(args.ref+"_"+args.tar+"_PPO")

    elif args.type == 5:  # multi-flow mptcp
        if args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_multiflow_mptcp, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()

    elif args.type == 6:  # multi-flow single cc picoquic
        if args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_picoquic_multiflow_single_cc, args.seed, start_time, args.total_time, args.type, args.ref, "bbr1", args.n_eval, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
        elif args.alg == 3:  # RL
            gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_picoquic_multiflow_single_cc, args.type, args.ref, "bbr1", args.tar)
            model = PPO("MlpPolicy", gym_env, verbose=1, n_steps=2, batch_size=2, learning_rate=1e-4)
            model.learn(total_timesteps=args.n_iter)
            model.save(args.ref+"_"+args.tar+"_PPO")

    elif args.type == 7:  # ns3 TCP
        if args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_ns3_tcp, args.seed, start_time, args.total_time, args.type, None, args.ref, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
        elif args.alg == 0:  # Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_ns3_tcp, args.type, args.n_iter, args.ref, args.tar)
            trace, score = randomGenerator.run(args.total_time)

    elif args.type == 8:  # cache eviction policy (libCacheSim)
        if args.alg == 1:  # GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_cache, args.seed, start_time, args.total_time, args.type, None, args.ref, args.tar, args.cache_size)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
        elif args.alg == 0:  # Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_cache, args.type, args.n_iter, args.ref, args.tar, args.cache_size)
            randomGenerator.run(args.total_time)

    os.system("pkill -9 iperf")  # clean up the background iperf server(s)
