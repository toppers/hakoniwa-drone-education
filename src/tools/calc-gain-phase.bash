#!/bin/bash

if [ $# -ne 3 ]
then
    echo "Usage: $0 <start_time> <duration> <frequency>"
    exit 1
fi

START_TIME=${1}
DURATION=${2}
FREQ=${3}
TOTAL_TIME=$((START_TIME + DURATION + 100))

# シグナルハンドラ
function handler()
{
    python ../src/tools/utils/fft_phase.py \
        in.csv drone_log0/drone_dynamics.csv \
        --column1 c1 --column2 Vz \
        --start_time ${START_TIME} --duration ${DURATION} --target_frequency ${FREQ}  \
        --output results/result-${FREQ}/out.csv | tee results/result-${FREQ}/phase.txt

    python ../src/tools/utils/fft_amp.py \
        in.csv drone_log0/drone_dynamics.csv \
        --column1 c1 --column2 Vz \
        --start_time ${START_TIME} --duration ${DURATION} --target_frequency ${FREQ}  \
        --input_max_value 2896 | tee results/result-${FREQ}/amp.txt

    cp in.csv results/result-${FREQ}/
    cp -rp drone_log0 results/result-${FREQ}/

    python ../src/tools/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --diff --columns Vz 
}

# SIGTERMをキャッチするためのハンドラを設定
trap handler SIGTERM

mkdir -p results/result-${FREQ} 

bash ../src/tools/eval-plant.bash ${TOTAL_TIME} ${FREQ} 200 c1:1448 c2:1448 c3:1448 c4:1448 
