from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.pntx import TwoPointCrossover
from GA.mutation import UniformMutation
import random
import numpy as np

class AdvNetGA():
    def __init__(self, problem, pop_size, seed, n_iter, individuals = None):
        self.problem = problem
        self.pop_size = pop_size
        self.seed = seed
        self.generator = random.Random(self.seed)
        if individuals is None:
            individuals = self.sampling()
            
        self.algorithm = GA(sampling = individuals, pop_size=self.pop_size, eliminate_duplicates=True, crossover = TwoPointCrossover(), mutation = UniformMutation())
        self.termination = get_termination("n_eval", n_iter)
        self.individuals = individuals
    
    def sampling(self):
        individuals = []
        for i in range(self.pop_size):
            trace = []

            for i in range(self.problem.trace_length):
                trace.append(self.generator.randint(self.problem.lower_bound[i], self.problem.upper_bound[i]))

            individuals.append(trace)

        return np.array(individuals)

    def run(self):
        if self.individuals is None:
            res = minimize(self.problem, self.algorithm, self.termination, seed=self.seed, save_history=False, verbose=False)
        else:
            res = minimize(self.problem, self.algorithm, self.termination, seed=self.seed, save_history=False, verbose=False, X = self.individuals)
        return res