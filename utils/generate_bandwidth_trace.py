import time

def create_trace(bandwidths, durations):
    unique_filename = f"file_{float(time.time())}"

    with open("traces/" + unique_filename, 'w') as file:
        # file.write("PDO\n")
        base_time = 0
        for i, duration in enumerate(durations):
            bandwidth = bandwidths[i]
            pdos = []
            time_unit = 12000 / bandwidth
            end_time = base_time + duration
            while base_time + time_unit <= end_time:
                pdos.append(round(base_time + time_unit))
                base_time += time_unit
            base_time = end_time
            if len(pdos) == 0:
                pdos.append(end_time)

            for pdo in pdos:
                file.write(str(pdo)+"\n")
        return unique_filename

def create_trace_non_pdo(bandwidths, durations):
    unique_filename = f"file_{float(time.time())}"

    with open("traces/" + unique_filename, 'w') as file:
        file.write("NON-PDO\n")
        for i, _ in enumerate(bandwidths):
            file.write(str(bandwidths[i]) + " " + str(durations[i]) + "\n")
    return unique_filename
    
def create_trace_fuzzing(pdos):
    unique_filename = f"file_{float(time.time())}"

    with open("traces/" + unique_filename, 'w') as file:
        for pdo in pdos:
            file.write(str(pdo)+"\n")
        return unique_filename