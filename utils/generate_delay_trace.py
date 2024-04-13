import time

def create_trace(latencies, durations):
    unique_filename = f"file_{float(time.time())}"

    with open("traces/" + unique_filename, 'w') as file:
        base_time = 0
        for i, duration in enumerate(durations):
            latency = latencies[i]
            file.write(str(base_time + 1) + " " + str(round(latency)) + "\n")
            file.write(str(base_time + duration) + " " + str(round(latency)) + "\n")

            base_time = base_time + duration
    
    return unique_filename