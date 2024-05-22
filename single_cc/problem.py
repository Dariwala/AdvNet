from pymoo.core.problem import Problem, ElementwiseProblem
import numpy as np
import time

class SingleCCProblem(ElementwiseProblem):
    def __init__(self, trace_length, lower_bound, upper_bound, ref, n_evals, evaluate, seed, fuzzing, start_time, total_time, **kwargs):
        self.trace_length = trace_length
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)
        self.ref = ref
        self.n_evals = n_evals
        self.func = evaluate
        self.fuzzing = fuzzing
        self.seed = seed
        self.start_time = start_time
        self.total_time = total_time
        self.max_score = -np.inf
        self.max_score_vs_time = []
        super().__init__(n_var=trace_length, n_obj=1, n_ieq_constr=0, n_eq_constr = 0, xl=lower_bound, xu=upper_bound, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        time_passed = time.perf_counter() - self.start_time

        if time_passed < self.total_time:
            score = self.func(list(x), self.ref, self.n_evals, fuzzing = self.fuzzing)
            out["F"] = - score
            if score > self.max_score:
                self.max_score = score
                self.max_score_vs_time.append([time.perf_counter() - self.start_time, self.max_score])
        else:
            out["F"] = - self.max_score
    
    def save(self):
        if self.fuzzing:
            method = "fuzz"
        else:
            method = "advnet"
        import pickle
        with open("results/score_across_time_GA_"+self.ref+"_"+str(self.seed)+"_"+str(self.trace_length)+"_timesteps_" + method, "wb") as f:
            pickle.dump(self.max_score_vs_time, f)