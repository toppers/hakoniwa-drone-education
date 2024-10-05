#!/bin/bash

if [ $# -ne 5 ]
then
    echo "Usage: $0 <start> <duration> <in-file> <out-file> <out-column>"
    exit 1
fi

START_TIME=${1}
DURATION=${2}
IN_FILE_PATH=${3}
OUT_FILE_PATH=${4}
COLNAME=${5}

# filoter
python ../src/tools/filter_data.py ${IN_FILE_PATH}  ${START_TIME} ${DURATION} c1 input.csv
python ../src/tools/filter_data.py ${OUT_FILE_PATH} ${START_TIME} ${DURATION} ${COLNAME} output.csv

# plot
python ../src/tools/hako_TimelineAnalyzer.py  input.csv output.csv  --diff --columns input.c1 output.${COLNAME}  --diff --duration ${DURATION}
