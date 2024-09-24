#!/bin/bash
trap 'kill 0' EXIT

if [ -z "${HAKO_CUSTOM_JSON_PATH}" ]
then
    echo "ERROR: HAKO_CUSTOM_JSON_PATH is not defined"
    exit 1
fi
if [ -z "${DRONE_CONFIG_PATH}" ]
then
    echo "ERROR: DRONE_CONFIG_PATH is not defined"
    exit 1
fi
if [ -z "${HAKO_CONTROLLER_PARAM_FILE}" ]
then
    echo "ERROR: HAKO_CONTROLLER_PARAM_FILE is not defined"
    exit 1
fi
if [ -z "${PYTHON_BIN}" ]
then
    echo "ERROR: PYTHON_BIN is not defined"
    exit 1
fi
if [ -z "${BIN_PATH}" ]
then
    echo "ERROR: BIN_PATH is not defined"
    exit 1
fi
if [ -z "${TOOL_PATH}" ]
then
    echo "ERROR: TOOL_PATH is not defined"
    exit 1
fi
if [ -z "${CONFIG_PATH}" ]
then
    echo "ERROR: CONFIG_PATH is not defined"
    exit 1
fi

EXEC_SIM_TIME=5

HAKO_PID=
EVAL_PID=
if [ $# -ne 3 -a $# -ne 4 ]
then
    echo "Usage: $0 <stop_time> <tkey:tvalue> <key:value> <S:targetSpeed>"
    exit 1
fi
if [ ${1} -gt 0 ]
then
    STOP_TIME=`expr ${1} \* 1000000`
else
    STOP_TIME=-1
fi

SPEED_KEY_VALUE=
if [ $# -eq 4 ]
then
    SPEED_KEY_VALUE=${4}
endif

TKEY_VALUE=${2}
KEY_VALUE=${3}
TKEY=`echo ${TKEY_VALUE} | awk -F: '{print $1}'`
TVALUE=`echo ${TKEY_VALUE} | awk -F: '{print $2}'`

KEY=`echo ${KEY_VALUE} | awk -F: '{print $1}'`
VALUE=`echo ${KEY_VALUE} | awk -F: '{print $2}'`

if [ "$TKEY" = "Rx" ] || [ "$TKEY" = "Ry" ]
then
    VAL=true
else
    VAL=false
fi

cp ${CONFIG_PATH}/control_evaluate_sample.json ./tmp1.json
jq --argjson value ${VAL} '.CONVERT_TO_DEGREE = $value' ./tmp1.json > ${CONFIG_PATH}/control_evaluate_sample.json
rm -f ./tmp1.json


# start hakoniwa
${BIN_PATH}/hako-px4sim 127.0.0.1 4560 ext &
HAKO_PID=$!

# start eval-ctrl
${PYTHON_BIN} ${TOOL_PATH}/eval-ctrl.py ${HAKO_CUSTOM_JSON_PATH} ${STOP_TIME} ${TKEY_VALUE} ${KEY_VALUE} ${SPEED_KEY_VALUE} &
EVAL_PID=$!

sleep 1

# hako start
hako-cmd start

cat ./tmp.json

sleep ${EXEC_SIM_TIME}

# kill hakoniwa
kill -s TERM ${HAKO_PID}

# kill eval-ctrl
kill -s TERM ${EVAL_PID}

jq --arg axis "$TKEY" --argjson value "$TVALUE" '.AXIS = $axis | .TARGET_VALUE = $value' ${CONFIG_PATH}/control_evaluate_sample.json > ./tmp.json

START_TIME=`cat /tmp/v.txt`
cp ./tmp.json ./tmp1.json
jq --argjson value "$START_TIME" '.EVALUATION_START_TIME = $value' ./tmp1.json > ./tmp.json
rm -f ./tmp1.json

# evaluation
${PYTHON_BIN} ${TOOL_PATH}/control_evaluate.py ./drone_log0/drone_dynamics.csv ./tmp.json

wait ${HAKO_PID} ${EVAL_PID}

echo "INFO: DONE"
