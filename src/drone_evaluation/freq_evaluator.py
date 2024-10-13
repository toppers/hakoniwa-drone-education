import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import json
import sys

class FFTAnalyzer:
    def __init__(self):
        pass

    def load_csv(self, filename):
        """
        Load CSV file and return as DataFrame
        """
        df = pd.read_csv(filename)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='us')
        return df

    def filter_by_time(self, df, start_time_sec, end_time_sec):
        """
        Filter DataFrame by a specific time range
        """
        start_time = pd.Timestamp(start_time_sec, unit='s')
        end_time = pd.Timestamp(end_time_sec, unit='s')
        return df[(df['timestamp'] >= start_time) & (df['timestamp'] <= end_time)]

    def normalize_signal(self, signal, max_val):
        """
        Normalize the signal by its maximum value
        """
        if max_val != 0:
            return signal / max_val
        else:
            return signal

    def perform_fft(self, signal, sample_spacing=1.0):
        """
        Perform FFT on the signal and return frequency, amplitude, and phase
        """
        signal_centered = signal - np.mean(signal)  # Remove offset
        N = len(signal_centered)
        yf = fft(signal_centered)
        xf = fftfreq(N, sample_spacing)[:N // 2]  # Positive frequency components only

        amplitude = 2.0 / N * np.abs(yf[:N // 2])  # Amplitude
        phase = np.angle(yf[:N // 2], deg=True)  # Phase in degrees
        return xf[:len(amplitude)], amplitude, phase

    def calculate_amplitude_gain(self, input_amplitude, output_amplitude):
        """
        Calculate amplitude gain in dB
        """
        # Ensure both amplitudes have the same length
        min_length = min(len(input_amplitude), len(output_amplitude))
        input_amplitude = input_amplitude[:min_length]
        output_amplitude = output_amplitude[:min_length]

        gain = output_amplitude / input_amplitude  # Amplitude ratio
        gain_db = 20 * np.log10(gain)  # Convert to dB
        return gain_db

    def calculate_phase_difference(self, phase1, phase2):
        """
        Calculate phase difference between two signals
        """
        # Ensure both phases have the same length
        min_length = min(len(phase1), len(phase2))
        phase1 = phase1[:min_length]
        phase2 = phase2[:min_length]

        phase_diff = phase2 - phase1
        phase_diff = (phase_diff + 180) % 360 - 180  # Normalize to range [-180, 180]
        return phase_diff

    def plot_results(self, xf, amplitude, phase_diff, output_plot_file):
        """
        Plot amplitude and phase difference
        """
        plt.figure(figsize=(12, 6))

        # Plot amplitude
        plt.subplot(2, 1, 1)
        plt.plot(xf, amplitude, label='Amplitude')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Amplitude')
        plt.title('Amplitude Spectrum')
        plt.legend()

        # Plot phase difference
        plt.subplot(2, 1, 2)
        plt.plot(xf, phase_diff, label='Phase Difference', color='r')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Phase Difference (degrees)')
        plt.title('Phase Difference Spectrum')
        plt.legend()

        plt.tight_layout()
        plt.savefig(output_plot_file)
        plt.show()

    def analyze_signals(self, input_file1, input_file2, start_time, freq, input_file1_label, input_file2_label, output_inverse=False, max_val=2896):
        """
        Load, filter, perform FFT, and calculate gain and phase difference for two signals.

        Args:
            input_file1 (str): Path to the input signal CSV file.
            input_file2 (str): Path to the output signal CSV file.
            start_time (float): Start time in seconds for filtering the data.
            freq (float): Frequency for which to calculate gain and phase.
            input_file1_label (str): Label for the input signal in the CSV file.
            input_file2_label (str): Label for the output signal in the CSV file.
            output_inverse (bool): Whether to invert the output signal.

        Returns:
            (float, float): Gain in dB and phase difference at the specified frequency.
        """
        # Load data
        df1 = self.load_csv(input_file1)
        df2 = self.load_csv(input_file2)

        # Filter by time
        end_time = df1['timestamp'].iloc[-1]
        filtered_df1 = self.filter_by_time(df1, start_time, end_time)
        filtered_df2 = self.filter_by_time(df2, start_time, end_time)

        # Remove last row if it contains garbage data
        filtered_df1 = filtered_df1[:-1]
        filtered_df2 = filtered_df2[:-1]

        # Invert output signal if specified
        if output_inverse:
            filtered_df2[input_file2_label] = -filtered_df2[input_file2_label]

        # Perform FFT on both signals
        sample_spacing = (filtered_df1['timestamp'].iloc[1] - filtered_df1['timestamp'].iloc[0]).total_seconds()
        signal1 = self.normalize_signal(filtered_df1[input_file1_label].values, max_val)
        signal2 = filtered_df2[input_file2_label].values

        xf1, amplitude1, phase1 = self.perform_fft(signal1, sample_spacing)
        xf2, amplitude2, phase2 = self.perform_fft(signal2, sample_spacing)

        # Ensure xf1 and gain_db have the same length
        min_length = min(len(xf1), len(amplitude1), len(amplitude2))
        xf1 = xf1[:min_length]
        amplitude1 = amplitude1[:min_length]
        amplitude2 = amplitude2[:min_length]

        # Calculate amplitude gain and phase difference
        gain_db = self.calculate_amplitude_gain(amplitude1, amplitude2)
        phase_diff = self.calculate_phase_difference(phase1, phase2)

        # Interpolate gain and phase at the specified frequency
        gain_at_freq = np.interp(freq, xf1, gain_db)
        phase_at_freq = np.interp(freq, xf1, phase_diff)

        return gain_at_freq, phase_at_freq

# Example usage
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <simulation_config_file>")
    else:
        # Load JSON file with simulation and evaluation parameters
        with open(sys.argv[1], "r") as json_file:
            config_data = json.load(json_file)

        analyzer = FFTAnalyzer()

        # Input parameters
        input_file1 = config_data['evaluation']['input_data']['log_file']
        input_file2 = config_data['evaluation']['output_data']['log_file']
        start_time  = config_data['evaluation']['freq_evaluation']['start_time']
        freq        = config_data['evaluation']['freq_evaluation']['freq']
        input_file1_label = config_data['evaluation']['input_data']['axis']
        input_file2_label = config_data['evaluation']['output_data']['axis']
        output_inverse = config_data['evaluation']['freq_evaluation'].get('output_inverse', False)
        input_max_val = config_data['evaluation']['input_data']['max_val']

        # Analyze signals and get results
        gain, phase = analyzer.analyze_signals(input_file1, input_file2, start_time, freq, 
                                               input_file1_label, input_file2_label, output_inverse=output_inverse, max_val=input_max_val)
        print(f"Gain at {freq} Hz: {gain:.2f} dB")
        print(f"Phase difference at {freq} Hz: {phase:.2f} degrees")