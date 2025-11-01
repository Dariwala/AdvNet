import statistics
import numpy as np

class NoiseHandler:
    def mean(self, values):
        return sum(values) / len(values)
    def median(self, values):
        return statistics.median(values)
    def trimmed_mean(self, values, pct=20):
        trim_len = len(values) * pct // 100
        trimmed_values = values[trim_len:-trim_len]
        return sum(trimmed_values) / len(trimmed_values) 
    def lcb(self, values, lam=2):
        if len(values) == 1:
            return values[0]
        samples = np.array(values, dtype=float)
        mean = np.mean(samples)
        std = np.std(samples, ddof=1)  # sample standard deviation
        n = len(samples)
        return mean - lam * (std / np.sqrt(n))
    def max(self, values):
        max_index, max_value = max(enumerate(values), key=lambda x: x[1])
        return max_value, max_index

