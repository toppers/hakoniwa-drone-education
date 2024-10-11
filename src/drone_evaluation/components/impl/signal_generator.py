import numpy as np
from scipy.signal import chirp
from ..isignal_generator import ISignalGenerator

class SineSignalGenerator(ISignalGenerator):
    def __init__(self, frequency=1.0, amp=1.0, offset=0.0):
        self.frequency = frequency
        self.amp = amp
        self.offset = offset

    def generate_signal(self, interval, total_time):
        time_points = np.arange(0, total_time, interval)
        period = 1 / self.frequency
        sine_values = self.amp * np.sin(2 * np.pi * time_points / period) + self.offset
        return sine_values.tolist()

class ChirpSignalGenerator(ISignalGenerator):
    def __init__(self, chirp_f0=0.0, chirp_f1=1.0, offset=0.0):
        self.chirp_f0 = chirp_f0
        self.chirp_f1 = chirp_f1
        self.offset = offset

    def generate_signal(self, interval, total_time):
        time_points = np.arange(0, total_time, interval)
        chirp_values = chirp(time_points, f0=self.chirp_f0, f1=self.chirp_f1, t1=total_time, method='linear') + self.offset
        return chirp_values.tolist()

class StepSignalGenerator(ISignalGenerator):
    def __init__(self, offset=0.0):
        self.offset = offset

    def generate_signal(self, interval, total_time):
        time_points = np.arange(0, total_time, interval)
        step_values = np.full_like(time_points, self.offset)
        return step_values.tolist()
