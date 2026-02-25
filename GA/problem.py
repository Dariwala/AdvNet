from pymoo.core.problem import Problem, ElementwiseProblem
import numpy as np
import time

class CCProblem(ElementwiseProblem):
    def __init__(self, trace_length, lower_bound, upper_bound, evaluate, seed, start_time, total_time, type, pop = None, *args, **kwargs):
        self.trace_length = trace_length
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)
        self.func = evaluate
        self.args = args
        self.seed = seed
        self.start_time = start_time
        self.total_time = total_time
        self.max_score = -np.inf ##
        self.max_score_vs_time = []
        self.type = type
        self.comps = 0
        self.pop = pop
        # self.args = self.args[0:1] + (1,) + self.args[2:]
        super().__init__(n_var=trace_length, n_obj=1, n_ieq_constr=0, n_eq_constr = 0, xl=lower_bound, xu=upper_bound, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        time_passed = time.perf_counter() - self.start_time
        is_in_init_pop = False
        if self.pop is not None:
            for p in self.pop:
                if np.all(np.isclose(x, p.X)):
                    out["F"] = -p.F
                    score = -out["F"]
                    is_in_init_pop = True
                    break
        if not is_in_init_pop:

            # if time_passed > self.total_time * 0.5:
            #     self.args = self.args[0:1] + (1,) + self.args[2:]

            if time_passed < self.total_time:
                self.comps += 1
                if self.type == 0:
                    score = self.func(list(x), self.args[0], self.args[1], fuzzing = self.args[2])
                elif self.type == 1:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2], self.args[3], self.args[4])
                elif self.type == 2:
                    score = self.func(list(x), self.args[0])
                elif self.type == 3:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2], self.args[3])
                elif self.type == 4:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2])
                elif self.type == 5:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2])
                elif self.type == 6:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2], self.args[3])
                out["F"] =  -score##
            else:
                score = self.max_score
                out["F"] = -self.max_score
        self.update_max_score(time_passed, x, score)
        self.log(time_passed, x, score)
        # if True:
        #     with open("patterns/UC2_"+self.args[0]+"_"+self.args[4] + "_" + str((len(list(x))-1)//5)+"_timesteps_delay_coeff", "a") as f:
        #         print(list(x), score, file = f)
        # else:
        #     out["F"] = -self.max_score##
    
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
                    with open("t_coeff_0.5/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_7200", "a") as f:
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
                with open("t_coeff_0.5/logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_7200", "a") as f:
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
    
    def save(self):
        if self.type == 0:
            if self.args[2]:
                method = "fuzzing"
            else:
                method = "advnet"
        elif self.type == 1:
            method = "mptcp_type_"+str(self.args[2])
        # import pickle
        # with open("results/score_across_time_ga_"+self.args[0]+"_"+str(self.seed)+"_"+str(self.trace_length)+"_trace_length_" + method, "wb") as f:
        #     pickle.dump(self.max_score_vs_time, f)