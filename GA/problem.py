"""pymoo problem definition for adversarial trace search.

:class:`CCProblem` adapts a domain-specific evaluation function into a pymoo
single-objective minimization problem. Because pymoo minimizes, the objective
is stored as ``-score`` (AdvNet maximizes the adversarial score). The class also
tracks the best score over time and logs the search progress.

The ``type`` argument selects which evaluation domain is active; the extra
positional ``*args`` are forwarded to the evaluation function and their meaning
is domain-specific (see the dispatch in ``search_adv_traces.py``).
"""

import os
import time

import numpy as np
from pymoo.core.problem import ElementwiseProblem


class CCProblem(ElementwiseProblem):
    """Single-objective problem wrapping a congestion-control evaluation."""

    def __init__(self, trace_length, lower_bound, upper_bound, evaluate, seed, start_time, total_time, type, pop=None, *args, **kwargs):
        """Args:
            trace_length: Number of decision variables (trace length).
            lower_bound / upper_bound: Per-dimension integer bounds.
            evaluate: Domain evaluation function returning a scalar score.
            seed: Random seed (kept for reproducibility/bookkeeping).
            start_time: ``time.perf_counter()`` reference for the time budget.
            total_time: Search time budget in seconds.
            type: Domain selector (see module docstring).
            pop: Optional warm-start population (pymoo ``Population``).
            *args: Extra, domain-specific arguments forwarded to ``evaluate``.
        """
        self.trace_length = trace_length
        self.lower_bound = np.array(lower_bound)
        self.upper_bound = np.array(upper_bound)
        self.func = evaluate
        self.args = args
        self.seed = seed
        self.start_time = start_time
        self.total_time = total_time
        self.max_score = -np.inf
        self.max_score_vs_time = []
        self.type = type
        self.comps = 0
        self.pop = pop
        super().__init__(n_var=trace_length, n_obj=1, n_ieq_constr=0, n_eq_constr=0, xl=lower_bound, xu=upper_bound, **kwargs)

    def _evaluate(self, x, out, *args, **kwargs):
        """Evaluate one trace ``x`` and store ``-score`` in ``out["F"]``.

        Reuses the cached objective for individuals already present in the
        warm-start population, stops evaluating once the time budget is spent
        (falling back to the best score seen), and otherwise dispatches to the
        domain evaluation function selected by ``self.type``.
        """
        time_passed = time.perf_counter() - self.start_time
        is_in_init_pop = False
        if self.pop is not None:
            for p in self.pop:
                if np.all(np.isclose(x, p.X)):
                    out["F"] = -p.F
                    score = -out["F"]
                    is_in_init_pop = True
                    break
        if not is_in_init_pop:
            if time_passed < self.total_time:
                self.comps += 1
                if self.type == 0:
                    score = self.func(list(x), self.args[0], self.args[1], fuzzing = self.args[2])
                elif self.type == 1:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2], self.args[3], self.args[4])
                elif self.type == 2:
                    score = self.func(list(x), self.args[0])
                elif self.type == 3:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2], self.args[3])
                elif self.type == 4:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2])
                elif self.type == 5:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2])
                elif self.type == 6:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2], self.args[3])
                elif self.type == 7:
                    score = self.func(list(x), self.args[0], self.args[1], False)
                elif self.type == 8:
                    score = self.func(list(x), self.args[0], self.args[1], self.args[2])
                out["F"] = -score
                self.update_max_score(time_passed, x, score)
                self.log(time_passed, x, score)
            else:
                score = self.max_score
                out["F"] = -self.max_score

    @staticmethod
    def _append(path, *values):
        """Append a space-separated record to ``path``, creating dirs as needed."""
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "a") as f:
            print(*values, file=f)

    def update_max_score(self, time_passed, x, score):
        """Record the best trace so far, writing it to the per-domain results file."""
        if score > self.max_score:
            self.max_score = score
            if self.type == 6:
                self._append("results/score_across_comparisons_GA_"+self.args[0]+"_and_"+self.args[1]+"_vs_"+self.args[3]+"_2_timesteps_multiflow_picoquic", self.comps, self.max_score, list(x))
            elif self.type == 1:
                if self.args[2] == 6:
                    self._append("results/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay", self.comps, self.max_score, list(x))
                elif self.args[2] == 7:
                    self._append("t_coeff_0.5/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_7200", self.comps, time_passed, self.max_score, list(x))
                elif self.args[2] == 8:
                    self._append("t_coeff_0.5/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_serial_"+str(self.args[1])+"_eval_median_iter_250", self.comps, time_passed, self.max_score, list(x))
                elif self.args[2] == 5:
                    self._append("results/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_2_links_with_delay", self.comps, self.max_score, list(x))
            elif self.type == 2:
                self._append("results/score_across_comparisons_GA_dc_vs_hb_2_timesteps", self.comps, self.max_score, list(x))
            elif self.type == 4:
                self._append("results/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[2]+"_2_timesteps_5_eval_multiflow_lcb", self.comps, time_passed, self.max_score, list(x))
            elif self.type == 7:
                self._append("0.4_0.4_0.2/score_across_comparisons_NS3_GA_"+self.args[0]+"_vs_"+self.args[1]+"_2_timesteps_with_delay", self.comps, self.max_score, list(x))
            elif self.type == 8:
                self._append("cache_results/score_across_comparisons_cache_GA_"+self.args[0]+"_vs_"+self.args[1]+"_"+str(self.args[2]), self.comps, time_passed, self.max_score, list(x))

    def log(self, time_passed, x, score):
        """Log every evaluated trace to the per-domain log file."""
        if self.type == 6:
            self._append("logs/score_across_comparisons_GA_"+self.args[0]+"_and_"+self.args[1]+"_vs_"+self.args[3]+"_2_timesteps_multiflow_picoquic", self.comps, score, list(x))
        elif self.type == 1:
            if self.args[2] == 6:
                self._append("logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay", self.comps, score, list(x))
            elif self.args[2] == 7:
<<<<<<< Updated upstream
                self._append("t_coeff_0.5/logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_7200", self.comps, time_passed, score, list(x))
=======
                with open("t_coeff_1/logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_parallel_"+str(self.args[1])+"_eval_median_time_7200", "a") as f:
                    print(self.comps, time_passed, score, list(x), file = f)
>>>>>>> Stashed changes
            elif self.args[2] == 8:
                self._append("t_coeff_0.5/logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_with_delay_serial_"+str(self.args[1])+"_eval_median_iter_250", self.comps, time_passed, score, list(x))
            elif self.args[2] == 5:
                self._append("logs/score_across_comparisons_GA_"+self.args[0]+"_vs_"+self.args[4]+"_2_timesteps_2_links_with_delay", self.comps, score, list(x))
        elif self.type == 2:
            self._append("logs/score_across_comparisons_GA_dc_vs_hb_2_timesteps", self.comps, score, list(x))
        elif self.type == 7:
            self._append("0.4_0.4_0.2/logs/score_across_comparisons_NS3_GA_"+self.args[0]+"_vs_"+self.args[1]+"_2_timesteps_with_delay", self.comps, score, list(x))
        elif self.type == 8:
            self._append("cache_results/logs/score_across_comparisons_cache_GA_"+self.args[0]+"_vs_"+self.args[1]+"_"+str(self.args[2]), self.comps, score, list(x))

    def save(self):
        """Placeholder hook for persisting the best-score history.

        The history is available in ``self.max_score_vs_time``; persisting it is
        currently a no-op. Retained for callers that invoke ``problem.save()``.
        """
        return
