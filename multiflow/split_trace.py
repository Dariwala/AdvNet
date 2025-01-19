def split(trace):
    trace, queue_length = trace[:-1], trace[-1]
    bandwidths = trace[:len(trace) // 3]
    latencies = trace[len(trace) // 3:2*len(trace) // 3]
    durations = trace[2 * len(trace) // 3:]

    return bandwidths, latencies, durations, queue_length

def split_mptcp(trace):
    trace, queue_length = trace[:-1], trace[-1]
    bandwidths_1 = trace[:len(trace) // 5]
    latencies_1 = trace[len(trace) // 5 : 2 * len(trace) // 5]
    bandwidths_2 = trace[2 * len(trace) // 5: 3 * len(trace) // 5]
    latencies_2 = trace[3 * len(trace) // 5 : 4 * len(trace) // 5]
    durations = trace[4 * len(trace) // 5:]

    return bandwidths_1, latencies_1, bandwidths_2, latencies_2, durations, queue_length