import numpy as np
import time
import random


class AdvNetEpsGreedy():
    def __init__(self, trace_length, lower_bound, upper_bound,
                 evaluate, type,
                 n_calls, seed,
                 start_time, total_time,
                 init_points=None,
                 epsilon=0.3,
                 elite_size=10,
                 *args):

        self.trace_length = trace_length
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)

        self.func = evaluate
        self.args = args
        self.type = type

        self.n_calls = n_calls
        self.seed = seed
        self.rng = random.Random(seed)

        self.start_time = start_time
        self.total_time = total_time

        self.init_points = init_points

        # Bandit params
        self.epsilon = epsilon
        self.elite_size = elite_size

        # Tracking (same as GA/BO)
        self.max_score = -np.inf
        self.best_x = None
        self.comps = 0

        # Memory (important!)
        self.elite = []

    # ----------------------------
    # Sampling
    # ----------------------------
    def _random_sample(self):
        return [
            self.rng.randint(self.lower_bound[i], self.upper_bound[i])
            for i in range(self.trace_length)
        ]

    def _mutate(self, x):
        """Mutate a full trace"""
        x_new = x.copy()
        for i in range(self.trace_length):
            if self.rng.random() < 0.1:  # mutation prob
                x_new[i] = self.rng.randint(self.lower_bound[i], self.upper_bound[i])
        return x_new

    def _sample(self):
        if len(self.elite) == 0 or self.rng.random() < self.epsilon:
            return self._random_sample()   # explore
        else:
            parent = self.rng.choice(self.elite)
            return self._mutate(parent)    # exploit

    # ----------------------------
    # Evaluation (same as BO)
    # ----------------------------
    def _evaluate(self, x):
        time_passed = time.perf_counter() - self.start_time

        if time_passed > self.total_time:
            return

        self.comps += 1

        if self.type == 0:
            score = self.func(list(x), self.args[0], self.args[1], fuzzing=self.args[2])
        elif self.type == 1:
            score = self.func(list(x), self.args[0], self.args[1],
                              self.args[2], self.args[3], self.args[4])
        elif self.type == 2:
            score = self.func(list(x), self.args[0])
        elif self.type == 3:
            score = self.func(list(x), self.args[0], self.args[1],
                              self.args[2], self.args[3])
        elif self.type == 4:
            score = self.func(list(x), self.args[0],
                              self.args[1], self.args[2])
        elif self.type == 5:
            score = self.func(list(x), self.args[0],
                              self.args[1], self.args[2])
        elif self.type == 6:
            score = self.func(list(x), self.args[0],
                              self.args[1], self.args[2], self.args[3])
        else:
            raise ValueError("Unknown type")

        self.update_max_score(time_passed, x, score)
        self.log(time_passed, x, score)

    # ----------------------------
    # Tracking (copied from BO, minor rename)
    # ----------------------------
    def update_max_score(self, time_passed, x, score):
        if score > self.max_score:
            self.max_score = score
            self.best_x = x

            # maintain elite set
            self.elite.append(x)
            if len(self.elite) > self.elite_size:
                self.elite.pop(0)

            # ---- SAME LOGIC AS BO (just rename BO) ----
            if self.type == 1 and self.args[2] == 7:
                with open("t_coeff_1/score_across_comparisons_EPS_" +
                          self.args[0] + "_vs_" + self.args[4] +
                          "_2_timesteps_with_delay_parallel_" +
                          str(self.args[1]) + "_eval_median_time_7200", "a") as f:
                    print(self.comps, time_passed, self.max_score, list(x), file=f)

    def log(self, time_passed, x, score):
        if self.type == 1 and self.args[2] == 7:
            with open("t_coeff_1/logs/score_across_comparisons_EPS_" +
                      self.args[0] + "_vs_" + self.args[4] +
                      "_2_timesteps_with_delay_parallel_" +
                      str(self.args[1]) + "_eval_median_time_7200", "a") as f:
                print(self.comps, time_passed, score, list(x), file=f)

    # ----------------------------
    # Main loop
    # ----------------------------
    def run(self):
        evaluations = 0

        # Evaluate initial points first (like GA/BO)
        if self.init_points is not None:
            for p in self.init_points:
                self._evaluate(list(p))
                evaluations += 1

        # Main ε-greedy loop
        while evaluations < self.n_calls:
            x = self._sample()
            self._evaluate(x)

            evaluations += 1

            if time.perf_counter() - self.start_time > self.total_time:
                break

        return {
            "best_x": self.best_x,
            "best_score": self.max_score,
            "evaluations": self.comps
        }