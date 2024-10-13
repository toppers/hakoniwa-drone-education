import pandas as pd
import json
import sys

# コマンドライン引数からファイルパスと対象行を取得
if len(sys.argv) != 5:
    print("Usage: python script.py <csv_file> <config_file> <sine_input_file> <row_index>")
    sys.exit(1)

csv_file = sys.argv[1]
config_file = sys.argv[2]
sine_input_file = sys.argv[3]
row_index = int(sys.argv[4])
updated_sine_input_file = 'sine-input-updated.json'

# CSVファイルから対象行を読み込む
csv_data = pd.read_csv(csv_file)
selected_row = csv_data.iloc[row_index]

# config.jsonの読み込み
with open(config_file, 'r') as f:
    config = json.load(f)

# sine-input.jsonの読み込み
with open(sine_input_file, 'r') as f:
    sine_input = json.load(f)

# sine-input.jsonの内容を更新
input_array_len = config['input_array_len']

sine_input['simulation']['signals']['sine']['parameters']['amp'] = [
    config['amp'] for _ in range(input_array_len)
]
sine_input['simulation']['signals']['sine']['parameters']['freq'] = [
    selected_row['freq'] for _ in range(input_array_len)
]
sine_input['simulation']['signals']['sine']['parameters']['offsets'] = [
    config['offset'] for _ in range(input_array_len)
]

# config.jsonの内容を反映
sine_input['simulation']['type'] = config['type']
sine_input['evaluation']['input_data']['axis'] = config['in_axis']
sine_input['evaluation']['output_data']['axis'] = config['out_axis']

# controller_typeの設定（存在しない場合は無視）
if 'controller_type' in config:
    sine_input['simulation']['controller_type'] = config['controller_type']

sine_input['simulation']['signal_input_timings'][0]['duration_sec'] = selected_row['duration']
sine_input['evaluation']['freq_evaluation']['freq'] = selected_row['freq']
sine_input['evaluation']['freq_evaluation']['output_inverse'] = config['output_inverse']
sine_input['evaluation']['freq_evaluation']['start_time'] = selected_row['start_time']


# 更新したsine-input.jsonを保存
with open(updated_sine_input_file, 'w') as f:
    json.dump(sine_input, f, indent=2)

print(f"Updated sine-input.json has been saved to {updated_sine_input_file}")