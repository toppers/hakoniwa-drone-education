#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: $0 <dir>"
    exit 1
fi

DIR=${1}

cd ${DIR}

echo "freq, log_freq, gain, phase, phase1_at_freq, phase2_at_freq" | tee result.csv
for entry in $(ls | sort -V)
do
    if [ ! -d $entry ]
    then
        continue
    fi
    cd $entry
    python ../../../../src/drone_evaluation/freq_evaluator.py sine-input-updated.json | tee -a ../result.csv
    cd ..
done
