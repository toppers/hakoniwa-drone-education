#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <input_dir>"
    exit 1
fi

INPUT_DIR="$1"
DIRNAME=$(basename "${INPUT_DIR}")

LINE_NUM=$(($(wc -l < "${INPUT_DIR}/test_pattern.csv") - 1))

if [ "${LINE_NUM}" -lt 0 ]; then
    echo "The file is empty or only contains a header."
    exit 1
fi

mkdir -p test-results/${DIRNAME}
rm -rf test-results/${DIRNAME}/*
echo "freq, log_freq, gain, phase, phase1_at_freq, phase2_at_freq" > test-results/${DIRNAME}/result.csv
for i in $(seq "${LINE_NUM}"); do
    index=$((i - 1))
    echo "index: ${index}"
    python ../src/drone_evaluation/update_input_params.py \
            "${INPUT_DIR}/test_pattern.csv" "${INPUT_DIR}/config.json" \
            ../src/drone_evaluation/template/sine-input.json ${index}
    bash -x ../src/drone_evaluation/evaluate.bash sine-input-updated.json
    python ../src/drone_evaluation/freq_evaluator.py ./sine-input-updated.json \
        >> test-results/${DIRNAME}/result.csv
    sed_line_no=$(expr $i + 1)
    FREQ="freq_$(sed -n "${sed_line_no}p" "${INPUT_DIR}/test_pattern.csv" | awk -F, '{print $1}')"
    mkdir -p test-results/${DIRNAME}/${FREQ}
    mv sine-input-updated.json test-results/${DIRNAME}/${FREQ}/
    mv in.csv test-results/${DIRNAME}/${FREQ}/
    mv drone_log0 test-results/${DIRNAME}/${FREQ}/
done
