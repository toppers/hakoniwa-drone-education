import sys
import os

def modify_simulation_delta_time(file_path, target_item_name, new_value):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    # Try to read and process the file
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    item_found = False
    
    # Modify the line containing the target item
    for i, line in enumerate(lines):
        # Skip lines that start with a comment
        if line.strip().startswith("#"):
            continue
        # Check if the target item is in the line
        if target_item_name in line:
            lines[i] = f"{target_item_name}   {new_value}\n"
            item_found = True
            break
    
    # If the target item was not found, exit with an error
    if not item_found:
        print(f"Error: Target item '{target_item_name}' not found in the file.")
        sys.exit(1)
    
    # Try to write the modified content back to the file
    try:
        with open(file_path, 'w') as file:
            file.writelines(lines)
        print(f"Updated {target_item_name} to {new_value} in '{file_path}'.")
    except Exception as e:
        print(f"Error writing to file: {e}")
        sys.exit(1)

# コマンドライン引数からファイルパスと対象行を取得
if len(sys.argv) != 4:
    print("Usage: python script.py <param_file> <target_item> <new_value>")
    sys.exit(1)

file_path = sys.argv[1]
target_item_name = sys.argv[2]

# Validate and convert new_value to float
try:
    new_value = float(sys.argv[3])
except ValueError:
    print(f"Error: '{sys.argv[3]}' is not a valid number.")
    sys.exit(1)

modify_simulation_delta_time(file_path, target_item_name, new_value)
