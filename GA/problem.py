from pymoo.core.problem import Problem, ElementwiseProblem
import numpy as np
import time

class CCProblem(ElementwiseProblem):
    def __init__(self, trace_length, lower_bound, upper_bound, evaluate, seed, start_time, total_time, type, *args, **kwargs):
        self.trace_length = trace_length
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)
        self.func = evaluate
        self.args = args
        self.seed = seed
        self.start_time = start_time
        self.total_time = total_time
        self.max_score = -np.inf
        self.max_score_vs_time = []
        self.type = type
        super().__init__(n_var=trace_length, n_obj=1, n_ieq_constr=0, n_eq_constr = 0, xl=lower_bound, xu=upper_bound, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        time_passed = time.perf_counter() - self.start_time

        if time_passed < self.total_time:
            if self.type == 0:
                score = self.func(list(x), self.args[0], self.args[1], fuzzing = self.args[2])
            elif self.type == 1:
                score = self.func(list(x), self.args[0], self.args[1], self.args[2], self.args[3])
            elif self.type == 2:
                score = self.func(list(x), self.args[0])
            out["F"] = - score
            if score > self.max_score:
                self.max_score = score
                self.max_score_vs_time.append([time.perf_counter() - self.start_time, self.max_score])
            if score > 0:
                print(list(x), score)
        else:
            out["F"] = - self.max_score
    
    def save(self):
        if self.type == 0:
            if self.args[2]:
                method = "fuzz"
            else:
                method = "advnet"
        elif self.type == 1:
            method = "mptcp_type_"+str(self.args[2])
        import pickle
        with open("results/score_across_time_GA_"+self.args[0]+"_"+str(self.seed)+"_"+str(self.trace_length)+"_trace_length_" + method, "wb") as f:
            pickle.dump(self.max_score_vs_time, f)