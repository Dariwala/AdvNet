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

def create_trace_rl(latencies, durations):
    unique_filename = f"file_{float(time.time())}"

    last_line = ""

    with open("traces/" + unique_filename, 'w') as file:
        base_time = 0
        for i, duration in enumerate(durations):
            latency = latencies[i]
            file.write(str(base_time + 1) + " " + str(round(latency)) + "\n")
            file.write(str(base_time + duration) + " " + str(round(latency)) + "\n")

            base_time = base_time + duration

            last_line += " " + str(base_time)

        file.write("Durations" + last_line + "\n")
    
    return unique_filename

def create_trace_fuzzing():
    unique_filename = f"file_{float(time.time())}"

    with open("traces/" + unique_filename, 'w') as file:    
        file.write("0  10\n")
        file.write("999  10\n")
        file.write("1000  11\n")
        file.write("1999  11\n")
    
    return unique_filename