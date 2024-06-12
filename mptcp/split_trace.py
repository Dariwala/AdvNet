def split_trace(trace):
    len_trace = len(trace)
    
    bandwidths_1 = trace[:(len_trace // 6)]
    latencies_1 = trace[(len_trace // 6): 2 * (len_trace // 6)]
    durations_1 = trace[2 * (len_trace // 6): 3 * (len_trace // 6)]

    bandwidths_2 = trace[3 * (len_trace // 6) : 4 * (len_trace // 6)]
    latencies_2 = trace[4 * (len_trace // 6): 5 * (len_trace // 6)]
    durations_2 = trace[5 * (len_trace // 6):]

    return bandwidths_1, latencies_1, durations_1, bandwidths_2, latencies_2, durations_2

def split_trace_simplify(trace, index):
    left_trace = trace[:index]
    right_trace = trace[index:]

    bandwidths_1 = left_trace[:(len(left_trace) // 3)]
    latencies_1 = left_trace[(len(left_trace) // 3): 2 * (len(left_trace) // 3)]
    durations_1 = left_trace[2 * (len(left_trace) // 3): 3 * (len(left_trace) // 3)]

    bandwidths_2 = right_trace[:(len(right_trace) // 3)]
    latencies_2 = right_trace[(len(right_trace) // 3): 2 * (len(right_trace) // 3)]
    durations_2 = right_trace[2 * (len(right_trace) // 3): 3 * (len(right_trace) // 3)]

    return bandwidths_1, latencies_1, durations_1, bandwidths_2, latencies_2, durations_2