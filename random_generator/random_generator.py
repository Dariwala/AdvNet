import random
import time
import numpy as np

class RandomGeneration():
    def __init__(self, trace_length, l_bounds, u_bounds, seed, evaluate, type, *args):
        assert len(l_bounds) == len(u_bounds) == trace_length
        self.seed = seed
        self.l_bounds = l_bounds
        self.u_bounds = u_bounds
        self.trace_length = trace_length
        self.generator = random.Random(self.seed)
        self.evaluate = evaluate
        self.args = args
        self.type = type
        self.comps = 0
        self.max_score = -np.inf
        self.max_score_vs_time = []
        # self.ref = ref
        # self.n_eval = n_eval
        # self.fuzzing = fuzzing

    def generate_trace(self):
        self.comps += 1
        trace = []

        for i in range(self.trace_length):
            trace.append(self.generator.randint(self.l_bounds[i], self.u_bounds[i]))

        return trace
    
    def run(self, total_time):
        start_time = time.perf_counter()
        time_passed = time.perf_counter() - start_time
        while time_passed < total_time:
            trace = self.generate_trace()
            if self.type == 0: #single_cc
                score = self.evaluate(trace, self.args[0], self.args[1], fuzzing = self.args[2])
            elif self.type == 1: #mptcp
                score = self.evaluate(trace, self.args[0], self.args[1], self.args[2], self.args[3], self.args[4])
            elif self.type == 2: #dchannel
                score = self.evaluate(trace, self.args[0])

            self.log(trace, time_passed, score)

            if score > self.max_score:
                self.max_score = score
                self.max_score_vs_time.append([time.perf_counter() - start_time, self.max_score])
                self.save(trace, time_passed)
                
            time_passed = time.perf_counter() - start_time

    def log(self, trace, time_passed, score):
        if self.type == 1:
            if self.args[2] == 7:
                with open("time_3600/logs/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_tcoeff_0.1", "a") as f:
                    print(self.comps, time_passed, score, trace, file = f)

    def save(self, trace, time_passed):
        if self.type == 1:
            if self.args[2] == 7:
                with open("time_3600/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_tcoeff_0.1", "a") as f:
                    print(self.comps, time_passed, self.max_score, trace, file = f)