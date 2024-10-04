
class TargetValues:
    def __init__(self):
        self.values = {}
        self.stop_time_usec = -1
        self.first_key = None

    def set_stop_time(self, value: int):
        self.stop_time_usec = value
    
    def set_target(self, key, value):
        if self.first_key is None:
            self.first_key = key
        self.values[key] = float(value)
        print(f"Target {key}: {value}")

    def has_key(self, key):
        return key in self.values

    def value(self, key):
        if self.has_key(key):
            return self.values[key]
        return None
