from collections import defaultdict

file = "mptcp_simplification_results"
ref = ""
initial_p_score = None
final_p_score = None
initial_c_score = None
final_c_score = None
fc = defaultdict(int)
ic = defaultdict(int)
fp = defaultdict(int)
ip = defaultdict(int)
s_l = defaultdict(int)
with open(file) as f:
    lines = f.readlines()
    for line in lines:
        if line.startswith("Reference"):
            ref = line[11:-1]
        elif line.startswith("Initial trace"):
            no_of_timesteps = (len(line[16:-1].split(",")) - 1) // 6
        elif line.startswith("Simplified trace"):
            no_of_timesteps_s = (len(line[19:-1].split(",")) - 1)
        elif line.startswith("Initial p_score"):
            initial_p_score = float(line[17:-1])
        elif line.startswith("Initial c_score"):
            initial_c_score = float(line[17:-1])
        elif line.startswith("Simplified p_score"):
            try:
                final_p_score = float(line[20:-1])
            except ValueError:
                final_p_score = initial_p_score
        elif line.startswith("Simplified c_score"):
            final_c_score = float(line[20:-1])

            fc[ref+"_"+str(no_of_timesteps)] += final_c_score / 3
            fp[ref+"_"+str(no_of_timesteps)] += final_p_score / 3
            ic[ref+"_"+str(no_of_timesteps)] += initial_c_score / 3
            ip[ref+"_"+str(no_of_timesteps)] += initial_p_score / 3
            s_l[ref+"_"+str(no_of_timesteps)] += no_of_timesteps_s / 3

for key in fc:
    print(key, ip[key], fp[key], ic[key], fc[key], s_l[key])

        
