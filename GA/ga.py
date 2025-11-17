from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.pntx import TwoPointCrossover
from GA.mutation import UniformMutation

class AdvNetGA():
    def __init__(self, problem, pop_size, seed, n_iter, individuals = None):
        self.problem = problem
        self.pop_size = pop_size
        self.seed = seed
        if individuals is None:
            self.algorithm = GA(sampling = IntegerRandomSampling(), pop_size=self.pop_size, eliminate_duplicates=True, crossover = TwoPointCrossover(), mutation = UniformMutation())
        else:
            self.algorithm = GA(sampling = individuals, pop_size=self.pop_size, eliminate_duplicates=True, crossover = TwoPointCrossover(), mutation = UniformMutation())
        self.termination = get_termination("n_eval", n_iter)
        self.individuals = individuals

    def run(self):
        if self.individuals is None:
            res = minimize(self.problem, self.algorithm, self.termination, seed=self.seed, save_history=False, verbose=False)
        else:
            res = minimize(self.problem, self.algorithm, self.termination, seed=self.seed, save_history=False, verbose=False, X = self.individuals)
        return res