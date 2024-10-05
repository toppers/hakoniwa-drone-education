#!/bin/bash

function handler()
{
    echo "SIGTERM"
}
trap handler SIGTERM

#bash ../src/tools/calc-gain-phase.bash 400 500 0.01
#bash ../src/tools/calc-gain-phase.bash 100 400 0.03
#bash ../src/tools/calc-gain-phase.bash 100 100 0.1
bash ../src/tools/calc-gain-phase.bash 100 100  0.2
#bash ../src/tools/calc-gain-phase.bash 100 100  0.3
bash ../src/tools/calc-gain-phase.bash 100 100  0.4
#bash ../src/tools/calc-gain-phase.bash 100 10  1
#bash ../src/tools/calc-gain-phase.bash 100 10  3
#bash ../src/tools/calc-gain-phase.bash 100 10  10
#bash ../src/tools/calc-gain-phase.bash 100 10  30
#bash ../src/tools/calc-gain-phase.bash 100 10  100
