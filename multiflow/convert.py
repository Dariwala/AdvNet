from utils.scale_up import scale_up

def convert(bandwidths, latencies, durations, queue_length):
    scale_up(bandwidths, 1000)
    scale_up(latencies, 5)
    scale_up(durations, 50)

    queue_length *= 10

    return bandwidths, latencies, durations, queue_length