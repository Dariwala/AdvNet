def split_trace(trace):
    len_trace = len(trace)
    
    bandwidths = trace[:(len_trace // 3)]
    latencies = trace[(len_trace // 3): 2 * (len_trace // 3)]
    durations = trace[2 * (len_trace // 3):]

    return bandwidths, latencies, durations