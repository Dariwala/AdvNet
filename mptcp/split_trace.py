def split_trace(trace):
    len_trace = len(trace)
    
    bandwidths_1 = trace[:(len_trace // 6)]
    latencies_1 = trace[(len_trace // 6): 2 * (len_trace // 6)]
    durations_1 = trace[2 * (len_trace // 6): 3 * (len_trace // 6)]

    bandwidths_2 = trace[3 * (len_trace // 6) : 4 * (len_trace // 6)]
    latencies_2 = trace[4 * (len_trace // 6): 5 * (len_trace // 6)]
    durations_2 = trace[5 * (len_trace // 6):]

    return bandwidths_1, latencies_1, durations_1, bandwidths_2, latencies_2, durations_2