import numpy as np
from mptcp.evaluate import evaluate
import copy
from Simplify.single_cc_simplify import SingleCCSimplify

class MpTcpSimplify():
    def __init__(self, initial_trace, pc, mpd, ref, kernel, mptcp_type):
        self.initial_trace = initial_trace
        self.pc = pc #maximum performance to complexity score ratio that would be tolerated by the simplification module
        self.mpd = mpd #maximum percentage decrease of performance that would be tolerated
        self.ref = ref
        self.kernel = kernel
        self.mptcp_type = mptcp_type
        self.initial_p_score = evaluate(self.initial_trace, self.ref, 3, self.mptcp_type, self.kernel)
        self.initial_c_score = self.compute_score(initial_trace)
        self.final_p_score = None

    def compute_score(self, trace):
        score_1 = SingleCCSimplify([0], 0, 0, "", True).compute_score(trace[ : len(trace) // 2])
        score_2 = SingleCCSimplify([0], 0, 0, "", True).compute_score(trace[len(trace) // 2 : ])

        return 0.5 * (score_1 + score_2)
    
    def slice(self, timesteps, trace):
        initial_timesteps = len(trace) // 3
        return trace[:timesteps] + trace[initial_timesteps: initial_timesteps + timesteps] + trace[2 * initial_timesteps: 2 * initial_timesteps + timesteps]
    
    def check_validity(self, c_score, p_score):
        if p_score / self.initial_p_score < 1 - self.mpd:
            return False
        elif p_score / c_score < self.pc:
            return False
        else:
            return True
    
    def shorten_length(self, trace, rest_of_the_trace, append):
        for candidate_length in range(1, len(trace) // 3 + 1):
            short_trace = self.slice(candidate_length, trace)
            org_trace = short_trace + rest_of_the_trace if append else rest_of_the_trace + short_trace
            complexity_score = self.compute_score(org_trace)
            performance_score = evaluate(org_trace, self.ref, 3, self.mptcp_type, self.kernel, simplify = True, index = len(short_trace) if append else len(rest_of_the_trace))

            if self.check_validity(complexity_score, performance_score):
                self.final_p_score = performance_score
                return short_trace
        return trace
    
    def reduce_variance(self, short_trace, rest_of_the_trace, append):
        for i in range(1, 2 * (len(short_trace) // 3)):
            if i % (len(short_trace) // 3) == 0:
                continue
            pct_change = (short_trace[i] - short_trace[i-1]) / short_trace[i-1]
            sign = 1
            if pct_change < 0:
                sign = -1
            for pct in range(0, int(pct_change * 100), sign * 5):
                old = short_trace[i]
                short_trace[i] = round(short_trace[i-1] * (1 + pct / 100))
                org_trace = short_trace + rest_of_the_trace if append else rest_of_the_trace + short_trace
                p_score = evaluate(org_trace, self.ref, 3, self.mptcp_type, self.kernel, simplify = True, index = len(short_trace) if append else len(rest_of_the_trace))
                c_score = self.compute_score(org_trace)

                if self.check_validity(c_score, p_score) == False:
                    short_trace[i] = old
                else:
                    self.final_p_score = p_score
                    break
    def simplify(self):
        prev_length = -1#len(self.initial_trace)
        left_index = len(self.initial_trace) // 2
        shortened_trace = copy.deepcopy(self.initial_trace)
        while True:
            left_trace = shortened_trace[:left_index]
            right_trace = shortened_trace[left_index:]
            shortened_left_trace = self.shorten_length(left_trace, right_trace, True)
            shortened_right_trace = self.shorten_length(right_trace, shortened_left_trace, False)
            shortened_trace = shortened_left_trace + shortened_right_trace
            if prev_length == len(shortened_trace):
                break
            else:
                prev_length = len(shortened_trace)
            self.reduce_variance(shortened_left_trace, shortened_right_trace, True)
            self.reduce_variance(shortened_right_trace, shortened_left_trace, False)
            shortened_trace = shortened_left_trace + shortened_right_trace
            left_index = len(shortened_left_trace)
        return shortened_trace, self.final_p_score, self.compute_score(shortened_trace), self.initial_p_score, self.initial_c_score
        
