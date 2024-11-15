# Base image
FROM ubuntu:22.04 as hakoniwa-drone-education

# Set non-interactive environment variable
ARG DEBIAN_FRONTEND=noninteractive

# Environment variables for the PATH and LD_LIBRARY_PATH
ENV PATH /usr/local/bin/hakoniwa:${PATH}
ENV LD_LIBRARY_PATH /usr/local/lib/hakoniwa:${LD_LIBRARY_PATH}
ENV ROOT_DIR /
ENV PYTHON_BIN python3

# Install system dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    python3 \
    python3-pip\
    python3-dev \
    build-essential \
    wget \
    vim \
    libssl-dev libreadline-dev zlib1g-dev \
    autoconf \
    automake \
    pkg-config \
    curl \
    net-tools \
    netcat \
    git jq libgtest-dev \
    gcc g++ make cmake \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p ${ROOT_DIR}/etc/hakoniwa \
    ${ROOT_DIR}/var/lib/hakoniwa/mmap \
    ${ROOT_DIR}/var/lib/hakoniwa/config \
    ${ROOT_DIR}/usr/local/lib/hakoniwa \
    ${ROOT_DIR}/usr/local/bin/hakoniwa \
    ${ROOT_DIR}/usr/local/include/hakoniwa \
    ${ROOT_DIR}/usr/local/lib/hakoniwa/hako_binary \
    ${ROOT_DIR}/usr/local/lib/hakoniwa/py \
    ${ROOT_DIR}/usr/local/lib/hakoniwa/py/hako_binary

# Set the working directory
WORKDIR /root/workspace

# Clone the necessary repositories
RUN git clone -b main https://github.com/toppers/hakoniwa-px4sim.git || echo "hakoniwa-px4sim is already cloned."

# Initialize and update submodules
WORKDIR /root/workspace/hakoniwa-px4sim/hakoniwa
RUN git submodule init third-party/hakoniwa-core-cpp-client && \
    git submodule update --recursive third-party/hakoniwa-core-cpp-client && \
    cd third-party/hakoniwa-core-cpp-client && \
    git submodule init core && \
    git submodule update --recursive core && \
    cd ../.. && \
    git submodule init third-party/glm && \
    git submodule update --recursive third-party/glm && \
    git submodule init third-party/c_library_v2 && \
    git submodule update --recursive third-party/c_library_v2 && \
    git submodule init third-party/hakoniwa-ros2pdu && \
    git submodule update --recursive third-party/hakoniwa-ros2pdu

# Build px4sim
RUN bash build.bash

# Install hakoniwa components
RUN HAKO_CORE_BUILD_DIR=cmake-build/third-party/hakoniwa-core-cpp-client && \
    cp ${HAKO_CORE_BUILD_DIR}/core/sample/base-procs/hako-cmd/hako-cmd ${ROOT_DIR}/usr/local/bin/hakoniwa/ && \
    cp ${HAKO_CORE_BUILD_DIR}/src/proxy/hako-proxy ${ROOT_DIR}/usr/local/bin/hakoniwa/ && \
    cp ${HAKO_CORE_BUILD_DIR}/src/hakoc/libhakoarun.* ${ROOT_DIR}/usr/local/lib/hakoniwa/ && \
    cp ${HAKO_CORE_BUILD_DIR}/src/hakoc/libshakoc.* ${ROOT_DIR}/usr/local/lib/hakoniwa/ && \
    cp ${HAKO_CORE_BUILD_DIR}/src/hakoc/libshakoc.* ${ROOT_DIR}/usr/local/lib/hakoniwa/hakoc.so && \
    cp ${HAKO_CORE_BUILD_DIR}/src/assets/libassets.* ${ROOT_DIR}/usr/local/lib/hakoniwa/ && \
    cp ${HAKO_CORE_BUILD_DIR}/src/conductor/libconductor.* ${ROOT_DIR}/usr/local/lib/hakoniwa/ && \
    cp ${HAKO_CORE_BUILD_DIR}/bindings/python/libhako_asset_python.so ${ROOT_DIR}/usr/local/lib/hakoniwa/py/hakopy.so && \
    cp /root/workspace/hakoniwa-px4sim/hakoniwa/third-party/hakoniwa-core-cpp-client/core/cpp_core_config.json ${ROOT_DIR}/etc/hakoniwa/cpp_core_config.json

# Install headers and Python bindings
WORKDIR /root/workspace
RUN cp hakoniwa-px4sim/hakoniwa/third-party/hakoniwa-core-cpp-client/src/include/*.h ${ROOT_DIR}/usr/local/include/hakoniwa/ && \
    cp -rp hakoniwa-px4sim/hakoniwa/third-party/hakoniwa-core-cpp-client/bindings/python/hako_binary/offset ${ROOT_DIR}/usr/local/lib/hakoniwa/hako_binary/ && \
    cp -rp hakoniwa-px4sim/hakoniwa/third-party/hakoniwa-core-cpp-client/bindings/python/hako_binary/*.py ${ROOT_DIR}/usr/local/lib/hakoniwa/py/hako_binary/ && \
    cp hakoniwa-px4sim/hakoniwa/third-party/hakoniwa-core-cpp-client/bindings/python/hako_pdu.py ${ROOT_DIR}/usr/local/lib/hakoniwa/py/

# Set directory permissions
RUN chmod -R 755 ${ROOT_DIR}/var/lib/hakoniwa

# Install hako-px4sim and drone_api
RUN cp -rp hakoniwa-px4sim/hakoniwa/third-party/hakoniwa-ros2pdu/pdu/offset ${ROOT_DIR}/usr/local/lib/hakoniwa/hako_binary/ && \
    cp hakoniwa-px4sim/hakoniwa/cmake-build/src/hako-px4sim ${ROOT_DIR}/usr/local/bin/hakoniwa/ && \
    cp hakoniwa-px4sim/drone_api/libs/*.py ${ROOT_DIR}/usr/local/lib/hakoniwa/py/


COPY requirements.txt /root/requirements.txt
RUN pip3 install -r /root/requirements.txt

ENV PYTHONPATH /root/work/src:/root/work/src/drone_evaluation:/root/work/src/drone_evaluation/components:${PYTHONPATH}

# Add initialization script
COPY docker/init_script.sh /root/init_script.sh

# Add entrypoint to run initialization script once
RUN chmod +x /root/init_script.sh
# Use CMD to run init_script.sh and keep shell open after it completes
CMD ["/bin/bash", "-c", "/root/init_script.sh && exec /bin/bash"]

# Expose necessary ports if required
EXPOSE 8000