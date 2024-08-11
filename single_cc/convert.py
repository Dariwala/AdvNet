from single_cc.split_trace import split_trace
from utils.scale_up import scale_up

def convert(trace):
    bandwidths, latencies, durations, queue_length = split_trace(trace)
    scale_up(bandwidths, 500) #l=1,u=300
    scale_up(latencies, 1) #l=1,u=40
    scale_up(durations, 50) #l=1,u=40
    # data *= 10 #l=1,u=1000
    queue_length *= 100 #l=1,u=100

    return bandwidths, latencies, durations, queue_length