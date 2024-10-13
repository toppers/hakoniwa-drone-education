#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <dir>"
    exit 1
fi

INPUT_DIR="$1"
DIRNAME=$(basename ${INPUT_DIR})

LINE_NUM=$(($(wc -l < "${INPUT_DIR}/test_pattern.csv") - 1))

if [ "${LINE_NUM}" -lt 0 ]; then
    echo "The file is empty or only contains a header."
    exit 1
fi

mkdir -p test-results/${DIRNAME}
echo "freq, log_freq, gain, phase" > test-results//${DIRNAME}/result.csv
for i in $(seq "${LINE_NUM}"); do
    index=$((i - 1))
    echo "index: ${index}"
    python ../src/drone_evaluation/update_input_params.py \
            "${INPUT_DIR}/test_pattern.csv" "${INPUT_DIR}/config.json" \
            ../src/drone_evaluation/template/sine-input.json ${index}
    bash -x ../src/drone_evaluation/evaluate.bash sine-input-updated.json
    python ../src/drone_evaluation/freq_evaluator.py ./sine-input-updated.json \
        >> test-results//${DIRNAME}/result.csv
done
