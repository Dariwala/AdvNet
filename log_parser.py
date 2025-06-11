import re

log = "UC2_SPTCP_Linux_Kernel_with_delay_coeff"

refs = []
tars = []
values = {}
traces = {}

with open(log) as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        line = line[:-1]
        # print(line)
        if line.split()[1] == "vs":
            ref = line.split()[0]
            tar = line.split()[2]
            no_of_timesteps = int(line.split()[3])
            score = float(line.split()[5])
            trace = ""
            # while True:
            line_no = i
            char_no = 0
            while lines[line_no][char_no] != '[':
                # print(lines[line_no][char_no])
                char_no += 1
            # while lines[line_no][char_no] < '1' or lines[line_no][char_no] > '9':
            char_no += 1
            # if lines[line_no][char_no] == '\t' or lines[line_no][char_no] == '':
            #     char_no += 1
            while lines[line_no][char_no] != ']':
                trace += lines[line_no][char_no]
                char_no += 1
                if char_no == len(lines[line_no]):
                    line_no += 1
                    char_no = 0

            # print(ref,tar,no_of_timesteps,score)
            if ref not in refs:
                refs.append(ref)
                values[ref] = {}
                traces[ref] = {}
            if tar not in tars:
                tars.append(tar)
            if tar not in values[ref]:
                values[ref][tar] = []
                traces[ref][tar] = []
            values[ref][tar].append(score)
            traces[ref][tar].append(trace)

def print_log(refs, tars):
    for ref in refs:
        print("\t"+ref,end="")
    print()
    for tar in tars:
        print(tar, end="")
        for ref in refs:
            try:
                # print('\t', end="")
                # print("\t" + str(round(max(values[ref][tar]),2)), end = "")
                # print("\t" + str(values[ref][tar].index(max(values[ref][tar]))+1), end = "")
                # print('\t' + re.sub(r"[\s\t\n]+", ",", traces[ref][tar][values[ref][tar].index(max(values[ref][tar]))]), end = "")
                print('\t' + re.sub(r"[\s\t\n]+", ",", traces[ref][tar][values[ref][tar].index(max(values[ref][tar]))].split()[-1]), end = "")
            except KeyError:
                print("\t", end = "")
        print()
print_log(refs, tars)
# str(values[ref][tar].index(max(values[ref][tar]))+1)

# cluster_1 = ["dctcp", "reno", "highspeed", "illinois", "htcp", "bic", "scalable", "veno"]

# print_log(cluster_1, tars)
# print("\t" + re.sub(r"[\s\t\n]+", ",", traces["highspeed"]["reno"][values["highspeed"]["reno"].index(max(values["highspeed"]["reno"]))].strip()), end = "")
# print("\t" + re.sub(r"[\s\t\n]+", ",", traces["htcp"]["bbr"][values["bic"]["bbr"].index(max(values["bic"]["bbr"]))].strip()), end = "")