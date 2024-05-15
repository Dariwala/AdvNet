import numpy as np
from single_cc.evaluate import evaluate

class SingleCCSimplify():
    def __init__(self, initial_trace, pc, mpd, ref):
        self.initial_trace = initial_trace
        self.pc = pc #maximum performance to complexity score ratio that would be tolerated by the simplification module
        self.mpd = mpd #maximum percentage decrease of performance that would be tolerated
        self.ref = ref
        self.initial_score = evaluate(self.initial_trace, self.ref, 3)

    def compute_score(self, trace):
        initial_length = len(self.initial_trace)
        length = len(trace)
        variance = self.compute_variance(trace, 0, len(trace) // 3 - 1)
        initial_trace_variance = self.compute_variance(self.initial_trace, 0, len(trace) // 3 - 1)


        try:
            return 0.5 * length / initial_length + 0.5 * variance / initial_trace_variance
        except ZeroDivisionError:
            return 0.5 * length / initial_length
        
    def compute_variance(trace, i, j):
        number_of_timesteps = len(trace) // 3
        sum = 0
        for k in range(i+1, j+1):
            sum += np.abs(trace[k] - trace[k-1])
        for k in range(i+1+number_of_timesteps, j+1+number_of_timesteps):
            sum += np.abs(trace[k] - trace[k-1])
        for k in range(i+1+2*number_of_timesteps, j+1+2*number_of_timesteps):
            sum += np.abs(trace[k] - trace[k-1])
        return sum
    
    def slice(self, timesteps):
        initial_timesteps = len(self.initial_trace) // 3
        return self.initial_trace[:timesteps] + self.initial_trace[initial_timesteps: initial_timesteps + timesteps] + self.initial_trace[2 * initial_timesteps: 2 * initial_timesteps + timesteps]
    
    def check_validity(self, c_score, p_score):
        if p_score / self.initial_score < 1 - self.mpd:
            return False
        elif p_score / c_score < self.pc:
            return False
        else:
            return True
    
    def shorten_length(self):
        for candidate_length in range(2, len(self.initial_trace) + 1):
            candidate_trace = self.slice(candidate_length)
            complexity_score = self.compute_score(candidate_trace)
            performance_score = evaluate(candidate_trace, self.ref, 3)

            if self.check_validity(complexity_score, performance_score):
                return candidate_trace
    