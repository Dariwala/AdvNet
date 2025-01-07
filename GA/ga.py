from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.pntx import TwoPointCrossover
from GA.mutation import UniformMutation

class AdvNetGA():
    def __init__(self, problem, pop_size, seed, n_iter):
        self.problem = problem
        self.pop_size = pop_size
        self.seed = seed
        self.algorithm = GA(sampling = IntegerRandomSampling(), pop_size=self.pop_size, eliminate_duplicates=True, crossover = TwoPointCrossover(), mutation = UniformMutation())
        self.termination = get_termination("n_eval", n_iter)

    def run(self):
        res = minimize(self.problem, self.algorithm, self.termination, seed=self.seed, save_history=False, verbose=False)
        return res