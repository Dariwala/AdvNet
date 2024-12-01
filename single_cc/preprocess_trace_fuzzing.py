def preprocess_trace_fuzzing(trace):
    for i in range(1, len(trace)):
        trace[i] += trace[i-1]
    return trace, 2 * trace[-1]