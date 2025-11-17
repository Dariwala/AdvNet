#!/bin/bash
source ../AdvNetVenv/bin/activate
sudo sysctl -w net.ipv4.ip_forward=1
# Define the list of seeds
seeds=(3)

# Define the list of reference parameters
# refs=("cubic" "reno" "bbr" "bic" "cdg" "dctcp" "highspeed" "htcp" "hybla" "illinois" "lp" "nv" "scalable" "vegas" "veno" "westwood" "yeah")
# refs=("highspeed" "htcp" "hybla" "illinois" "lp" "nv" "scalable" "vegas" "veno" "westwood" "yeah")
# refs=("bbr" "cubic" "vegas" "wvegas" "balia")
# tars=("cubic" "reno" "bbr" "bic" "cdg" "dctcp" "highspeed" "htcp" "hybla" "illinois" "lp" "nv" "scalable" "vegas" "veno" "westwood" "yeah")
# tars=("cubic" "reno" "bbr" "bic" "cdg" "dctcp" "highspeed" "htcp" "hybla" "illinois" "lp" "nv" "scalable" "vegas" "veno" "westwood" "yeah")
# refs=("cubic")
tars=("bbr1")
refs=("bbr")

# Loop over each seed
for ref in "${refs[@]}"; do
    # Loop over each reference parameter
    for tar in "${tars[@]}"; do
        if [ "$ref" == "$tar" ]; then
            continue
        fi
        # Run GA
        # python search_adv_traces.py --l_bounds 1 1 1 1 10 10 --u_bounds 120 20 120 20 50 500 --trace_length=6 --alg=1 --ref="$ref" --seed="$seed" --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=1 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 10 10 10 --u_bounds 120 120 20 20 120 120 20 20 50 50 500 --trace_length=11 --alg=1 --ref="$ref" --seed="$seed" --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=1 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 1 1 1 1 10 10 10 10 --u_bounds 120 120 120 20 20 20 120 120 120 20 20 20 50 50 50 500 --trace_length=16 --alg=1 --ref="$ref" --seed="$seed" --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=1 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 10 10 10 10 10 --u_bounds 120 120 120 120 20 20 20 20 120 120 120 120 20 20 20 20 50 50 50 50 500 --trace_length=21 --alg=1 --ref="$ref" --seed="$seed" --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=1 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 10 10 10 10 10 10 --u_bounds 120 120 120 120 120 20 20 20 20 20 120 120 120 120 120 20 20 20 20 20 50 50 50 50 50 500 --trace_length=26 --alg=1 --ref="$ref" --seed="$seed" --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=1 --total_time=3600
        #Extract execution time of GA
        # tot_time=$(tail -n 1 "results/res_seed_${seed}_ref_${ref}_GA.txt" | awk '{print $NF}')
        #Run random generation for the same time
        # python search_adv_traces.py --l_bounds 1000 1000 5 5 1000 1000 --u_bounds 4000 4000 20 20 3000 3000 --trace_length=6 --alg=0 --total_time=$tot_time --ref="$ref" --seed="$seed" --n_eval=3 > results/"res_seed_${seed}_ref_${ref}_RG.txt"
        # python search_adv_traces.py --l_bounds 1 1 1 1 10 10 --u_bounds 120 20 1 1 50 500 --trace_length=6 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=6 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 10 10 10 0 --u_bounds 120 120 20 20 1 1 1 1 50 50 500 100 --trace_length=12 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=6 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 1 1 1 1 10 10 10 10 --u_bounds 120 120 120 20 20 20 1 1 1 1 1 1 50 50 50 500 --trace_length=16 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=6 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 10 10 10 10 10 --u_bounds 120 120 120 120 20 20 20 20 1 1 1 1 1 1 1 1 50 50 50 50 500 --trace_length=21 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=6 --total_time=3600
        # python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 10 10 10 10 10 10 --u_bounds 120 120 120 120 120 20 20 20 20 20 1 1 1 1 1 1 1 1 1 1 50 50 50 50 50 500 --trace_length=26 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=6 --total_time=3600
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 10 --u_bounds 1200 1200 50 50 50 50 100 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=500 --pop_size=25 --n_eval=5 --type=4
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=1 --kernel=5 --type=1 --mptcp_type=8 --total_time=36000
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=2 --kernel=5 --type=1 --mptcp_type=8 --total_time=36000
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=8 --total_time=36000
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=4 --kernel=5 --type=1 --mptcp_type=8 --total_time=36000
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=5 --kernel=5 --type=1 --mptcp_type=8 --total_time=36000
        sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=0 --ref="$ref" --tar="$tar" --seed=1 --n_iter=350 --pop_size=25 --n_eval=5 --kernel=5 --type=1 --mptcp_type=7 --total_time=3600
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=8 --kernel=5 --type=1 --mptcp_type=7 --total_time=36000
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=9 --kernel=5 --type=1 --mptcp_type=7 --total_time=36000
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 200 200 100 100 50 50 1000 --trace_length=7 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=150 --pop_size=25 --n_eval=10 --kernel=5 --type=1 --mptcp_type=7 --total_time=36000
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 10 10 50 --u_bounds 1200 1200 50 50 50 50 1000 --trace_length=7 --alg=3 --ref="$ref" --tar="$tar" --seed=1 --n_iter=1500 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=6 --total_time=3600
        # sudo ls;python search_adv_traces.py --l_bounds 1 1 1 1 1 1 1 1 1 1 1 1 10 10 10 10 10 10 10 --u_bounds 1200 1200 1200 1200 1200 1200 50 50 50 50 50 50 50 50 50 50 50 50 100 --trace_length=19 --alg=1 --ref="$ref" --tar="$tar" --seed=1 --n_iter=3300 --pop_size=25 --n_eval=3 --type=1 --mptcp_type=7 --kernel=5 --total_time=50000
        # ../clean.sh
        # rm traces/*
        # sleep 300
        # break
    done
    # break
done

# python search_adv_traces.py --l_bounds 1 1 1 1 10 10 --u_bounds 120 20 120 20 50 500 --trace_length=6 --alg=1 --ref=lia --tar=balia --seed=1 --n_iter=10 --pop_size=25 --n_eval=3 --kernel=5 --type=1 --mptcp_type=5 --total_time=3600