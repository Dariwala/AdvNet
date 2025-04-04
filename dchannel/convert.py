from utils.scale_up import scale_up
from dchannel.split_trace import split

def convert(trace):
    bandwidths_1, bandwidths_2, latencies, durations, ll_latency, queue_length, data = split(trace)
    scale_up(bandwidths_1, 500)#l = 30,u=300
    scale_up(bandwidths_2, 500)#l=2,u=10
    scale_up(latencies, 5)#l=1,u=25
    scale_up(durations, 5)#l=1,u=20
    data *= 500 #l=1,u=10
    queue_length *= 100 #l=1,u=50

    return bandwidths_1 + bandwidths_2 + latencies + durations + [data, ll_latency, queue_length]