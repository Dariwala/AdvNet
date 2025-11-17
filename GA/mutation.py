from pymoo.core.mutation import Mutation
import random

class UniformMutation(Mutation):
    def __init__(self, prob = 0.2):
        super().__init__()
        self.prob = prob

    def _do(self, problem, X, **kwargs):
        # for each individual
        for i in range(len(X)):
            for j in range(len(X[i])):
                r = random.random()

                if r < self.prob:
                    new_value = random.randint(int(problem.xl[j]), int(problem.xu[j]))
                    X[i][j] = new_value

        return X