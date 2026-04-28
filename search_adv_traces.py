import argparse
import multiprocessing
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
from random_generator.random_generator import RandomGeneration
import os, subprocess
from GA.ga import AdvNetGA
from BO.bo import AdvNetBO
from BL.bl import AdvNetEpsGreedy
from pymoo.core.problem import StarmapParallelization
# from RL.bandit import Env, MonteCarloBanditAgent, bandit_learning
from RL.single_agent_rl import RLlibEnv
# from RL.multi_agent_rl import RLlibMultiAgentEnv, FlattenedMultiAgentEnv
# from ray.rllib.algorithms.ppo import PPOConfig
# from ray.rllib.algorithms.a3c import A3CConfig
# from ray.rllib.algorithms.bandit import BanditConfig
# from ray import tune
# from RL.bandit import BanditEnv
# from ray.tune.registry import register_env
# from RL.custom_environment import CustomEnvironment
# from gymnasium.spaces import Discrete
# from ray.rllib.env import PettingZooEnv
# from ray.rllib.env.wrappers.multi_agent_env_compatibility import MultiAgentEnvCompatibility
import time
# import supersuit as ss
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import DummyVecEnv
from stable_baselines3.common.vec_env import VecNormalize
import logging
# from pettingzoo.utils import parallel_to_aec
# from pettingzoo.utils.wrappers import BaseParallelWrapper

# def env_creator(config):
#     raw_env = CustomEnvironment(config=config)
#     return PettingZooEnv(raw_env)

def get_top_individuals(filename, max_time, pop_size):
    import ast
    import numpy as np
    """
    Reads a file and returns the top `pop_size` individuals (decision variables)
    with the highest scores, filtering by maximum time.
    
    Parameters:
        filename (str): Path to the file.
        max_time (float): Maximum allowed time for filtering.
        pop_size (int): Number of top individuals to return.
    
    Returns:
        top_X (np.ndarray): Array of top individuals (shape: pop_size x n_vars)
        top_scores (np.ndarray): Array of their corresponding scores
    """
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
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    # Disable logging globally:
    logging.disable(logging.NOTSET)  # turns off all logs <= CRITICAL

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
            randomGenerator.save()

        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.fuzzing)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            if not args.fuzzing:
                with open("UC1_results", "a") as f:
                    print(args.ref, (args.trace_length - 1) // 3 ,"timesteps", -result.F[0], result.X, time.perf_counter() - start_time, file = f)
            else:
                with open("fuzz_results", "a") as f:
                    print(args.ref, args.trace_length ,"timesteps", -result.F[0], result.X, time.perf_counter() - start_time, file = f)
            problem.save()
        # score = evaluate([10, 7, 21, 17], args.ref, args.n_eval, True)
        # print(score)
        # elif args.alg == 2: #BO
        #     bo = AdvNetBO(args.trace_length, args.l_bounds, args.u_bounds, evaluate, args.n_eval, args.ref, args.seed)
        #     res = bo.run(args.n_calls)         
        #     score = evaluate(res.x, args.ref, 1, True)
        #     print(score)
    
    elif args.type == 1: #mptcp
        if args.kernel == "6":
            os.system("mptcpize run iperf -s &")
        elif args.kernel == "5":
            # os.system("iperf -s &")
            pass
        if args.alg == 0: #Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_mptcp, args.type, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
            randomGenerator.run(args.total_time, args.n_iter)
            # print(trace, score)
            # randomGenerator.save()
        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            # initialize the thread pool and create the runner
            # n_proccess = args.n_processes
            # pool = multiprocessing.Pool(n_proccess)
            # runner = StarmapParallelization(pool.starmap)
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
            # pool.close()  # Prevents new tasks from being submitted
            # pool.join()   # Waits for all workers to finish
            # with open("UC2_SPTCP_Linux_Kernel_with_delay_coeff", "a") as f:
            #     print(args.ref, "vs", args.tar, (args.trace_length - 1) // 5, "timesteps", -result.F[0], result.X, time.perf_counter() - start_time, file = f)
            problem.save()
        elif args.alg == 2:
            pass
            # Define configuration for the environment
            # config = {
            #     "l_bound": args.l_bounds,
            #     "bound_range": [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)],
            #     "ref": args.ref,
            #     "tar": args.tar,
            #     "mptcp_type": args.mptcp_type,
            #     "n_evals": args.n_eval,
            #     "kernel": args.kernel,
            # }

            # Register the custom environment
            # tune.register_env("BanditEnv", lambda cfg: BanditEnv(cfg))

            # Run the Bandit optimization
            # tune.run(
            #     "PPO",  # You can replace "PPO" with any supported RLlib algorithm like "DQN" or "A3C"
            #     config={
            #         "env": "BanditEnv",
            #         "env_config": config,
            #         "gamma": 0.99,  # Optional: Discount factor
            #     },
            #     stop={"training_iteration": args.n_iter},
            #     local_dir="./results",
            # )
        elif args.alg == 3:
            pass
            # Define the configuration for the RLlib environment
            # config = {
            #     "l_bound": args.l_bounds,
            #     "bound_range": [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)],
            #     "ref": args.ref,
            #     "tar": args.tar,
            #     "mptcp_type": args.mptcp_type,
            #     "n_evals": args.n_eval,
            #     "kernel": args.kernel,
            # }

            # Register the environment
            # tune.register_env("RLlibEnv", lambda cfg: RLlibEnv(cfg))

            # Configure the PPO algorithm
            # ppo_config = (
            #     A3CConfig()
            #     .environment("RLlibEnv", env_config=config)
            #     .framework("torch")
            #     .training(
            #         train_batch_size=25,
            #         sgd_minibatch_size=5,  # Set to a smaller value <= train_batch_size
            #         gamma=0.99,
            #     ).rollouts(
            #         num_rollout_workers=1  # Use only 1 worker for sequential execution
            #     )
            # )

            # Train the RLlib agent
            # tune.run(
            #     "A3C",
            #     config=ppo_config.to_dict(),
            #     stop={"training_iteration": args.n_iter},  # Stop after 50 iterations
            #     local_dir="./results",  # Save results to this directory
            # )
            def make_env():
                gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_mptcp_rl, args.type, args.ref, args.tar, args.mptcp_type, args.kernel, args.rl_steps, args.history_len, args.seed, args.gamma)
                return gym_env
            # 2. Wrap into a DummyVecEnv
            venv = DummyVecEnv([make_env])

            # 3. Add VecNormalize wrapper (normalizes obs + rewards)
            venv = VecNormalize(venv, norm_obs=True, norm_reward=True, clip_obs=10.)
            # Train using Stable-Baselines3
            model = PPO("MlpPolicy", venv, verbose=1, n_steps = 128, batch_size = 32, learning_rate = 1e-4, gamma=args.gamma)

            # Train the model
            model.learn(total_timesteps=args.n_iter)

            # Save the model
            model.save("RL/models/"+args.ref+"_vs_"+args.tar+"_"+str(args.rl_steps)+"_timesteps_with_delay_"+str(args.n_eval)+"_eval_"+str(args.history_len)+"_history_"+str(args.gamma)+"_gamma")
            # Save VecNormalize stats
            venv.save("RL/models/"+args.ref+"_vs_"+args.tar+"_"+str(args.rl_steps)+"_timesteps_with_delay_"+str(args.n_eval)+"_eval_"+str(args.history_len)+"_history_"+str(args.gamma)+"_gamma.pkl")
        # score = evaluate_mptcp([2 ,  5 , 68 , 17 , 30 ,363], args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar, True)
        # score = evaluate_mptcp([76, 106,  20,   5,  53,   8,   3,  16,  45,  40, 426], args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar, True)
        # print(score)
        # elif args.alg == 4:
            # Define the multi-agent environment config
            # env_config = {
            #     "l_bound": args.l_bounds,
            #     "bound_range": [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)],
            #     "ref": args.ref,
            #     "tar": args.tar,
            #     "mptcp_type": args.mptcp_type,
            #     "n_evals": args.n_eval,
            #     "kernel": args.kernel,
            #     "num_agents": 2,  # Define the number of agents
            # }

            # Register the environment
            # register_env("custom_pettingzoo_env", env_creator)

            # Create your PettingZoo environment instance
            # raw_env = CustomEnvironment(config=env_config)

            # Wrap the environment with PettingZooEnv
            # rllib_env = PettingZooEnv(raw_env)

            # Set up Ray RLLib configuration for multi-agent PPO
            # config = PPOConfig().environment(
            #     env="custom_pettingzoo_env", env_config=env_config
            # ).multi_agent(
            #     policies={
            #         "policy_0": (None, Discrete(1), env_config["bound_range"], {}),
            #         "policy_1": (None, Discrete(1), env_config["bound_range"], {}),
            #     },
            #     policy_mapping_fn=lambda agent_id: "policy_0" if agent_id == "agent_0" else "policy_1",
            # ).rollouts(num_rollout_workers=1)

            # Running the experiment with Ray Tune
            # tune.run("PPO", config=config.to_dict(), stop={"training_iteration": args.n_iter})  # Adjust the number of iterations
            # Initialize the PettingZoo parallel environment
            # multi_agent_env = RLlibMultiAgentEnv(env_config)

            # Wrap it with the FlattenedMultiAgentEnv wrapper
            # gym_env = FlattenedMultiAgentEnv(multi_agent_env)

            # Train using Stable-Baselines3
            # model = PPO("MlpPolicy", gym_env, verbose=1)

            # Train the model
            # model.learn(total_timesteps=1)

            # Save the model
            # model.save("ppo_custom_env")
        elif args.alg == 4:
            start_time = time.perf_counter()
            bo = AdvNetBO(args.trace_length, args.l_bounds, args.u_bounds, evaluate_mptcp, args.type, args.n_iter, args.seed, start_time, args.total_time, None, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
            bo.run()
        elif args.alg == 5:
            start_time = time.perf_counter()
            bo = AdvNetEpsGreedy(args.trace_length, args.l_bounds, args.u_bounds, evaluate_mptcp, args.type, args.n_iter, args.seed, start_time, args.total_time, None, 0.3, 10, args.ref, args.n_eval, args.mptcp_type, args.kernel, args.tar)
            bo.run()
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
        elif args.alg == 3: #RL
            gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_dchannel, args.type, args.dchannel_exp_type)
            
            # Train using Stable-Baselines3
            model = PPO("MlpPolicy", gym_env, verbose=1, n_steps = 2, batch_size = 2, learning_rate = 1e-4)

            # Train the model
            model.learn(total_timesteps=args.n_iter)

            # Save the model
            model.save(args.ref+"_"+args.tar+"_PPO")
        # score = evaluate_dchannel([171, 57, 10, 4, 4, 2, 10, 5, 11], 1, 1, True) #balia 0.75
        # score = evaluate_dchannel([101, 73, 8, 9, 4, 19, 67, 5, 14], 1, 1, True) # balia 2
        score = evaluate_dchannel([282, 45, 10, 9, 24, 23, 41, 3, 45], 1, 1, True) # cubic 0.75
        print(score)
    elif args.type == 3: #picoquic
        if args.alg == 0: #Random
            randomGenerator = RandomGeneration(args.trace_length, args.l_bounds, args.u_bounds, args.seed, evaluate_picoquic, args.type, args.picoquic_exp_type, args.ref, args.tar, args.n_eval)
            trace, score = randomGenerator.run(args.total_time)
            print(trace, score)
            randomGenerator.save()
        elif args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_picoquic, args.seed, start_time, args.total_time, args.type, args.picoquic_exp_type, args.ref, args.tar, args.n_eval)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            with open("picoquic_results", "a") as f:
                print(args.ref, (args.trace_length - 2) // 3, "timesteps", args.tar, -result.F[0], result.X, time.perf_counter() - start_time, file = f)
        score = evaluate_picoquic([345,  284,  208,  173,   14,   22, 3306,   28], 2, args.ref, args.tar, args.n_eval, True)
        print(score)
    elif args.type == 4: #multi-flow single cc
        if args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_multiflow_single_cc, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            # with open("UC2_SPTCP_Linux_Kernel_with_delay_coeff", "a") as f:
            #     print(args.ref, "vs", args.tar, (args.trace_length - 1) // 5, "timesteps", -result.F[0], result.X, time.perf_counter() - start_time, file = f)
            # problem.save()
        elif args.alg == 3: #RL
            gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_multiflow_single_cc, args.type, args.ref, args.tar)
            
            # Train using Stable-Baselines3
            model = PPO("MlpPolicy", gym_env, verbose=1, n_steps = 2, batch_size = 2, learning_rate = 1e-4)

            # Train the model
            model.learn(total_timesteps=args.n_iter)

            # Save the model
            model.save(args.ref+"_"+args.tar+"_PPO")
    elif args.type == 5: #multi-flow mptcp
        if args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_multiflow_mptcp, args.seed, start_time, args.total_time, args.type, args.ref, args.n_eval, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
    elif args.type == 6: #multi-flow single cc picoquic
        if args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_picoquic_multiflow_single_cc, args.seed, start_time, args.total_time, args.type, args.ref, "bbr1", args.n_eval, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
        elif args.alg == 3: #RL
            gym_env = RLlibEnv(args.l_bounds, [args.u_bounds[i] - args.l_bounds[i] + 1 for i in range(args.trace_length)], args.n_eval, evaluate_picoquic_multiflow_single_cc, args.type, args.ref, "bbr1", args.tar)
            
            # Train using Stable-Baselines3
            model = PPO("MlpPolicy", gym_env, verbose=1, n_steps = 2, batch_size = 2, learning_rate = 1e-4)

            # Train the model
            model.learn(total_timesteps=args.n_iter)

            # Save the model
            model.save(args.ref+"_"+args.tar+"_PPO")
    elif args.type == 7: #ns3 TCP
        if args.alg == 1: #GA
            start_time = time.perf_counter()
            problem = CCProblem(args.trace_length, args.l_bounds, args.u_bounds, evaluate_ns3_tcp, args.seed, start_time, args.total_time, args.type, None, args.ref, args.tar)
            ga = AdvNetGA(problem, args.pop_size, args.seed, args.n_iter)
            result = ga.run()
            
    # os.system("rm traces/*")
    os.system("pkill -9 iperf")
    