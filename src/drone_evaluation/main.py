import sys
import os
from components.simulation_executor import SimulationExecutor

simulation_executor = None

def my_on_initialize(context):
    global simulation_executor
    simulation_executor.create_pdu()
    return 0

def my_on_manual_timing_control(context):
    global simulation_executor
    simulation_executor.run()
    return 0

def my_on_reset(context):
    return 0

my_callback = {
    'on_initialize': my_on_initialize,
    'on_simulation_step': None,
    'on_manual_timing_control': my_on_manual_timing_control,
    'on_reset': my_on_reset
}

def main():
    global simulation_executor

    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <drone_config_path> <pdu_config_path> <evaluation_config_path>")
        return 1

    simulation_executor = SimulationExecutor(sys.argv[1], sys.argv[2], sys.argv[3])
    if simulation_executor.initialize(my_callback) == False:
        return 1

    simulation_executor.start()

    return 0

if __name__ == "__main__":
    sys.exit(main())
