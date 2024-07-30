from utils.scale_up import scale_up
from picoquic.split_trace import split

def convert(trace):
    bandwidths_1, bandwidths_2, latencies_1, latencies_2, durations, data, queue_length = split(trace)
    scale_up(bandwidths_1, 500)#l = 1,u=400
    scale_up(bandwidths_2, 500)#l=1,u=400
    scale_up(latencies_1, 5)#l=1,u=40
    scale_up(latencies_2, 5)#l=1,u=40
    scale_up(durations, 5)#l=1,u=40
    data *= 500 #l=1,u=10000
    queue_length *= 100 #l=1,u=50

    return bandwidths_1 + bandwidths_2 + latencies_1 + latencies_2 + durations + [data, queue_length]