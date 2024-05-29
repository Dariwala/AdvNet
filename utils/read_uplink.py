def read_uplink(file):
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
        duration = 0
        lines = output.split('\n')[4:-1]
        for line in lines:
            line = line.split()
            duration = int(line[0])
            if line[1] == '-':
                tot_bytes += int(line[2])
    return tot_bytes, duration