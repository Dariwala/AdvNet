#!/usr/bin/env bash
set -euo pipefail

# Optional: enable this for debug output
# DEBUG=1
# [[ -n "${DEBUG-}" ]] && set -x

shopt -s nullglob

if [[ $# -lt 6 ]]; then
    echo "Usage: $0 <GA|RG> <timesteps> <eval> <lcb|nolcb> <serial|parallel> <compute|fromfile> [n_last_lines]"
    echo "Example: $0 GA 2 7 lcb parallel compute 3"
    exit 1
fi

ALG=$1
TIMESTEPS=$2
EVAL=$3
LCB=$4
SERIAL=$5
SOURCE=$6       # compute or fromfile
N_LAST=${7:-1}  # optional, default 1

# Validate inputs
if [[ "$ALG" != "GA" && "$ALG" != "RG" && "$ALG" != "RG_then_GA" ]]; then
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
if [[ "$SOURCE" != "compute" && "$SOURCE" != "fromfile" ]]; then
    echo "SOURCE must be 'compute' or 'fromfile'"
    exit 1
fi

# build filename suffix
if [[ "$LCB" == "lcb" ]]; then
    FILE_SUFFIX="_${TIMESTEPS}_timesteps_with_delay_${SERIAL}_${EVAL}_eval_lcb"
else
    FILE_SUFFIX="_${TIMESTEPS}_timesteps_with_delay_${SERIAL}_${EVAL}_eval_median_tcoeff_0.1"
fi

PATTERN="time_3600/score_across_comparisons_${ALG}_*_vs_*${FILE_SUFFIX}"

refs=("bbr" "cubic" "highspeed" "reno" "vegas" "dctcp" "hybla" "illinois" "westwood" "scalable")
tars=("bbr" "cubic" "highspeed" "reno" "vegas" "dctcp" "hybla" "illinois" "westwood" "scalable")
declare -A results

for file in $PATTERN; do
    [[ -f "$file" ]] || continue

    base=$(basename "$file")
    ref=$(echo "$base" | sed -E "s/^score_across_comparisons_${ALG}_([^_]*)_vs_([^_]*)${FILE_SUFFIX}/\1/")
    tar=$(echo "$base" | sed -E "s/^score_across_comparisons_${ALG}_([^_]*)_vs_([^_]*)${FILE_SUFFIX}/\2/")

    if [[ -z "$ref" || -z "$tar" ]]; then
        echo "Warning: could not parse ref/tar from $file; skipping"
        continue
    fi
    if [[ ! " ${refs[*]} " =~ " ${ref} " ]] || [[ ! " ${tars[*]} " =~ " ${tar} " ]]; then
        echo "Skipping $ref vs $tar (not in refs/tars list)"
        continue
    fi

    max_score=""

    while IFS= read -r line; do
        trace=$(echo "$line" | sed -n "s/.*\[\([^]]*\)\].*/\1/p" | tr -d "'," | xargs)
        [[ -z "$trace" ]] && continue

        if [[ "$SOURCE" == "compute" ]]; then
            # Run python analysis for score
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
        else
            # Directly extract score from line (3rd column)
            score=$(echo "$line" | awk '{print $3}')
        fi

        # Validate numeric score
        if ! [[ $score =~ ^[+-]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]+)?$ ]]; then
            echo "Warning: non-numeric score ('$score') for $ref vs $tar; skipping"
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

# Print matrix rows
for ref in "${refs[@]}"; do
    printf "%s\t" "$ref"  # start row with reference
    for tar in "${tars[@]}"; do
        if [[ "$ref" == "$tar" ]]; then
            printf "\t"      # empty cell for diagonal
        else
            printf "%s\t" "${results["$ref $tar"]:-NA}"
        fi
    done
    printf "\n"
done
