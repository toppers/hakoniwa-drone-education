#!/bin/bash

# Get the directory path from the script_path
DIR_PATH=`pwd`/installer/linux
UTILS_PATH=${DIR_PATH}/utils

# Copy config files
cp workspace/hakoniwa-px4sim/hakoniwa/third-party/hakoniwa-core-cpp-client/core/cpp_core_config.json ${ROOT_DIR}/etc/hakoniwa/cpp_core_config.json
#cp -rp ${DIR_PATH}/config/* ${ROOT_DIR}/var/lib/hakoniwa/config/

# Set up mmap
export default_core_mmap_path=${ROOT_DIR}/var/lib/hakoniwa/mmap
export config_file=${ROOT_DIR}/etc/hakoniwa/cpp_core_config.json
bash ${UTILS_PATH}/hako-mmap-set.bash -p ${default_core_mmap_path}

# Run additional setup
bash ${UTILS_PATH}/create_setup.bash

# The setup.bash will be created in the current directory
# Ensure setup.bash is sourced in .bashrc for login
if [ -f ./setup.bash ]; then
    echo 'source /root/workspace/setup.bash' >> ~/.bashrc
fi
