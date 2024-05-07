from pymoo.core.problem import Problem, ElementwiseProblem
import numpy as np

class SingleCCProblem(ElementwiseProblem):
    def __init__(self, trace_length, lower_bound, upper_bound, ref, n_evals, evaluate, fuzzing, **kwargs):
        self.trace_length = trace_length
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)
        self.ref = ref
        self.n_evals = n_evals
        self.func = evaluate
        self.fuzzing = fuzzing
        super().__init__(n_var=trace_length, n_obj=1, n_ieq_constr=0, n_eq_constr = 0, xl=lower_bound, xu=upper_bound, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        score = self.func(list(x), self.ref, self.n_evals, fuzzing = self.fuzzing)
        out["F"] = - score