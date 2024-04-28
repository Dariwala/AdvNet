from skopt import gp_minimize

class AdvNetBO():
    def __init__(self, trace_length, l_bound, u_bound, evaluate, n_evals, ref, seed):
        self.trace_length = trace_length
        self.l_bound = l_bound
        self.u_bound = u_bound
        self.func = evaluate
        self.n_evals = n_evals
        self.ref = ref
        self.seed = seed
    
    def _evaluate(self, trace):
        score = self.func(trace, self.ref, self.n_evals)
        return -score
    
    def run(self, n_calls):
        res = gp_minimize(self._evaluate,
                  [(self.l_bound[i], self.u_bound[i]) for i in range(self.trace_length)],
                  n_calls=n_calls,
                  random_state=self.seed,
                  acq_optimizer = "auto",
                  n_jobs = -1)
        return res
