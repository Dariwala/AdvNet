def split(trace):
    queue_length = trace[-1]
    ll_latency = trace[-2]
    data = trace[-3]

    l = len(trace) - 3
    bandwidths_1 = trace[:l//4]
    bandwidths_2 = trace[l//4:2*(l//4)]
    latencies = trace[2*(l//4):3*(l//4)]
    durations = trace[3*(l//4):l]

    return bandwidths_1, bandwidths_2, latencies, durations, ll_latency, queue_length, data