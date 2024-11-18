import json
import os
import argparse

def load_json(file_path):
    """JSONファイルを読み込む"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Error: {file_path} が存在しません")
    
    with open(file_path, 'r') as file:
        return json.load(file)

def merge_json_files(base_dir, config_path):
    """指定されたJSONファイルを読み込んでマージする"""
    print(f"base_dir: {base_dir} config_file: {config_path}")
    config_data = load_json(config_path)
    
    merged_data = {}

    # plantsのJSONファイルを配列として読み込む
    if 'plants' in config_data:
        merged_data['plants'] = []
        for json_file in config_data['plants']:
            print(f"json_file: {json_file}")
            json_path = os.path.join(base_dir, 'plants', json_file)
            try:
                merged_data['plants'].append(load_json(json_path))
            except FileNotFoundError as e:
                print(e)

    # controllersのJSONファイルを配列として読み込む
    if 'controllers' in config_data:
        merged_data['controllers'] = []
        for json_file in config_data['controllers']:
            json_path = os.path.join(base_dir, 'controllers', json_file)
            try:
                merged_data['controllers'].append(load_json(json_path))
            except FileNotFoundError as e:
                print(e)

    # constantsのJSONファイルをそのまま展開
    if 'constants' in config_data:
        merged_data['constants'] = {}
        for json_file in config_data['constants']:
            json_path = os.path.join(base_dir, 'constants', json_file)
            try:
                merged_data['constants'].update(load_json(json_path))
            except FileNotFoundError as e:
                print(e)
    # pd_argsのJSONファイルをそのまま展開
    if 'pd_args' in config_data:
        merged_data['pd_args'] = config_data['pd_args']

    return merged_data

def save_json(data, output_file):
    """展開後のJSONデータをファイルに保存する"""
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    parser = argparse.ArgumentParser(description='alt_control.jsonを読み込み展開する')
    parser.add_argument('base_dir', help='base_modelsのディレクトリ')
    parser.add_argument('config_file', help='展開するcombined modelのパス')
    parser.add_argument('output_file', help='展開後のJSONファイルの出力先')

    args = parser.parse_args()

    # alt_control.jsonのディレクトリを取得
    base_dir = args.base_dir

    try:
        # alt_control.jsonを展開してマージ
        merged_data = merge_json_files(base_dir, args.config_file)

        # 展開後のJSONを保存
        save_json(merged_data, args.output_file)
        print(f"展開後のJSONファイルを {args.output_file} に保存しました")
    
    except FileNotFoundError as e:
        print(e)

if __name__ == '__main__':
    main()
