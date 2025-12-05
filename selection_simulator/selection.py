import time
from typing import Callable
from mptcp.evaluate import evaluate


def run_test(
    time_budget: int,
    selection_function: Callable[[list, int], list],
    traces
) -> float:
    # 2. Pass variables and S to the selection function
    # The selection function is expected to use the budget S by calling sample()
    best_trace, best_score = selection_function(traces, time_budget)
    
    with open(output_filename, 'a') as f:
        f.write(f"1 {time_budget} {best_score} {best_trace}\n")

class SampledRV:
    def __init__(self, trace):
        self._trace = trace
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0  # sum of squared deviations

    def take_sample(self):
        x = evaluate(self._trace, ref, 1, 8, "5", tar, False)
        self.n += 1

        # Incremental mean and variance (Welford)
        delta = x - self.mean
        self.mean += delta / self.n
        delta2 = x - self.mean
        self.M2 += delta * delta2

    def get_sample_mean(self):
        return self.mean

    def get_sample_variance(self):
        if self.n < 2:
            return float("inf")
        return self.M2 / (self.n - 1)

    def get_n(self):
        return self.n


def mst_selector(
    traces, 
    time_budget: int
):
    """
    Selects the best RV using a multi-stage tournament
    """
    n = len(traces)
    srv = [SampledRV(traces[i]) for i in range(n)]
    start_time = time.perf_counter()
    round_size = n
    
    while time.perf_counter() - start_time < time_budget:
        for i in range(round_size):
            srv[i].take_sample()
            if time.perf_counter() - start_time >= time_budget:
                break
        
        # Re-sort
        srv = sorted(
            srv, 
            key=lambda rv: rv.get_sample_mean(), 
            reverse=True
        )
        
        # Eliminate
        round_size = max(5, int(round_size * 0.5))
    
    return srv[0]._trace, srv[0].get_sample_mean()

def wtm_selector(
    traces,
    time_budget: int,
):
    n = len(traces)
    srv = [SampledRV(traces[i]) for i in range(n)]
    start_time = time.perf_counter()

    i = 0
    while i < n and (time.perf_counter() - start_time) < time_budget:
        srv[i].take_sample()
        i += 1

    # ---- 2. Tournament elimination (MST-like) ----
    while len(srv) > 4 and time.perf_counter() - start_time < time_budget:
        k = len(srv)
        
        for i in range(k):
            if time.perf_counter() - start_time >= time_budget:
                break
            srv[i].take_sample()

        # Sort and eliminate bottom fraction
        srv.sort(key=lambda rv: rv.get_sample_mean(), reverse=True)
        survivors = max(4, int(k * 0.5))
        srv = srv[:survivors]

    # ---- 3. Top-two focused phase ----
    # Now only a few arms remain (≤ 4). We spend the rest of the budget
    # mostly on the best two arms, but never exceed `budget`.
    while time.perf_counter() - start_time < time_budget:
        # Re-rank
        srv.sort(key=lambda rv: rv.get_sample_mean(), reverse=True)
        k = len(srv)
        if k == 1:
            break

        best = srv[0]
        second = srv[1]

        best.take_sample()
        
        if time.perf_counter() - start_time >= time_budget:
            break
        second.take_sample()

        # 3.3 Occasional exploration for remaining arms
        for other in srv[2:]:
            if time.perf_counter() - start_time >= time_budget:
                break
            other.take_sample()

        # Loop repeats, recomputes best/second with updated means

    # Final winner
    srv.sort(key=lambda rv: rv.get_sample_mean(), reverse=True)
    return srv[0]._trace, srv[0].get_sample_mean()

def extract_top_K_traces(filename, max_time, pop_size):
    import ast
    import numpy as np
    """
    Reads a file and returns the top `pop_size` individuals (decision variables)
    with the highest scores, filtering by maximum time.
    
    Parameters:
        filename (str): Path to the file.
        max_time (float): Maximum allowed time for filtering.
        pop_size (int): Number of top individuals to return.
    
    Returns:
        top_X (np.ndarray): Array of top individuals (shape: pop_size x n_vars)
        top_scores (np.ndarray): Array of their corresponding scores
    """
    individuals = []
    scores = []

    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split(maxsplit=3)
            if len(parts) < 4:
                continue
            time = float(parts[1])
            score = float(parts[2])
            if time > max_time:
                break
            # convert string representation of list to actual list
            ind = ast.literal_eval(parts[3])
            individuals.append(ind)
            scores.append(score)

    if not individuals:
        return []

    # Convert to numpy arrays
    individuals = np.array(individuals)
    # Get indices of top scores (higher is better)
    top_indices = np.argsort(scores)[-pop_size:][::-1]  # descending order

    top_X = individuals[top_indices].tolist()

    return top_X


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiment with CC protocols.")

    parser.add_argument("--ref", type=str, default="cubic",
                        help="Reference congestion control protocol")
    parser.add_argument("--tar", type=str, default="bbr",
                        help="Target congestion control protocol")
    parser.add_argument("--time_pct", type=float, default=0.1,
                        help="Time percentage cutoff")
    args = parser.parse_args()

    ref = args.ref
    tar = args.tar
    time_pct = args.time_pct
    file_name = "t_coeff_0.5/logs/score_across_comparisons_GA_"+ref+"_vs_"+tar+"_2_timesteps_with_delay_parallel_5_eval_median_iter_250"
    output_filename = "t_coeff_0.5/score_across_comparisons_GA_"+ref+"_vs_"+tar+"_2_timesteps_with_delay_parallel_5_eval_median_iter_250_selection_mst_"+str(time_pct)

    time_budget = int(3600 * time_pct)
    traces = extract_top_K_traces(file_name, 3600 - time_budget, 25)
    # print(traces[0])
    run_test(time_budget, mst_selector, traces)