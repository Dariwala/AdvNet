import random

class RandomGeneration():
    def __init__(self, trace_length, l_bounds, u_bounds, seed):
        assert len(l_bounds) == len(u_bounds) == trace_length
        self.seed = seed
        self.l_bounds = l_bounds
        self.u_bounds = u_bounds
        self.trace_length = trace_length
        self.generator = random.Random(self.seed)

    def generate_trace(self):
        trace = []

        for i in range(self.trace_length):
            trace.append(self.generator.randint(self.l_bounds[i], self.u_bounds[i]))

        return trace