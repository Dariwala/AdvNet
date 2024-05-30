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
        # self.ref = ref
        # self.n_eval = n_eval
        # self.fuzzing = fuzzing

    def generate_trace(self):
        trace = []

        for i in range(self.trace_length):
            trace.append(self.generator.randint(self.l_bounds[i], self.u_bounds[i]))

        return trace
    
    def run(self, total_time):
        start_time = time.perf_counter()
        best_score = -np.inf
        best_trace = None
        while time.perf_counter() - start_time < total_time:
            trace = self.generate_trace()
            if self.type == 0: #single_cc
                score = self.evaluate(trace, self.args[0], self.args[1], fuzzing = self.args[2])
            elif self.type == 1: #mptcp
                score = self.evaluate(trace, self.args[0])

            if score > best_score:
                best_score = score
                best_trace = trace
        return best_trace, best_score