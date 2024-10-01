#!/bin/bash

# SIGTERMをキャッチするためのハンドラを設定
trap handler SIGTERM

TOOL_PATH=$(dirname $(realpath ${0}))

# シグナルハンドラ
function handler()
{
    # Z軸のプロット
    python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Z --diff
    if [ $? -eq 0 ]; then
        mv plot.png plot_z.png
    fi

    # Rx軸のプロット
    python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Rx --diff
    if [ $? -eq 0 ]; then
        mv plot.png plot_rx.png
    fi

    # Ry軸のプロット
    python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Ry --diff
    if [ $? -eq 0 ]; then
        mv plot.png plot_ry.png
    fi

    # Rz軸のプロット
    python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Rz --diff
    if [ $? -eq 0 ]; then
        mv plot.png plot_rz.png
    fi

    # 最後にプロット集計
    python ${TOOL_PATH}/plots.py
    rm -f *.png
}

# 引数のチェック
if [ $# -ne 3 -a $# -ne 4 ]
then
    echo "Usage: $0 <Rx:angle> <Ry:angle> <Rz:angle> [stop]"
    exit 1
fi

# 引数を設定
ARG1=${1}
ARG2=${2}
ARG3=${3}
ARG4=${4}

# eval-ctrlをバックグラウンドで実行し、そのPIDを待つ
WAIT_PID=
if [ $# -eq 3 ]
then
    bash ${TOOL_PATH}/eval-ctrl.bash -1 ${ARG1} ${ARG2} ${ARG3} &
    WAIT_PID=$!
else
    bash ${TOOL_PATH}/eval-ctrl.bash ${ARG4} ${ARG1} ${ARG2} ${ARG3} &
    WAIT_PID=$!
fi

# バックグラウンドプロセスを待機
wait $WAIT_PID
