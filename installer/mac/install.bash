#!/bin/bash

script_path=$(realpath "$0")
echo "Script path: $script_path"

which sudo
if [ $? -eq 0 ]
then
    export SUDO=`which sudo`
else
    export SUDO=
fi

DIR_PATH=`(cd "$(dirname $script_path)" && pwd)`
UTILS_PATH=${DIR_PATH}/utils

# ROOT_DIR ディレクトリは好みで変えてください
CURR_DIR=`pwd`
export ROOT_DIR=${CURR_DIR}/root

bash ${UTILS_PATH}/install_env.bash
if [ $? -ne 0 ]
then
    echo "ERROR: instal_env.bash error"
    exit 1
fi
bash ${UTILS_PATH}/build_hako.bash
if [ $? -ne 0 ]
then
    echo "ERROR: build_hako.bash error"
    exit 1
fi
bash ${UTILS_PATH}/install_hako.bash
if [ $? -ne 0 ]
then
    echo "ERROR: instal_hako.bash error"
    exit 1
fi

cp ${DIR_PATH}/config/* ${ROOT_DIR}/var/lib/hakoniwa/config/

export default_core_mmap_path=${ROOT_DIR}/var/lib/hakoniwa/mmap
export config_file=${ROOT_DIR}/etc/hakoniwa/cpp_core_config.json
bash ${UTILS_PATH}/hako-mmap-set.bash -p ${ROOT_DIR}/var/lib/hakoniwa/mmap

bash ${UTILS_PATH}/create_setup.bash

(cd ../src/drone_control && rm -rf cmake-build/* && bash build.bash)
