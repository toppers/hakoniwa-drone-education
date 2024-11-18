import json
import math
import argparse
import re
import math
from pathlib import Path


def load_pid_config(pid_file_path):
    """Load config_pid data from the specified file."""
    pid_config = {}
    with open(pid_file_path, 'r') as file:
        for line in file:
            # 空行をスキップ
            if not line.strip():
                continue
            # コメント行をスキップ
            if line.startswith("#"):
                continue
            key, value = line.strip().split(maxsplit=1)
            pid_config[key] = float(value)
    return pid_config


def get_from_json(json_data, path):
    """Retrieve a value from a JSON structure using a dotted path, supporting array indexing."""
    keys = path.split('.')
    value = json_data
    for key in keys:
        if '[' in key and ']' in key:  # Check if the key includes array indexing
            base_key, index = key.split('[')
            index = int(index[:-1])  # Convert index string (e.g., "0]") to integer
            value = value[base_key][index]
        else:
            value = value[key]
    return value


def calculate_values(config, pid_config, drone_config):
    """Expand and calculate values based on the input configuration."""
    expanded = {}

    # Step 1: Handle "config_pid" and "config_drone" keys
    for key, path in config.items():
        if path.startswith("config_pid:"):
            pid_key = path.split("config_pid:")[1]
            expanded[key] = pid_config[pid_key]
        elif path.startswith("config_drone:"):
            drone_path = path.split("config_drone:")[1]
            expanded[key] = get_from_json(drone_config, drone_path)
            print(f"drone_path: {drone_path} key: {key} value: {expanded[key]}")
        elif path.startswith("value:"):
            expanded[key] = float(path.split("value:")[1])

def calculate_values(config, pid_config, drone_config):
    """Expand and calculate values based on the input configuration."""
    expanded = {}

    # Step 1: Handle "config_pid" and "config_drone" keys
    for key, path in config.items():
        if path.startswith("config_pid:"):
            pid_key = path.split("config_pid:")[1]
            expanded[key] = pid_config[pid_key]
        elif path.startswith("config_drone:"):
            drone_path = path.split("config_drone:")[1]
            expanded[key] = get_from_json(drone_config, drone_path)
        elif path.startswith("value:"):
            expanded[key] = float(path.split("value:")[1])

    # Step 2: Handle "calc" keys
    for key, formula in config.items():
        if formula.startswith("calc:"):
            expression = formula.split("calc:")[1]

            # Replace only variables that exist in the expanded dictionary
            def replace_var(match):
                var_name = match.group(0)
                if var_name in expanded:
                    return f"({expanded[var_name]})"
                return var_name  # Keep it unchanged if not in expanded

            # Replace variables in the expression
            expression = re.sub(r'\b[a-zA-Z_][a-zA-Z_0-9]*\b', replace_var, expression)

            # Evaluate the expression, passing the math module to eval
            expanded[key] = eval(expression, {"math": math, "__builtins__": {}})

    return expanded



def main():
    parser = argparse.ArgumentParser(description="Expand and calculate values from config files.")
    parser.add_argument("pid_file_path", type=str, help="Path to the config_pid file.")
    parser.add_argument("drone_file_path", type=str, help="Path to the config_drone JSON file.")
    parser.add_argument("config_file_path", type=str, help="Path to the input config JSON file.")
    parser.add_argument("output_file_path", type=str, help="Path to save the output JSON file.")

    args = parser.parse_args()

    # Load input files
    pid_file_path = Path(args.pid_file_path)
    drone_file_path = Path(args.drone_file_path)
    config_file_path = Path(args.config_file_path)
    output_file_path = Path(args.output_file_path)

    if not pid_file_path.is_file() or not drone_file_path.is_file() or not config_file_path.is_file():
        print("Error: One or more file paths are invalid.")
        return

    pid_config = load_pid_config(pid_file_path)
    with open(drone_file_path, 'r') as file:
        drone_config = json.load(file)

    with open(config_file_path, 'r') as file:
        config = json.load(file)

    # Calculate expanded and derived values
    results = calculate_values(config, pid_config, drone_config)

    # Dump results to JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(results, output_file, indent=4)
    print(f"Results have been saved to {output_file_path}")


if __name__ == "__main__":
    main()
