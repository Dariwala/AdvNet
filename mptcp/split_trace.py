def extract_queue_length(trace):
    return trace[-1], trace[:-1]

def split_trace(trace, mptcp_type = -1):
    if mptcp_type != 6 and mptcp_type != 7 and mptcp_type != 8:
        queue_length, trace = extract_queue_length(trace)
        len_trace = len(trace)
        
        bandwidths_1 = trace[:(len_trace // 5)]
        latencies_1 = trace[(len_trace // 5): 2 * (len_trace // 5)]
        bandwidths_2 = trace[2 * (len_trace // 5): 3 * (len_trace // 5)]

        latencies_2 = trace[3 * (len_trace // 5) : 4 * (len_trace // 5)]
        durations = trace[4 * (len_trace // 5):]

        return bandwidths_1, latencies_1, durations, bandwidths_2, latencies_2, queue_length
    elif mptcp_type == 6 or mptcp_type == 7 or mptcp_type == 8:
        queue_length, trace = extract_queue_length(trace)
        len_trace = len(trace)
        
        bandwidths_1 = trace[:(len_trace // 3)]
        latencies_1 = trace[(len_trace // 3): 2 * (len_trace // 3)]
        durations = trace[2 * (len_trace // 3):]

        return bandwidths_1, latencies_1, durations, [], [], queue_length

def split_trace_simplify(trace, index):
    queue_length, trace = extract_queue_length(trace)
    left_trace = trace[:index]
    right_trace = trace[index:]

    bandwidths_1 = left_trace[:(len(left_trace) // 3)]
    latencies_1 = left_trace[(len(left_trace) // 3): 2 * (len(left_trace) // 3)]
    durations_1 = left_trace[2 * (len(left_trace) // 3): 3 * (len(left_trace) // 3)]

    bandwidths_2 = right_trace[:(len(right_trace) // 3)]
    latencies_2 = right_trace[(len(right_trace) // 3): 2 * (len(right_trace) // 3)]
    durations_2 = right_trace[2 * (len(right_trace) // 3): 3 * (len(right_trace) // 3)]

    return bandwidths_1, latencies_1, durations_1, bandwidths_2, latencies_2, durations_2, queue_length