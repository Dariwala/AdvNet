def split(trace):
    queue_length = trace[-1]
    data = trace[-2]

    l = len(trace) - 2
    bandwidths_1 = trace[:l//5]
    bandwidths_2 = trace[l//5:2*(l//5)]
    latencies_1 = trace[2*(l//5):3*(l//5)]
    latencies_2 = trace[3*(l//5):4*(l//5)]
    durations = trace[4*(l//5):l]

    return bandwidths_1, bandwidths_2, latencies_1, latencies_2, durations, data, queue_length