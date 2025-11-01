#!/usr/bin/env bash
set -euo pipefail

# Optional: enable this for debug output
# DEBUG=1
# [[ -n "${DEBUG-}" ]] && set -x

shopt -s nullglob

if [[ $# -lt 5 ]]; then
    echo "Usage: $0 <GA|RG> <timesteps> <eval> <lcb|nolcb> <serial|parallel> [n_last_lines]"
    echo "Example: $0 GA 2 7 lcb parallel 3"
    exit 1
fi

ALG=$1           # GA or RG
TIMESTEPS=$2     # e.g., 2
EVAL=$3          # e.g., 7
LCB=$4           # lcb or nolcb
SERIAL=$5        # serial or parallel
N_LAST=${6:-1}   # optional, default 1

# Validate inputs a bit
if [[ "$ALG" != "GA" && "$ALG" != "RG" ]]; then
    echo "ALG must be GA or RG"
    exit 1
fi
if [[ "$LCB" != "lcb" && "$LCB" != "nolcb" ]]; then
    echo "LCB must be 'lcb' or 'nolcb'"
    exit 1
fi
if [[ "$SERIAL" != "serial" && "$SERIAL" != "parallel" ]]; then
    echo "SERIAL must be 'serial' or 'parallel'"
    exit 1
fi

# build filename suffix
if [[ "$LCB" == "lcb" ]]; then
    FILE_SUFFIX="_${TIMESTEPS}_timesteps_with_delay_${SERIAL}_${EVAL}_eval_lcb"
else
    FILE_SUFFIX="_${TIMESTEPS}_timesteps_with_delay_${SERIAL}_${EVAL}_eval_median"
fi

PATTERN="time_3600/score_across_comparisons_${ALG}_*_vs_*${FILE_SUFFIX}"

# ---------------------------
# Congestion controls (example)
# ---------------------------
refs=("bbr")   # rows
tars=("cubic") # columns

declare -A results

# ---------------------------
# Collect scores
# ---------------------------
for file in $PATTERN; do
    [[ -f "$file" ]] || continue

    base=$(basename "$file")

    # Extract ref and tar from filename
    ref=$(echo "$base" | sed -E "s/^score_across_comparisons_${ALG}_([^_]*)_vs_([^_]*)${FILE_SUFFIX}/\1/")
    tar=$(echo "$base" | sed -E "s/^score_across_comparisons_${ALG}_([^_]*)_vs_([^_]*)${FILE_SUFFIX}/\2/")

    if [[ -z "$ref" || -z "$tar" ]]; then
        echo "Warning: could not parse ref/tar from $file; skipping"
        continue
    fi

    # ✅ Only evaluate if ref ∈ refs and tar ∈ tars
    if [[ ! " ${refs[*]} " =~ " ${ref} " ]] || [[ ! " ${tars[*]} " =~ " ${tar} " ]]; then
        echo "Skipping $ref vs $tar (not in refs/tars list)"
        continue
    fi

    max_score=""

    while IFS= read -r line; do
        trace=$(echo "$line" | sed -n "s/.*\[\([^]]*\)\].*/\1/p" | tr -d "'," | xargs)
        [[ -z "$trace" ]] && continue

        tmpfile=$(mktemp)
        python -u analyze_single_cc_trace.py \
            --trace $trace \
            --ref="$ref" \
            --tar="$tar" \
            --mptcp \
            --mptcp_type=8 \
            --n_processes=1 > "$tmpfile"

        score=$(tail -n 1 "$tmpfile" | tr -d '[:space:]')
        rm -f "$tmpfile"

        if ! [[ $score =~ ^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?$ ]]; then
            echo "Warning: non-numeric score ('$score') for $ref vs $tar; skipping this line"
            continue
        fi

        if [[ -z "$max_score" ]]; then
            max_score="$score"
        else
            is_greater=$(awk -v a="$score" -v b="$max_score" 'BEGIN{print (a > b) ? 1 : 0}')
            [[ "$is_greater" == "1" ]] && max_score="$score"
        fi
    done < <(tail -n "$N_LAST" "$file")

    [[ -z "$max_score" ]] && max_score="NA"

    echo "Final score ($ref vs $tar): $max_score"
    results["$ref $tar"]="$max_score"
done

# ---------------------------
# Print matrix
# ---------------------------
printf "\t"
for tar in "${tars[@]}"; do
    printf "%s\t" "$tar"
done
printf "\n"

for ref in "${refs[@]}"; do
    printf "%s\t" "$ref"
    for tar in "${tars[@]}"; do
        if [[ "$ref" == "$tar" ]]; then
            printf "\t"
        else
            printf "%s\t" "${results["$ref $tar"]:-NA}"
        fi
    done
    printf "\n"
done
