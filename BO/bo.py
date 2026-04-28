from skopt import forest_minimize
import numpy as np
import time


class AdvNetBO():
    def __init__(self, trace_length, lower_bound, upper_bound,
                 evaluate, type,
                 n_calls, seed,
                 start_time, total_time,
                 init_points=None, *args):

        self.trace_length = trace_length
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)

        self.func = evaluate
        self.args = args
        self.type = type

        self.n_calls = n_calls
        self.seed = seed

        self.start_time = start_time
        self.total_time = total_time

        self.init_points = init_points

        # Tracking (same as GA)
        self.max_score = -np.inf
        self.comps = 0

    def _evaluate(self, x):
        time_passed = time.perf_counter() - self.start_time

        # Stop condition based on time
        if time_passed > self.total_time:
            return -self.max_score

        self.comps += 1

        # --- Match GA evaluation logic ---
        if self.type == 0:
            score = self.func(list(x), self.args[0], self.args[1], fuzzing=self.args[2])
        elif self.type == 1:
            score = self.func(list(x), self.args[0], self.args[1],
                              self.args[2], self.args[3], self.args[4])
        elif self.type == 2:
            score = self.func(list(x), self.args[0])
        elif self.type == 3:
            score = self.func(list(x), self.args[0], self.args[1],
                              self.args[2], self.args[3])
        elif self.type == 4:
            score = self.func(list(x), self.args[0],
                              self.args[1], self.args[2])
        elif self.type == 5:
            score = self.func(list(x), self.args[0],
                              self.args[1], self.args[2])
        elif self.type == 6:
            score = self.func(list(x), self.args[0],
                              self.args[1], self.args[2], self.args[3])
        else:
            raise ValueError("Unknown type")
        
        self.update_max_score(time_passed, x, score)
        self.log(time_passed, x, score)

        return -score  # minimize
    
    def update_max_score(self, time_passed, x, score):
        if score > self.max_score:##
            self.max_score = score
            if self.type == 6:
                with open("results/score_across_comparisons_GA_"+self.args[0]+"_and_"+self.args[1]+"_vs_"+self.args[3]+"_2_timesteps_multiflow_picoquic", "a") as f:
                    print(self.comps, self.max_score, list(x), file = f)
            elif self.type == 1:
                if self.args[2] == 6:
                    with open("results/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay", "a") as f:
                        print(self.comps, self.max_score, list(x), file = f)
                elif self.args[2] == 7:
                    with open("t_coeff_0.5/score_across_comparisons_BO_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_7200", "a") as f:
                        print(self.comps, time_passed, self.max_score, list(x), file = f)
                elif self.args[2] == 8:
                    with open("t_coeff_0.5/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_serial_"+str(self.args[1])+"_eval_median_iter_250", "a") as f:
                        print(self.comps, time_passed, self.max_score, list(x), file = f)
                elif self.args[2] == 5:
                    with open("results/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_2_links_with_delay", "a") as f:
                        print(self.comps, self.max_score, list(x), file = f)
            # with open("results/score_across_comparisons_GA_"+self.args[0]+"_1_vs_2links_2_timesteps_with_delay", "a") as f:
            #     print(self.comps, self.max_score, list(x), file = f)
            elif self.type == 2:
                with open("results/score_across_comparisons_GA_dc_vs_hb_2_timesteps", "a") as f:
                    print(self.comps, self.max_score, list(x), file = f)
            elif self.type == 4:
                with open("results/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[2]+"_2_timesteps_5_eval_multiflow_lcb", "a") as f:
                    print(self.comps, time_passed, self.max_score, list(x), file = f)
    
    def log(self, time_passed, x, score):
        if self.type == 6:
            with open("logs/score_across_comparisons_GA_"+self.args[0]+"_and_"+self.args[1]+"_vs_"+self.args[3]+"_2_timesteps_multiflow_picoquic", "a") as f:
                print(self.comps, score, list(x), file = f)
        elif self.type == 1:
            if self.args[2] == 6:
                with open("logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay", "a") as f:
                    print(self.comps, score, list(x), file = f)
            elif self.args[2] == 7:
                with open("t_coeff_0.5/logs/score_across_comparisons_BO_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_7200", "a") as f:
                    print(self.comps, time_passed, score, list(x), file = f)
            elif self.args[2] == 8:
                with open("t_coeff_0.5/logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_serial_"+str(self.args[1])+"_eval_median_iter_250", "a") as f:
                    print(self.comps, time_passed, score, list(x), file = f)
            elif self.args[2] == 5:
                with open("logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_2_links_with_delay", "a") as f:
                    print(self.comps, score, list(x), file = f)
        # with open("results/score_across_comparisons_GA_"+self.args[0]+"_1_vs_2links_2_timesteps_with_delay", "a") as f:
        #     print(self.comps, self.max_score, list(x), file = f)
        elif self.type == 2:
            with open("logs/score_across_comparisons_GA_dc_vs_hb_2_timesteps", "a") as f:
                print(self.comps, score, list(x), file = f)

    def run(self):
        space = [(int(self.lower_bound[i]), int(self.upper_bound[i]))
                 for i in range(self.trace_length)]

        # Handle initial population
        x0 = None
        if self.init_points is not None:
            x0 = [list(p) for p in self.init_points]

        res = forest_minimize(
            self._evaluate,
            space,
            n_calls=self.n_calls,
            x0=x0,
            random_state=self.seed,
            acq_func="LCB",          # better than default for exploration
            n_initial_points=25 if x0 is None else 0,
            n_jobs=-1
        )

        return res