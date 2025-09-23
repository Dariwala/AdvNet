#!/bin/bash

sudo ls
N=10  # Number of runs
declare -A total_cpu
cores=(0 1 2)

# Initialize totals
for core in "${cores[@]}"; do
    total_cpu[$core]=0
done

for i in $(seq 1 $N); do
    echo "Run $i..."

    # Run mpstat for all 3 cores in background
    (mpstat -P 0,1,2 1 > mpstat_output.txt) & MPSTAT_PID=$!
    
    # Run your experiment
    python analyze_single_cc_trace.py --trace 1200 1 100 100 --ref=bbr --tar=cubic --mptcp --mptcp_type=6 --multiprocessing --n_processes=2
    
    # Kill mpstat once experiment finishes
    kill $MPSTAT_PID
    wait $MPSTAT_PID 2>/dev/null

    echo "Average CPU usage for run $i:"
    
    for core in "${cores[@]}"; do
        avg_cpu=$(awk -v core=$core '/^[0-9]/ && $3 == core { idle += $(NF); count++ } END { if (count > 0) print 100 - idle/count }' mpstat_output.txt)
        echo "  Core $core: $avg_cpu%"
        total_cpu[$core]=$(echo "${total_cpu[$core]} + $avg_cpu" | bc)
    done
done

echo "------------------------------------------"
echo "Final average CPU usage over $N runs:"
for core in "${cores[@]}"; do
    final_avg=$(echo "scale=2; ${total_cpu[$core]} / $N" | bc)
    echo "  Core $core: $final_avg%"
done
