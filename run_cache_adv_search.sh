#!/usr/bin/env bash
set -euo pipefail

export ADVNET_CACHESIM="/Users/shehaba2/Documents/PhD Research/libcachesim/_build/bin/cachesim"

# Full policy list used for both --ref and --tar
POLICIES=(LRU FIFO Clock LFU LFUDA ARC LeCaR TwoQ S3FIFO Sieve Hyperbolic PQEvolve)

SEEDS=(1 2 3 4 5)

# Pairs already completed in the earlier mini matrix: ref in {LRU,LFU,FIFO,ARC}, tar in {LeCaR}
ALREADY_DONE_REFS=(LRU FIFO Clock LFU LFUDA ARC LeCaR TwoQ S3FIFO Sieve Hyperbolic)
ALREADY_DONE_TARS=(LRU FIFO Clock LFU LFUDA ARC LeCaR TwoQ S3FIFO Sieve Hyperbolic)

is_already_done() {
    local ref="$1"
    local tar="$2"
    local tar_match=1
    for t in "${ALREADY_DONE_TARS[@]}"; do
        if [[ "${t}" == "${tar}" ]]; then
            tar_match=0
            break
        fi
    done
    if [[ "${tar_match}" -eq 0 ]]; then
        for r in "${ALREADY_DONE_REFS[@]}"; do
            if [[ "${r}" == "${ref}" ]]; then
                return 0
            fi
        done
    fi
    return 1
}

for SEED in "${SEEDS[@]}"; do
    for REF in "${POLICIES[@]}"; do
        for TAR in "${POLICIES[@]}"; do

            # Skip ref == tar
            if [[ "${REF}" == "${TAR}" ]]; then
                continue
            fi

            # Skip pairs already run in the earlier mini matrix
            if is_already_done "${REF}" "${TAR}"; then
                echo "--- Skipping already-completed pair seed=${SEED} ref=${REF} tar=${TAR} ---"
                continue
            fi

            echo "=== Running seed=${SEED} ref=${REF} tar=${TAR} ==="

            python -u search_adv_traces.py \
                --type=8 --alg=1 \
                --ref="${REF}" --tar="${TAR}" --cache_size=knob \
                --trace_length=11 \
                --l_bounds  50  1  1  0  0   50  1  1  0  0    10 \
                --u_bounds 150 200 64 50 50  150 200 64 50 50  500 \
                --seed="${SEED}" --pop_size=20 --n_iter=500 --total_time=3600

            echo "=== Finished seed=${SEED} ref=${REF} tar=${TAR} ==="
        done
    done
done