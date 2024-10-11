import pandas as pd

class Logger:
    def __init__(self, filename='out.csv'):
        self.data_cache = []
        self.filename = filename
        self.columns = ["timestamp", "value"]  # デフォルトのカラム名を設定

    def set_columns(self, columns):
        """カラム名を設定するメソッド"""
        self.columns = columns

    def log(self, *values):
        """ログに複数の値を記録する"""
        if len(values) != len(self.columns):
            raise ValueError(f"Expected {len(self.columns)} values, but got {len(values)}")
        self.data_cache.append(values)

    def save(self):
        """キャッシュをCSVに保存する"""
        df = pd.DataFrame(self.data_cache, columns=self.columns)
        df.to_csv(self.filename, index=False)
