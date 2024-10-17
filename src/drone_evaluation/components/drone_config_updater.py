import json
import argparse

class DroneConfigUpdater:
    def __init__(self, file_path):
        self.file_path = file_path
        self.base_path = "../src/drone_control/cmake-build/workspace/"
        try:
            with open(self.file_path, 'r') as file:
                self.params = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {self.file_path} was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"The file at {self.file_path} is not a valid JSON file.")

    def set_simulation_time_step(self, simulation_time_step):
        self.params['simulation']['timeStep'] = simulation_time_step

    def set_plant_module(self):
        module_name = 'PlantController'
        self.params['controller'].pop('mixer', None)  # mixerを削除
        self.params['controller']['direct_rotor_control'] = True
        self.params['controller']['moduleDirectory'] = self.base_path + module_name
        self.params['controller']['moduleName'] = module_name

    def set_controller_module(self, controller_type):
        valid_types = ['angle', 'spd', 'spd_z', 'pos', 'pos_z']
        if controller_type not in valid_types:
            raise ValueError(f"Unsupported controller type: {controller_type}. Valid types are: {valid_types}")
        
        if controller_type == 'angle':
            module_name = 'AngleController'
        elif controller_type == 'spd':
            module_name = 'SpeedController'
        elif controller_type == 'spd_z':
            module_name = 'AltSpeedController'
        elif controller_type == 'pos':
            module_name = 'PositionController'
        elif controller_type == 'pos_z':
            module_name = 'PositionController'

        self.params['components']['droneDynamics'].pop('out_of_bounds_reset', None)
        self.params['controller']['direct_rotor_control'] = False
        self.params['controller']['moduleDirectory'] = self.base_path + module_name
        self.params['controller']['moduleName'] = module_name

    def save(self, output_filepath):
        """現在の設定を指定されたファイルに保存"""
        with open(output_filepath, 'w') as outfile:
            json.dump(self.params, outfile, indent=4)

def validate_evaluation_config(eval_config):
    """evaluation_config_file の検証"""
    if 'simulation' not in eval_config:
        raise KeyError("Missing 'simulation' key in evaluation config")
    
    if 'type' not in eval_config['simulation']:
        raise KeyError("Missing 'type' in 'simulation' section")
    
    if eval_config['simulation']['type'] not in ['plant', 'controller']:
        raise ValueError("Invalid 'simulation' type. Expected 'plant' or 'controller'.")
    
    if eval_config['simulation']['type'] != 'plant' and 'controller_type' not in eval_config['simulation']:
        raise KeyError("Missing 'controller_type' in 'simulation' when type is not 'plant'")

def main():
    # コマンドライン引数の処理
    parser = argparse.ArgumentParser(description='Update drone configuration.')
    parser.add_argument('template_file', help='Path to the template configuration JSON file.')
    parser.add_argument('output_file', help='Path to save the updated configuration JSON file.')
    parser.add_argument('evaluation_config_file', help='Path to the evaluation configuration JSON file.')
    
    args = parser.parse_args()
    
    # DroneConfigUpdaterを初期化
    updater = DroneConfigUpdater(args.template_file)
    
    # evaluation_config_file の読み込みとバリデーション
    try:
        with open(args.evaluation_config_file, 'r') as eval_file:
            eval_config = json.load(eval_file)
            print("Loaded evaluation configuration:", eval_config)
            
            # eval_config の検証
            validate_evaluation_config(eval_config)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file at {args.evaluation_config_file} was not found.")
    except json.JSONDecodeError:
        raise ValueError(f"The file at {args.evaluation_config_file} is not a valid JSON file.")
    except KeyError as e:
        raise KeyError(f"Missing key in evaluation config: {e}")
    except ValueError as e:
        raise ValueError(f"Error in evaluation config: {e}")
    
    # シミュレーション設定に基づいてモジュールを設定
    if eval_config['simulation']['type'] == 'plant':
        updater.set_plant_module()
    else:
        updater.set_controller_module(eval_config['simulation']['controller_type'])
    
    updater.set_simulation_time_step(eval_config['simulation']['simulation_time_step'])

    # 設定をファイルに保存
    updater.save(args.output_file)
    print(f"Configuration saved to {args.output_file}")

if __name__ == "__main__":
    main()
