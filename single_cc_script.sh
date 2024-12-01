#!/bin/bash
sudo ls

# refs=("cubic" "reno" "bbr" "bic" "cdg" "dctcp" "highspeed" "htcp" "hybla" "illinois" "lp" "nv" "scalable" "vegas" "veno" "westwood" "yeah")
# refs=("cubic" "reno" "bbr" "vegas" "westwood")
refs=("vegas")

for ref in "${refs[@]}"; do
    python search_adv_traces.py --type=0 --alg=1 --trace_length=4 --l_bounds 1 1 10 1 --u_bounds 20 30 40 100 --n_eval=3 --ref="$ref" --total_time=36 --pop_size=30 --n_iter=20
    # python search_adv_traces.py --type=0 --alg=1 --trace_length=7 --l_bounds 1 1 1 1 10 10 1 --u_bounds 20 20 30 30 40 40 100 --n_eval=3 --ref="$ref" --total_time=3600 --pop_size=30 --n_iter=20
    # python search_adv_traces.py --type=0 --alg=1 --trace_length=10 --l_bounds 1 1 1 1 1 1 10 10 10 1 --u_bounds 20 20 20 30 30 30 40 40 40 100 --n_eval=3 --ref="$ref" --total_time=1800 --pop_size=30 --n_iter=20
    # python search_adv_traces.py --type=0 --alg=1 --trace_length=13 --l_bounds 1 1 1 1 1 1 1 1 10 10 10 10 1 --u_bounds 20 20 20 20 30 30 30 30 40 40 40 40 100 --n_eval=3 --ref="$ref" --total_time=1800 --pop_size=30 --n_iter=20
    # python search_adv_traces.py --type=0 --alg=1 --trace_length=16 --l_bounds 1 1 1 1 1 1 1 1 1 1 10 10 10 10 10 1 --u_bounds 20 20 20 20 20 30 30 30 30 30 40 40 40 40 40 100 --n_eval=3 --ref="$ref" --total_time=1800 --pop_size=30 --n_iter=20
done