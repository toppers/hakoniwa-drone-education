#!/bin/bash
trap 'kill 0' EXIT

script_path=$(realpath "$0")
echo "Script path: $script_path"

TOOL_PATH=`(cd "$(dirname $script_path)" && pwd)`


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
if [ -z "${CONFIG_PATH}" ]
then
    echo "ERROR: CONFIG_PATH is not defined"
    exit 1
fi

EXEC_SIM_TIME=5

HAKO_PID=
EVAL_PID=
if [ $# -ne 5 ]
then
    echo "Usage: $0 <stop_time> <tkey:tvalue> <key:value> <key:value> <key:value>"
    exit 1
fi

STOP_TIME=${1}
TKEY_VALUE=${2}
KEY_VALUE1=${3}
KEY_VALUE2=${4}
KEY_VALUE3=${5}
TKEY=`echo ${TKEY_VALUE} | awk -F: '{print $1}'`
TVALUE=`echo ${TKEY_VALUE} | awk -F: '{print $2}'`

KEY1=`echo ${KEY_VALUE1} | awk -F: '{print $1}'`
VALUE1=`echo ${KEY_VALUE1} | awk -F: '{print $2}'`

KEY2=`echo ${KEY_VALUE2} | awk -F: '{print $1}'`
VALUE2=`echo ${KEY_VALUE2} | awk -F: '{print $2}'`

KEY3=`echo ${KEY_VALUE3} | awk -F: '{print $1}'`
VALUE3=`echo ${KEY_VALUE3} | awk -F: '{print $2}'`


module_name="PlantController"
new_path="../src/drone_control/cmake-build/workspace/${module_name}"
drone_config_file="${DRONE_CONFIG_PATH}/drone_config_0.json"
cp ${drone_config_file} ./tmp1.json
# --arg を使って文字列として渡す
jq --arg new_path "$new_path" \
    --arg module_name "$module_name" \
    '.controller.moduleName = $module_name | .controller.moduleDirectory = $new_path' \
    ./tmp1.json > ${drone_config_file}
rm tmp1.json

# start hakoniwa
${BIN_PATH}/hako-px4sim 127.0.0.1 4560 ext &
HAKO_PID=$!

# start eval-ctrl
${PYTHON_BIN} ${TOOL_PATH}/eval-plant.py ${HAKO_CUSTOM_JSON_PATH} ${STOP_TIME} ${TKEY_VALUE} ${KEY_VALUE1} ${KEY_VALUE2} ${KEY_VALUE3} &
EVAL_PID=$!

sleep 3

# hako start
hako-cmd start

#sleep ${EXEC_SIM_TIME}

wait $EVAL_PID

# kill hakoniwa
kill -s TERM ${HAKO_PID}


#wait ${HAKO_PID} ${EVAL_PID}
wait ${HAKO_PID}
echo "INFO: DONE"
