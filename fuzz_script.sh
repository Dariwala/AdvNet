#!/bin/bash
sudo ls

refs=("cubic" "bbr" "reno" "vegas")

# Loop over each reference parameter
for ref in "${refs[@]}"; do
    # Run GA
    python search_adv_traces.py --type=0 --alg=1 --trace_length=50 --l_bounds 0 --u_bounds 24 --n_eval=3 --ref="$ref" --total_time=3600 --pop_size=30 --n_iter=20 --fuzzing
    python search_adv_traces.py --type=0 --alg=1 --trace_length=75 --l_bounds 0 --u_bounds 24 --n_eval=3 --ref="$ref" --total_time=3600 --pop_size=30 --n_iter=20 --fuzzing
    python search_adv_traces.py --type=0 --alg=1 --trace_length=100 --l_bounds 0 --u_bounds 24 --n_eval=3 --ref="$ref" --total_time=3600 --pop_size=30 --n_iter=20 --fuzzing
done