# hakoniwa-drone-education



# 箱庭ドローンシミュレータの環境構築手順

- サポート範囲：
  - Nativeマシン
    - MacOS(AppleSilicon/Intel)
    - Ubuntu 22.0.4
    - Windows/WSL2


本リポジトリーをクローンします。

```bash
git clone https://github.com/toppers/hakoniwa-drone-education.git
```

ワークスペースを作ります。

```bash
cd hakoniwa-drone-education && mkdir workspace
```

ワークスペースに移動します。

```bash
cd workspace
```

インストーラを起動します。

```
bash ../installer/install.bash
```

インストールが成功すると、以下のようになります。

```bash
% ls
hakoniwa-px4sim         hakoniwa-webserver      root                    setup.bash              static.webgl.zip
```

箱庭ドローンシミュレータのバイナリやコンフィグファイル類は、すべて `root` に入っています。
`setup.bash` は、環境変数定義ファイルです。ツール利用する際に `source` してください。

# シミュレーション評価時の準備

シミュレーション定義ファイルを作成します。

例：src/drone_evaluation/input/spd_z-step-input.json
```json
{
  "simulation": {
    "simulation_time_step": 0.001,
    "type": "controller",
    "controller_type": "spd_z",
    "signals": {
      "step1": {
        "type": "step",
        "parameters": {
          "comment": "target speed z : 1 m/sec",
          "offsets": [ 1 ]
        }
      },
      "step2": {
        "type": "step",
        "parameters": {
          "comment": "target speed z : 0 m/sec",
          "offsets": [ 0 ]
        }
      },
      "step3": {
        "type": "step",
        "parameters": {
          "comment": "target speed z : 1 m/sec",
          "offsets": [ 1 ]
        }
      }
    },
    "signal_input_timings": [
      {
        "name": "step1",
        "duration_sec": 99.0
      },
      {
        "name": "step2",
        "duration_sec": 100.0
      },
      {
        "name": "step3",
        "duration_sec": 100.0
      }
    ]
  },
  "evaluation": {
    "step_evaluation": {
      "config_params": {
        "AXIS": "Vz",
        "INVERT_AXIS": true,
        "EVALUATION_START_TIME": 200.0,
        "CONVERT_TO_DEGREE": false
      },
      "target_params": {
          "TARGET_TR": 2.0,
          "TARGET_TD": 1.01,
          "TARGET_OS": 0.04,
          "TARGET_TS": 5.49,
          "TARGET_VALUE": 1.0
      }
    },
    "input_data": {
      "log_file": "in.csv",
      "cache_len": 1024
    },
    "output_data": {
      "log_file": "drone_log0/drone_dynamics.csv"
    }
  }
}
```


# シミュレーション実行方法

```bash
cd workspace
```

```bash
source setup.bash
```

Z軸方向の速度制御の評価を実行する場合は、以下のコマンドを実行してください。
```bash
bash ../src/drone_evaluation/evaluate.bash ../src/drone_evaluation/input/spd_z-step-input.json
```

成功すると以下のようにログファイルが出力されます。

```bash
% ls drone_log0                                                                                    
drone_dynamics.csv      log_baro.csv            log_gps.csv             log_mag.csv             log_rotor_1.csv         log_rotor_3.csv
log_acc.csv             log_battery.csv         log_gyro.csv            log_rotor_0.csv         log_rotor_2.csv         log_thrust.csv
```

TODO: 結果の解析方法はペンディング中。

## PIDパラメータの変更方法

PIDパラメータは、以下に配置されていますので、適宜変更してください。

`src/drone_control/config/param-api-mixer.txt`


