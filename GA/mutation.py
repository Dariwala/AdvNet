from pymoo.core.mutation import Mutation
import random


class UniformMutation(Mutation):
    """Per-gene uniform mutation operator for integer-encoded traces.

    With probability ``prob`` each gene is independently resampled uniformly
    from its variable bounds ``[problem.xl[j], problem.xu[j]]``. This integer
    resampling matches AdvNet's discrete trace representation.
    """

    def __init__(self, prob: float = 0.2):
        """Args:
            prob: Per-gene probability of resampling a value (default 0.2).
        """
        super().__init__()
        self.prob = prob

    def _do(self, problem, X, **kwargs):
        """Mutate the population ``X`` in place and return it."""
        for i in range(len(X)):  # each individual
            for j in range(len(X[i])):  # each gene
                if random.random() < self.prob:
                    X[i][j] = random.randint(int(problem.xl[j]), int(problem.xu[j]))

        return X