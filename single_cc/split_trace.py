def split_trace(trace):
    queue_length = trace[-1]

    len_trace = len(trace) - 1
    
    bandwidths = trace[:(len_trace // 3)]
    latencies = trace[(len_trace // 3): 2 * (len_trace // 3)]
    durations = trace[2 * (len_trace // 3): len_trace]

    return bandwidths, latencies, durations, queue_length