from utils.scale_up import scale_up
from picoquic.split_trace import split

def convert(trace, exp_type):
    if exp_type == 1:
        bandwidths_1, bandwidths_2, latencies_1, latencies_2, durations, data, queue_length = split(trace, 1)
        scale_up(bandwidths_1, 500)#l = 1,u=400
        scale_up(bandwidths_2, 500)#l=1,u=400
        scale_up(latencies_1, 5)#l=1,u=40
        scale_up(latencies_2, 5)#l=1,u=40
        scale_up(durations, 5)#l=1,u=40
        data *= 500 #l=1,u=10000
        queue_length *= 100 #l=1,u=50
        return bandwidths_1 + bandwidths_2 + latencies_1 + latencies_2 + durations + [data, queue_length]
    elif exp_type == 2:
        bandwidths, latencies, durations, data, queue_length = split(trace, 2)
        scale_up(bandwidths, 500)#l = 1,u=400
        scale_up(latencies, 5)#l=1,u=40
        scale_up(durations, 5)#l=1,u=40
        data *= 500 #l=1,u=10000
        queue_length *= 100 #l=1,u=50
        return bandwidths + latencies + durations + [data, queue_length]
    