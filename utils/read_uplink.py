def read_uplink(file, data = -1):
    with open(file) as f:
        output = f.read()
        # throughput = output.split("\n")[-2].split()[-4]
        # unit = output.split("\n")[-2].split()[-3]
        # # print("HOHOH", output)
        # if unit == "MBytes":
        #     return float(throughput)
        # elif unit == "KBytes":
        #     return float(throughput) / 1024
        tot_bytes = 0
        time_stamp = 0
        lines = output.split('\n')[4:-1]
        start_time = int(lines[0].split()[0])
        for line in lines:
            line = line.split()
            time_stamp = int(line[0])
            if line[1] == '-':
                tot_bytes += int(line[2])
                if data != -1 and tot_bytes >= data:
                    return -1, time_stamp - start_time
    return tot_bytes, time_stamp - start_time