from utils.scale_up import scale_up
from mptcp.split_trace import split_trace

def convert(trace, simplify = False):
    bandwidths_1, latencies_1, durations, bandwidths_2, latencies_2, queue_length = split_trace(trace)
    scale_up(bandwidths_1, 500)
    scale_up(bandwidths_2, 500)

    scale_up(latencies_1, 5)
    scale_up(latencies_2, 5)

    scale_up(durations, 50)

    queue_length *= 10
    
    if simplify:
        return bandwidths_1 + latencies_1 + durations + bandwidths_2 + latencies_2 + durations + [queue_length]
    else:
        return bandwidths_1 + latencies_1 + bandwidths_2 + latencies_2 + durations + [queue_length]