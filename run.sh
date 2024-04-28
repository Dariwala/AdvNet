#!/bin/bash
source ../AdvNetVenv/bin/activate
# Define the list of seeds
seeds=(1)

# Define the list of reference parameters
# refs=("cubic" "reno" "bbr" "bic" "cdg" "dctcp" "highspeed" "htcp" "hybla" "illinois" "lp" "nv" "scalable" "vegas" "veno" "westwood" "yeah")
# refs=("highspeed" "htcp" "hybla" "illinois" "lp" "nv" "scalable" "vegas" "veno" "westwood" "yeah")
refs=("bbr")

# Loop over each seed
for seed in "${seeds[@]}"; do
    # Loop over each reference parameter
    for ref in "${refs[@]}"; do
        # Run GA
        # python search_adv_traces.py --l_bounds 1000 1000 5 5 1000 1000 --u_bounds 4000 4000 20 20 3000 3000 --trace_length=6 --alg=1 --ref="$ref" --seed="$seed" --n_iter=10 --pop_size=30 --n_eval=3 > results/"res_seed_${seed}_ref_${ref}_GA.txt"
        #Extract execution time of GA
        tot_time=$(tail -n 1 "results/res_seed_${seed}_ref_${ref}_GA.txt" | awk '{print $NF}')
        #Run random generation for the same time
        python search_adv_traces.py --l_bounds 1000 1000 5 5 1000 1000 --u_bounds 4000 4000 20 20 3000 3000 --trace_length=6 --alg=0 --total_time=$tot_time --ref="$ref" --seed="$seed" --n_eval=3 > results/"res_seed_${seed}_ref_${ref}_RG.txt"
    done
done
