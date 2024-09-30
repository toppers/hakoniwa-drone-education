#!/bin/bash

if [ $# -ne 1 ]
then
    echo "Usage: $0 <model file>"
    exit 1
fi
MODEL_FILE=${1}

python ./src/libs/expand_json.py ${MODEL_FILE} out.json
python ./src/libs/analyze_model.py out.json --mode bode ls
python ./src/libs/analyze_model.py out.json --mode step ws
python ./src/libs/analyze_model.py out.json --mode impulse ws
python ./src/libs/analyze_model.py out.json --mode poles ws
python ./src/tools/plots.py 