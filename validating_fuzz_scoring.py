import random
from Simplify.single_cc_simplify import SingleCCSimplify
from Simplify.pdo_simplify import PDOSimplify
from utils.generate_bandwidth_trace import create_trace
import scipy.stats as stats

if __name__ == "__main__":
    advnet_scores = []
    pdo_scores = []
    rnd = random.Random(1)
    for timestep in range(2, 6):
        for _ in range(1):
            bandwidths = [rnd.randint(1000, 4000) for _ in range(timestep)]
            latencies = [rnd.randint(5, 20) for _ in range(timestep)]
            durations = [rnd.randint(1000, 3000) for _ in range(timestep)]

            pdos = create_trace(bandwidths, durations, False)

            trace = bandwidths + latencies + durations
            print(trace)
            single_cc_simplify = SingleCCSimplify(trace, 0.1, 0.1, "cubic")
            pdo_simplify = PDOSimplify(pdos, 0.1, 0.1, "cubic")

            advnet_score, pdo_score = single_cc_simplify.compute_score(trace), pdo_simplify.compute_score(pdos)
            print(advnet_score, pdo_score)

            advnet_scores.append(advnet_score)
            pdo_scores.append(pdo_score)
        break
    # pearson_corr, _ = stats.pearsonr(advnet_scores, pdo_scores)
    # print('Pearson correlation:', pearson_corr)