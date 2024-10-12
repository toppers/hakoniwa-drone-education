#!/bin/bash

DRONE_TEMPLATE_CONFIG=../src/drone_evaluation/template/drone_config.json
DRONE_CONFIG=root/var/lib/hakoniwa/config/mixer-api/drone_config_0.json
PDU_CONFIG=root/var/lib/hakoniwa/config/custom.json

if [ $# -ne 1 ]
then
    echo "Usage: $0 <scenario_config_path>"
    exit 1
fi
SCENARIO_CONFIG=${1}

if [ ! -f ${SCENARIO_CONFIG} ]
then
    echo "ERROR: can not found ${SCENARIO_CONFIG}"
    exit 1
fi

source setup.bash

function handler()
{
    echo "SIGTERM"
}
trap handler SIGTERM

python ../src/drone_evaluation/components/drone_config_updater.py \
    ${DRONE_TEMPLATE_CONFIG} ${DRONE_CONFIG} ${SCENARIO_CONFIG}

hako-px4sim 127.0.0.1 450 ext &
HAKO_PID=$!

sleep 1

python3.12 ../src/drone_evaluation/evaluator.py \
            ${DRONE_CONFIG} ${PDU_CONFIG} ${SCENARIO_CONFIG} &
EVAL_PID=$!

sleep 3

hako-cmd start

wait $EVAL_PID

kill -s TERM $HAKO_PID


