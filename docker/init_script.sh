#!/bin/bash

# Get the directory path from the script_path
UTILS_PATH=/root/work/installer/docker/utils

# Set up mmap
export default_core_mmap_path=${ROOT_DIR}/var/lib/hakoniwa/mmap
export config_file=${ROOT_DIR}/etc/hakoniwa/cpp_core_config.json
bash ${UTILS_PATH}/hako-mmap-set.bash -p ${default_core_mmap_path}

# Run additional setup
bash ${UTILS_PATH}/create_setup.bash

# The setup.bash will be created in the current directory
# Ensure setup.bash is sourced in .bashrc for login
if [ -f ./setup.bash ]; then
    echo 'source /root/work/setup.bash' >> ~/.bashrc
fi

cd /root/work/src/drone_control
bash build.bash