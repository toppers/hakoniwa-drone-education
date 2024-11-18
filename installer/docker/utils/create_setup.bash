#!/bin/bash

# TOP_DIR の設定 (必要に応じて適切なディレクトリに変更)
echo "ROOT_DIR: ${ROOT_DIR}"
HAKO_CONFIG_ROOT_PATH=/root/work/workspace/root
TOP_DIR="${ROOT_DIR}/usr/local"
#echo ${ROOT_DIR}

# 環境変数の定義
LD_LIBRARY_PATH_VAR="${TOP_DIR}/lib/hakoniwa:${TOP_DIR}/lib/hakoniwa/py"
PATH_VAR="${TOP_DIR}/bin/hakoniwa"
HAKO_CUSTOM_JSON_PATH_VAR="${ROOT_DIR}/var/lib/hakoniwa/config/custom.json"
PYTHONPATH_VAR="${TOP_DIR}/lib/hakoniwa:${TOP_DIR}/lib/hakoniwa/py"
DRONE_CONFIG_PATH_VAR="${HAKO_CONFIG_ROOT_PATH}/var/lib/hakoniwa/config/mixer-api"
HAKO_CONTROLLER_PARAM_FILE_VAR="${HAKO_CONFIG_ROOT_PATH}/var/lib/hakoniwa/config/param-api-mixer.txt"
#BIN_PATH
BIN_PATH_VAR="${ROOT_DIR}/usr/local/bin/hakoniwa"
#CONFIG_PATH
CONFIG_PATH_VAR="${ROOT_DIR}/var/lib/hakoniwa/config"
HAKO_CONFIG_PATH_VAR="${ROOT_DIR}/etc/hakoniwa/cpp_core_config.json"
HAKO_BINARY_PATH_VAR="${ROOT_DIR}/usr/local/lib/hakoniwa/hako_binary/offset"

# setup.bash に環境変数を追加する関数
add_to_setup() {
    local var_name="$1"
    local var_value="$2"
    
    echo "export ${var_name}=${var_value}" >> ./setup.bash
    echo "${var_name} added to setup.bash"
}
rm -f setup.bash

# 環境変数を.setupに追加 (すでに存在しない場合のみ)
add_to_setup "LD_LIBRARY_PATH" "${LD_LIBRARY_PATH_VAR}:\$LD_LIBRARY_PATH"
add_to_setup "PATH" "${PATH_VAR}:\$PATH"
add_to_setup "PYTHONPATH" "${PYTHONPATH_VAR}:\$PYTHONPATH"
add_to_setup "DRONE_CONFIG_PATH" "${DRONE_CONFIG_PATH_VAR}"
add_to_setup "HAKO_CONTROLLER_PARAM_FILE" "${HAKO_CONTROLLER_PARAM_FILE_VAR}"
add_to_setup "HAKO_CUSTOM_JSON_PATH" "${HAKO_CUSTOM_JSON_PATH_VAR}"
add_to_setup "BIN_PATH" "${BIN_PATH_VAR}"
add_to_setup "CONFIG_PATH" "${CONFIG_PATH_VAR}"
add_to_setup "HAKO_CONFIG_PATH" "${HAKO_CONFIG_PATH_VAR}"
add_to_setup "HAKO_BINARY_PATH" "${HAKO_BINARY_PATH_VAR}"
echo "Installation complete. Environment variables have been set."
