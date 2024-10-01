#!/bin/bash

# SIGTERMをキャッチするためのハンドラを設定
trap handler SIGTERM

TOOL_PATH=$(dirname $(realpath ${0}))
KEY="X"
# シグナルハンドラ
function handler()
{
    # Z軸のプロット
    python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Z --diff
    if [ $? -eq 0 ]; then
        mv plot.png plot_z.png
    fi
    if [ $KEY = "X" ]
    then
        # X軸のプロット
        python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns X --diff
        if [ $? -eq 0 ]; then
            mv plot.png plot_x.png
        fi
        # Vx軸のプロット
        python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Vx --diff
        if [ $? -eq 0 ]; then
            mv plot.png plot_vx.png
        fi
    fi
    if [ $KEY = "Y" ]
    then
        # Y軸のプロット
        python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Y --diff
        if [ $? -eq 0 ]; then
            mv plot.png plot_y.png
        fi
        # Vy軸のプロット
        python ${TOOL_PATH}/hako_TimelineAnalyzer.py ./drone_log0/drone_dynamics.csv --columns Vy --diff
        if [ $? -eq 0 ]; then
            mv plot.png plot_vy.png
        fi
    fi

    # 最後にプロット集計
    python ${TOOL_PATH}/plots.py
    rm -f *.png

}


# 引数のチェック
if [ $# -ne 4 -a $# -ne 5 ]
then
    echo "Usage: $0 <X:x> <Y:y> <Z:z> <S:speed> [stop]"
    exit 1
fi

# 引数を設定
ARG1=${1}
ARG2=${2}
ARG3=${3}
ARG4=${4}
ARG4=${5}

KEY=$(echo $ARG1 | awk -F: '{print $1}')

# eval-ctrlをバックグラウンドで実行し、そのPIDを待つ
WAIT_PID=
if [ $# -eq 4 ]
then
    bash ${TOOL_PATH}/eval-ctrl.bash -1 ${ARG1} ${ARG2} ${ARG3} ${ARG4} &
    WAIT_PID=$!
else
    bash ${TOOL_PATH}/eval-ctrl.bash ${ARG5} ${ARG1} ${ARG2} ${ARG3} ${ARG4} &
    WAIT_PID=$!
fi

# バックグラウンドプロセスを待機
wait $WAIT_PID

