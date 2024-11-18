# はじめに

ここでは、物理モデルと制御モデルのモデルデータを管理します。

# ディレクトリ構成

- base_models
  - plants: 物理モデルのベースモデルデータを格納します。
    - alt.json: Zの物理モデルです。
    - alt_spd.json: Vzの物理モデルです。
    - rotor_thrust.json: ローター/スララスタの物理モデルです。
  - controllers: 制御モデルのベースモデルデータを格納します。
    - pid_alt.json：Z軸方向のPID制御モデルです。
    - pid_alt_spd.json：Vz軸方向のPID制御モデルです。
    - mixer.json：ミキサーモデルです。
  - constants: 物理モデルや制御モデルで使用する定数データを格納します。
    - constants-map.json: シミュレータのパラメータとのマッピングをします。
      - config_drone: installer/config/mixer-api/drone_config_0.json
      - config_pid: src/drone_control/config/param-api-mixer.txt
      - value: 即値を設定します
      - calc: 計算式を設定します
    - constants.json: constants-map.jsonから展開したパラメータです。
- combined_models
  - control_alt_spd.json: Z軸方向の制御モデルです。
  - plant_alt_spd.json: Vzの物理モデルです。
- expanded_models:全てのパラメータを展開したデータを格納します。

# 定数展開方法

```bash
python src/libs/expand_constants.py src/drone_control/config/param-api-mixer.txt installer/config/mixer-api/drone_config_0.json models/constants/constants-map.json ./models/constants/constants.json
```

# 展開モデルの作成方法

plant_alt_spd.jsonを例に説明します。

```bash
python src/libs/expand_json.py models/base_models models/combined_models/plant_alt_spd.json models/expanded_models/expanded_plant_alt_spd.json
```
