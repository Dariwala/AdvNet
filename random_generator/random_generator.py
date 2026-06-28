"""Random-search baseline for adversarial trace generation.

Samples traces uniformly within the per-dimension bounds and evaluates each with
a domain-specific function, keeping the best score found. Used as the baseline
that AdvNet's learned search is compared against.
"""

import os
import random
import time

import numpy as np


class RandomGeneration():
    """Uniform random search over the trace space (the ``RG`` baseline)."""

    def __init__(self, trace_length, l_bounds, u_bounds, seed, evaluate, type, n_iter, *args):
        """Args:
            trace_length: Number of decision variables (trace length).
            l_bounds / u_bounds: Per-dimension inclusive integer bounds.
            seed: Random seed for reproducible sampling.
            evaluate: Domain evaluation function returning a scalar score.
            type: Domain selector (see ``search_adv_traces.py``).
            n_iter: Maximum number of evaluations.
            *args: Extra, domain-specific arguments forwarded to ``evaluate``.
        """
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
        self.n_iter = n_iter

    @staticmethod
    def _append(path, *values):
        """Append a space-separated record to ``path``, creating dirs as needed."""
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "a") as f:
            print(*values, file=f)

    def generate_trace(self):
        """Sample a single random trace within the configured bounds."""
        self.comps += 1
        trace = []

        for i in range(self.trace_length):
            trace.append(self.generator.randint(self.l_bounds[i], self.u_bounds[i]))

        return trace

    def run(self, total_time):
        """Search until the time budget or evaluation cap (``n_iter``) is hit."""
        start_time = time.perf_counter()
        time_passed = time.perf_counter() - start_time
        while time_passed < total_time and self.comps < self.n_iter:
            trace = self.generate_trace()
            if self.type == 0:  # single_cc
                score = self.evaluate(trace, self.args[0], self.args[1], fuzzing = self.args[2])
            elif self.type == 1:  # mptcp
                score = self.evaluate(trace, self.args[0], self.args[1], self.args[2], self.args[3], self.args[4])
            elif self.type == 2:  # dchannel
                score = self.evaluate(trace, self.args[0])
            elif self.type == 7:
                score = self.evaluate(trace, self.args[0], self.args[1])

            self.log(trace, time_passed, score)

            if score > self.max_score:
                self.max_score = score
                self.max_score_vs_time.append([time.perf_counter() - start_time, self.max_score])
                self.save(trace, time_passed)

            time_passed = time.perf_counter() - start_time

    def log(self, trace, time_passed, score):
        """Log every evaluated trace to the per-domain log file."""
        if self.type == 1:
            if self.args[2] == 7:
<<<<<<< Updated upstream
                self._append("time_3600/logs/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_tcoeff_0.1", self.comps, time_passed, score, trace)
        elif self.type == 7:
            self._append("t_coeff_0.5/logs/score_across_comparisons_NS3_RG_"+self.args[0]+"_vs_"+self.args[1]+"_2_timesteps_with_delay", self.comps, score, trace)
=======
                with open("d_coeff_1/logs/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_3600", "a") as f:
                    print(self.comps, time_passed, score, trace, file = f)
            elif self.args[2] == 8:
                with open("t_coeff_0.5/logs/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_serial_"+str(self.args[1])+"_eval_median_iter_150", "a") as f:
                    print(self.comps, time_passed, score, trace, file = f)
>>>>>>> Stashed changes

    def save(self, trace, time_passed):
        """Record the best trace so far to the per-domain results file."""
        if self.type == 1:
            if self.args[2] == 7:
<<<<<<< Updated upstream
                self._append("time_3600/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_tcoeff_0.1", self.comps, time_passed, self.max_score, trace)
        elif self.type == 7:
            self._append("t_coeff_0.5/score_across_comparisons_NS3_RG_"+self.args[0]+"_vs_"+self.args[1]+"_2_timesteps_with_delay", self.comps, self.max_score, trace)
=======
                with open("d_coeff_1/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_3600", "a") as f:
                    print(self.comps, time_passed, self.max_score, trace, file = f)
            elif self.args[2] == 8:
                with open("t_coeff_0.5/score_across_comparisons_RG_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_serial_"+str(self.args[1])+"_eval_median_iter_150", "a") as f:
                    print(self.comps, time_passed, self.max_score, trace, file = f)
>>>>>>> Stashed changes
