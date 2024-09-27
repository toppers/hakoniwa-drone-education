#!/bin/bash
trap 'kill 0' EXIT

# Get the real path of the script
script_path=$(realpath "$0")
echo "Script path: $script_path"

# Define tool path
TOOL_PATH=$(cd "$(dirname "$script_path")" && pwd)

# Error handling function
error_exit() {
    echo "ERROR: $1 is not defined"
    exit 1
}

# Check if required environment variables are set
[ -z "${HAKO_CUSTOM_JSON_PATH}" ] && error_exit "HAKO_CUSTOM_JSON_PATH"
[ -z "${DRONE_CONFIG_PATH}" ] && error_exit "DRONE_CONFIG_PATH"
[ -z "${PYTHON_BIN}" ] && error_exit "PYTHON_BIN"
[ -z "${BIN_PATH}" ] && error_exit "BIN_PATH"
[ -z "${CONFIG_PATH}" ] && error_exit "CONFIG_PATH"

# Start hako-px4sim in the background
echo "INFO: start hakoniwa drone simulator"
${BIN_PATH}/hako-px4sim 127.0.0.1 4560 replay &
HAKO_PID=${!}
sleep 1

# Change directory and start realtime syncher
echo "INFO: start hakoniwa asset(real time syncher)"
CURR_DIR=$(pwd)
cd hakoniwa-px4sim/drone_api/sample
${PYTHON_BIN} ${TOOL_PATH}/real_time_syncher.py ${HAKO_CUSTOM_JSON_PATH} 20 &
SYNC_PID=${!}
sleep 1
cd ${CURR_DIR}

# Wait for services to start
sleep 3

# Change directory and start the web server
export HAKO_CUSTOM_JSON_PATH=$(pwd)/hakoniwa-webserver/config/custom.json
echo "INFO: start hakoniwa asset(web server)"
CURR_DIR=$(pwd)
cd hakoniwa-webserver
${PYTHON_BIN} server/main.py --asset_name WebServer --config_path ${HAKO_CUSTOM_JSON_PATH} --delta_time_usec 20000 &
WEB_PID=${!}
sleep 1
cd ${CURR_DIR}

# Start services
echo "Press ENTER to start the services"
read
hako-cmd start

sleep 3

# Loop for restart or exit
while true; do
    echo "Type 'restart' to restart the services or 'exit' to stop and exit:"
    read input

    case $input in
        restart)
            echo "INFO: restarting services..."
            hako-cmd stop
            sleep 1
            hako-cmd reset
            sleep 1
            hako-cmd start
            sleep 3
            ;;
        exit)
            echo "INFO: stopping services..."
            # Terminate the processes
            kill -s TERM ${HAKO_PID} ${SYNC_PID} ${WEB_PID}
            # Wait for processes to exit
            wait
            break
            ;;
        *)
            echo "Invalid input. Please type 'restart' or 'exit'."
            ;;
    esac
done
