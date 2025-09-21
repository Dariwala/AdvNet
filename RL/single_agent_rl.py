import numpy as np
import gymnasium as gym
from gymnasium.spaces import MultiDiscrete, Box
from NoiseHandler.noisehandler import NoiseHandler
import random
import threading
import uuid
from mptcp.convert import convert as mptcp_convert
from config import parent_folder
from time import sleep
import os
import shutil
import struct
from mptcp.evaluate import evaluate as mptcp_evaluate
import logging

class RLlibEnv(gym.Env):
    def __init__(self, l_bound, bound_range, n_evals, evaluate, *args):
        super(RLlibEnv, self).__init__()
        self.l_bound = l_bound
        self.bound_range = bound_range
        self.n_evals = n_evals
        self.max_reward = -np.inf
        self.comp = 0
        self.eval = evaluate
        self.args = args
        self.steps_in_an_episode = self.args[5]
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.debug("Constructor called")

        if self.args[0] == 1 and self.args[3] == 7: #single cc among each other
            #last one is queue size which is time-invariant so outside of RL action, the second last one is duration
            self.action_space = MultiDiscrete(self.bound_range[:-2])
            self.time_invariant_bound_range = [self.bound_range[-2]] * self.steps_in_an_episode + self.bound_range[-1:]
            self.bound_range = self.bound_range[:-2]
            self.time_invariant_l_bound = [self.l_bound[-2]] * self.steps_in_an_episode + self.l_bound[-1:]
            self.l_bound = self.l_bound[:-2]

            # Observation space : avg. throughput, avg. latency, queue occupancy
            self.observation_space = Box(low=np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]), high=np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]), shape=(6,), dtype=np.float64)
            self.prev_tot_delay = [0 for _ in range(2 * self.n_evals)]
            self.prev_tot_bytes = [0 for _ in range(2 * self.n_evals)]
            self.prev_no_packets = [0 for _ in range(2 * self.n_evals)]
            self.prev_timestamps = [0 for _ in range(2 * self.n_evals)]

            self.history_length = self.args[6]
            self.logger.info(f"Time variant portion: {self.l_bound} {self.bound_range}")
            self.logger.info(f"Time invariant portion: {self.time_invariant_l_bound} {self.time_invariant_bound_range}")

        self.current_step_no = 0
        self.generator = random.Random(self.args[7])

        self.folders = []
        self.results = {}
        self.sleep_times = []
        self.trace = []

        for i in range(2 * n_evals):
            folder = f"{uuid.uuid4().hex}"+"_"+str(i)+"/"
            self.folders.append(folder)
            os.makedirs(parent_folder + folder)
        
        self.logger.debug("Folders created")
    
    def delete_and_recreate_folders(self):
        for i in range(self.n_evals * 2):
            shutil.rmtree(parent_folder + self.folders[i])
            sleep(0.05)
            os.makedirs(parent_folder + self.folders[i])

    def reset(self, *, seed=None, options=None):
        self.state = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])  # Initialize state
        info = {}  # Return any additional info (can be empty)
        self.results = {}
        self.current_step_no = 0
        # self.sleep_times = []
        self.trace = []
        self.prev_tot_delay = [0 for _ in range(2 * self.n_evals)]
        self.prev_tot_bytes = [0 for _ in range(2 * self.n_evals)]
        self.prev_no_packets = [0 for _ in range(2 * self.n_evals)]
        self.prev_timestamps = [0 for _ in range(2 * self.n_evals)]
        os.system("sudo pkill -9 mm")
        self.logger.debug("Reset method initialized everything")
        self.delete_and_recreate_folders()
        return self.state, info
    
    def wait_until_start_of_flow(self, folder):
        while True:
            if os.path.exists(parent_folder + folder + "packet-log-output-uplink"):
                with open(parent_folder + folder + "packet-log-output-uplink") as f:
                    line = f.readline()

                    if not line:
                        sleep(0.05)
                        continue
                    else:
                        break
            else:
                sleep(0.05)
    
    def read_stat(self, flow_number):
        folder = self.folders[flow_number]

        if self.current_step_no == 0:
            while True:
                if os.path.exists(parent_folder + folder + "stats-uplink.txt") == False:
                    sleep(0.05)
                else:
                    break

        while True:
            with open(parent_folder + folder + "stats-uplink.txt") as f:
                lines = list(f)
                if len(lines) < self.current_step_no + 1:
                    sleep(0.05)
                    continue
                line = lines[self.current_step_no][:-1].split('\t')

                curr_time = int(line[0])
                tot_bytes_sent = int(line[1])
                tot_packets_sent = int(line[2])
                tot_latency = int(line[3])
                queue_occupancy = float(line[4])
                self.logger.debug(f"Flow {flow_number + 1} statistics after timestep {self.current_step_no + 1}: {curr_time} {tot_bytes_sent}, {tot_packets_sent} {tot_latency} {queue_occupancy}")
                break

        self.results[str(flow_number)+"_"+str(self.current_step_no)]=[curr_time, tot_bytes_sent, tot_packets_sent, tot_latency, queue_occupancy]

    
    # def handle_one_flow(self, flow_number):
    #     self.wait_until_start_of_flow(self.folders[flow_number])
    #     self.logger.debug(f"Flow {flow_number + 1} started sending packets")
    #     for i, sleep_time in enumerate(self.sleep_times):
    #         sleep(sleep_time / 1000)
    #         self.logger.debug(f"Flow {flow_number + 1} slept for {sleep_time} ms")

    #         with open(parent_folder + self.folders[flow_number] + "stats_uplink.txt") as f:
    #             line = f.readline()[:-1].split()
    #             tot_bytes_sent = int(line[1])
    #             tot_packets_sent = int(line[2])
    #             tot_latency = int(line[3])
    #             queue_occupancy = float(line[4])
    #             self.logger.debug(f"Flow {flow_number + 1} statistics after timestep {i+1}: {tot_bytes_sent}, {tot_packets_sent} {tot_latency} {queue_occupancy}")
    #         with self.lock:
    #             self.results[str(flow_number)+"_"+str(i)]=[tot_bytes_sent, tot_packets_sent, tot_latency, queue_occupancy]

    def get_reward(self):
        for i in range(2 * self.n_evals):
            self.read_stat(i)
        # sleep(self.sleep_times[self.current_step_no] / 1000)
        self.logger.debug(f"Main thread collected stats for timestep {self.current_step_no + 1}")
        scores = []
        throughputs = []
        delays = []
        occupancies_ref = []
        occupancies_tar = []
        for i in range(2 * self.n_evals):
            curr_time, tot_bytes_sent, tot_packets_sent, tot_latency, queue_occupancy = self.results[str(i)+"_"+str(self.current_step_no)]
            throughput = (tot_bytes_sent - self.prev_tot_bytes[i]) * 0.008 / (curr_time - self.prev_timestamps[i])
            throughputs.append(throughput)
            self.prev_tot_bytes[i] = tot_bytes_sent
            self.prev_timestamps[i] = curr_time
            try:
                delay = (tot_latency - self.prev_tot_delay[i]) / (tot_packets_sent - self.prev_no_packets[i])
            except ZeroDivisionError:
                delay = 0
                self.logger.debug("Delay is 0")

            delays.append(delay)
            self.prev_tot_delay[i] = tot_latency
            self.prev_no_packets[i] = tot_packets_sent
            if i%2 == 0:
                occupancies_ref.append(queue_occupancy)
            else:
                occupancies_tar.append(queue_occupancy)
        i = 0
        sum_throughput_ref = sum_throughput_tar = sum_delay_ref = sum_delay_tar = 0
        while i < len(throughputs):
            throughput_ref = throughputs[i]
            throughput_tar = throughputs[i+1]
            sum_throughput_ref += throughput_ref
            sum_throughput_tar += throughput_tar
            delay_ref = delays[i]
            delay_tar = delays[i+1]
            sum_delay_ref += delay_ref
            sum_delay_tar += delay_tar

            score = (throughput_ref - throughput_tar) / (throughput_ref * 2) + (delay_tar - delay_ref) / (delay_tar * 2)
            scores.append(score)

            i+=2
        
        self.state = np.array([sum_throughput_ref / (self.n_evals * (self.bound_range[0] + self.l_bound[0] - 1)),
                               sum_throughput_tar / (self.n_evals * (self.bound_range[0] + self.l_bound[0] - 1)),
                               sum_delay_ref / (self.n_evals * (self.bound_range[1] + self.l_bound[1] - 1)),
                               sum_delay_tar / (self.n_evals * (self.bound_range[1] + self.l_bound[1] - 1)),
                               sum(occupancies_ref) / self.n_evals,
                               sum(occupancies_tar) / self.n_evals,
                            ])

        noiseHandler = NoiseHandler().mean
        score = noiseHandler(scores)
        return score
    
    def take_action(self, bandwidth, latency):
        self.logger.debug(f"Main thread will take action for timestep {self.current_step_no + 1}")
        for i in range(self.n_evals * 2):
            pdo_uplink_path = parent_folder + self.folders[i] + "schedule_pipe-uplink"
            pdo_downlink_path = parent_folder + self.folders[i] + "schedule_pipe-downlink"
            delay_uplink_path = parent_folder + self.folders[i] + "delay_trace_pipe-uplink"
            delay_downlink_path = parent_folder + self.folders[i] + "delay_trace_pipe-downlink"

            pdo_data = [bandwidth * 1000, 1]
            latency_data = [1, latency * 5]

            self.logger.debug(f"Main thread writing action to {self.folders[i]}")

            with open(pdo_uplink_path, "wb") as fifo:
                payload = struct.pack("Q", len(pdo_data)) + struct.pack(f"{len(pdo_data)}Q", *pdo_data)
                self.logger.debug(f"Payload that will be written to pdo uplink: {payload}")
                fifo.write(payload)
            
            with open(pdo_downlink_path, "wb") as fifo:
                fifo.write(payload)

            with open(delay_uplink_path, "wb") as fifo:
                payload = struct.pack("Q", len(latency_data)) + struct.pack(f"{len(latency_data)}Q", *latency_data)
                fifo.write(payload)
            
            with open(delay_downlink_path, "wb") as fifo:
                fifo.write(payload)

    def step(self, action):
        self.logger.debug(f"Step method called with action: {action}")
        if self.current_step_no == 0:
            if self.args[0] == 1 and self.args[3] == 7:
                time_invariant_trace = []
                for i in range(len(self.time_invariant_l_bound)):
                    time_invariant_trace.append(self.generator.randrange(self.time_invariant_l_bound[i], self.time_invariant_l_bound[i] + self.time_invariant_bound_range[i]))
                self.logger.debug(f"Time invariant trace: {time_invariant_trace}")
                self.comp += 1
                trace = []
                for i in range(len(action)):
                    trace += [self.l_bound[i] + action[i]] * self.steps_in_an_episode
                trace += time_invariant_trace
                self.logger.debug(f"Initial trace from action: {trace}")
                self.trace = trace

                # self.sleep_times = self.compute_sleep_time(trace)
                # self.logger.debug(f"Sleep times: {self.sleep_times}")
                # for i in range(self.n_evals * 2):
                #     t = threading.Thread(target = self.handle_one_flow, args=(i,))
                #     t.start()
                #     self.logger.debug(f"Thread for handling flow {i+1} started")
                
                t = threading.Thread(target = self.eval, args=(trace, self.args[1], self.n_evals, self.args[3], self.args[4], self.args[2], self.folders))  # Calculate reward
                t.start()
                self.logger.debug("Thread calling evaluate method started")
        else:
            self.take_action(self.l_bound[0] + action[0], self.l_bound[1] + action[1])
            self.trace[self.current_step_no] = self.l_bound[0] + action[0]
            self.trace[self.current_step_no + self.steps_in_an_episode] = self.l_bound[1] + action[1]
        reward = self.get_reward()
            
        truncated = False  # Flag if episode is truncated
        info = {}  # Add any additional information here (can be empty)

        done = False
        self.current_step_no += 1

        if self.current_step_no == self.steps_in_an_episode:
            done = True
            self.log()
        return self.state, reward, done, truncated, info
    
    # def compute_sleep_time(self, trace):
    #     if self.args[0] == 1:
    #         converted_trace = mptcp_convert(trace, self.args[3])
    #         sleep_times = converted_trace[-self.steps_in_an_episode-1:-1]
    #     return sleep_times


    def log(self):
        self.logger.debug("Episode finished. Main thread computing score of the trace")
        if self.args[0] == 1:
            reward = mptcp_evaluate(self.trace, self.args[1], self.n_evals, self.args[3], self.args[4], self.args[2])
        elif self.args[0] == 4:
            reward = self.eval(self.trace, self.args[1], self.n_evals, self.args[2])
        if reward > self.max_reward:
            self.max_reward = reward
            if self.args[0] == 1:#mptcp
                with open("results/score_across_comparisons_SRL_"+self.args[1]+"_vs_"+self.args[2]+"_2_timesteps_with_delay_1_eval", "a") as f:
                    print(self.comp, self.max_reward, self.trace, file = f)
            elif self.args[0] == 4:#multi-flow
                with open("results/score_across_comparisons_SRL_"+self.args[1]+"_vs_"+self.args[2]+"_2_timesteps_multiflow", "a") as f:
                    print(self.comp, self.max_reward, self.trace, file = f)
        return reward