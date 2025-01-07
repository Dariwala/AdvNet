def split(trace):
    trace, queue_length = trace[:-1], trace[-1]
    bandwidths = trace[:len(trace) // 3]
    latencies = trace[len(trace) // 3:2*len(trace) // 3]
    durations = trace[2 * len(trace) // 3:]

    return bandwidths, latencies, durations, queue_length