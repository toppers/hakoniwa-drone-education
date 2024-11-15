#!/bin/bash

DRONE_TEMPLATE_CONFIG=../installer/config/mixer-api/drone_config_0.json
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

if [ -f setup.bash ]
then
    source setup.bash
fi

if [ ! -z ${PYTHON_BIN} ]
then
    which python3.12
    if [ $? -eq 0 ]
    then
        PYTHON_BIN=python3.12
    else
        which python3
        if [ $? -eq 0 ]
        then
            PYTHON_BIN=python3
        else
            PYTHON_BIN=python
        fi
    fi
fi
function handler()
{
    echo "SIGTERM"
}
trap handler SIGTERM

VALUE=$(jq '.simulation.simulation_time_step' ${SCENARIO_CONFIG})
${PYTHON_BIN} ../src/drone_evaluation/update_control_params.py ${HAKO_CONTROLLER_PARAM_FILE} SIMULATION_DELTA_TIME $VALUE

${PYTHON_BIN} ../src/drone_evaluation/components/drone_config_updater.py \
    ${DRONE_TEMPLATE_CONFIG} ${DRONE_CONFIG} ${SCENARIO_CONFIG}

hako-px4sim 127.0.0.1 450 ext &
HAKO_PID=$!

sleep 1

${PYTHON_BIN} ../src/drone_evaluation/evaluator.py \
        ${DRONE_CONFIG} ${PDU_CONFIG} ${SCENARIO_CONFIG} &
EVAL_PID=$!

sleep 3

hako-cmd start

wait $EVAL_PID

kill -s TERM $HAKO_PID


