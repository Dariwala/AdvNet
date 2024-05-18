import numpy as np
from single_cc.evaluate import evaluate
import copy

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
        
    def compute_variance(self, trace, i, j):
        number_of_timesteps = len(trace) // 3
        sum = 0
        for k in range(i+1, j+1):
            sum += np.abs(trace[k] - trace[k-1])
        for k in range(i+1+number_of_timesteps, j+1+number_of_timesteps):
            sum += np.abs(trace[k] - trace[k-1])
        for k in range(i+1+2*number_of_timesteps, j+1+2*number_of_timesteps):
            sum += np.abs(trace[k] - trace[k-1])
        return sum
    
    def slice(self, timesteps, trace):
        initial_timesteps = len(trace) // 3
        return trace[:timesteps] + trace[initial_timesteps: initial_timesteps + timesteps] + trace[2 * initial_timesteps: 2 * initial_timesteps + timesteps]
    
    def check_validity(self, c_score, p_score):
        if p_score / self.initial_score < 1 - self.mpd:
            return False
        elif p_score / c_score < self.pc:
            return False
        else:
            return True
    
    def shorten_length(self, trace):
        for candidate_length in range(2, len(trace) // 3 + 1):
            candidate_trace = self.slice(candidate_length, trace)
            complexity_score = self.compute_score(candidate_trace)
            performance_score = evaluate(candidate_trace, self.ref, 3)

            if self.check_validity(complexity_score, performance_score):
                return candidate_trace
        return trace
    
    def reduce_variance(self, short_trace):
        for i in range(1, len(short_trace)):
            if i % (len(short_trace) // 3) == 0:
                continue
            pct_change = (short_trace[i] - short_trace[i-1]) / short_trace[i-1]
            sign = 1
            if pct_change < 0:
                sign = -1
            for pct in range(0, int(pct_change * 100), sign * 5):
                old = short_trace[i]
                short_trace[i] = round(short_trace[i-1] * (1 + pct / 100))
                p_score = evaluate(short_trace, self.ref, 3)
                c_score = self.compute_score(short_trace)

                if self.check_validity(c_score, p_score) == False:
                    short_trace[i] = old
                else:
                    break
    def simplify(self):
        prev_length = len(self.initial_trace)
        shortened_trace = copy.deepcopy(self.initial_trace)
        while True:
            shortened_trace = self.shorten_length(shortened_trace)
            if prev_length == len(shortened_trace):
                break
            else:
                prev_length = len(shortened_trace)
            self.reduce_variance(shortened_trace)
        return shortened_trace, evaluate(shortened_trace, self.ref, 3), self.compute_score(shortened_trace)
        
