#!/bin/bash

DRONE_CONFIG=root/var/lib/hakoniwa/config/mixer-api/drone_config_0.json
PDU_CONFIG=root/var/lib/hakoniwa/config/custom.json
SCENARIO_CONFIG=../src/drone_evaluation/input/plant-step-input.json

source setup.bash

function handler()
{
    echo "SIGTERM"
}
trap handler SIGTERM

hako-px4sim 127.0.0.1 450 ext &
HAKO_PID=$!

sleep 1

python3.12 ../src/drone_evaluation/evaluator.py \
            ${DRONE_CONFIG} \
            ${PDU_CONFIG} \
            ${SCENARIO_CONFIG} &
EVAL_PID=$!

sleep 3

hako-cmd start

wait $EVAL_PID

kill -s TERM $HAKO_PID


