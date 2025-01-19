from utils.scale_up import scale_up

def convert(bandwidths, latencies, durations, queue_length):
    scale_up(bandwidths, 1000)
    scale_up(latencies, 5)
    scale_up(durations, 50)

    queue_length *= 10

    return bandwidths, latencies, durations, queue_length

def convert_mptcp(bandwidths_1, latencies_1, bandwidths_2, latencies_2, durations, queue_length):
    scale_up(bandwidths_1, 1000)
    scale_up(latencies_1, 5)
    scale_up(bandwidths_2, 1000)
    scale_up(latencies_2, 5)
    scale_up(durations, 50)

    queue_length *= 10

    return bandwidths_1, latencies_1, bandwidths_2, latencies_2, durations, queue_length