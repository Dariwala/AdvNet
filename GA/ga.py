from pymoo.algorithms.soo.nonconvex.ga import GA
from pymoo.termination import get_termination
from pymoo.optimize import minimize
from pymoo.operators.sampling.rnd import IntegerRandomSampling
from pymoo.operators.crossover.pntx import TwoPointCrossover
from GA.mutation import UniformMutation
import random
import numpy as np

class AdvNetGA():
    """Genetic-algorithm search over network traces, wrapping pymoo's ``GA``.

    Uses two-point crossover and the integer :class:`UniformMutation` operator.
    If no initial population is supplied, one is drawn uniformly within the
    problem's per-dimension bounds.
    """

    def __init__(self, problem, pop_size, seed, n_iter, individuals=None):
        """Args:
            problem: A :class:`CCProblem` instance defining the search space.
            pop_size: Number of individuals per generation.
            seed: Random seed for reproducible sampling and optimization.
            n_iter: Termination budget, in number of evaluations (``n_eval``).
            individuals: Optional initial population; sampled if ``None``.
        """
        self.problem = problem
        self.pop_size = pop_size
        self.seed = seed
        self.generator = random.Random(self.seed)
        if individuals is None:
            individuals = self.sampling()

        self.algorithm = GA(sampling=individuals, pop_size=self.pop_size, eliminate_duplicates=True, crossover=TwoPointCrossover(), mutation=UniformMutation())
        self.termination = get_termination("n_eval", n_iter)
        self.individuals = individuals

    def sampling(self):
        """Draw ``pop_size`` random traces within the problem's bounds."""
        individuals = []
        for _ in range(self.pop_size):
            trace = []
            for j in range(self.problem.trace_length):
                trace.append(self.generator.randint(self.problem.lower_bound[j], self.problem.upper_bound[j]))
            individuals.append(trace)

        return np.array(individuals)

    def run(self):
        """Run the optimization and return pymoo's result object."""
        return minimize(self.problem, self.algorithm, self.termination, seed=self.seed, save_history=False, verbose=False, X=self.individuals)