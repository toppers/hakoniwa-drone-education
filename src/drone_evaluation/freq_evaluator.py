import pandas as pd
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
import json
import sys
import math
from scipy.signal import find_peaks

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
        return phase_diff

    def find_peaks_in_signal(self, signal, height=None, distance=None):
        """
        Find peaks in the signal using scipy's find_peaks function
        """
        peaks, _ = find_peaks(signal, height=height, distance=distance)
        return peaks

    def calculate_peak_time_differences(self, timestamps, peaks):
        """
        Calculate the time differences between consecutive peaks
        """
        peak_times = timestamps[peaks]
        time_diffs = np.diff(peak_times).astype('timedelta64[ms]').astype(float) / 1000  # Convert to seconds
        return time_diffs

    def calculate_average_period(self, time_diffs):
        """
        Calculate the average period from time differences between peaks
        """
        if len(time_diffs) > 0:
            return np.mean(time_diffs)
        else:
            return None

    def plot_results(self, xf, amplitude, phase_diff, output_plot_file):
        """
        Plot amplitude and phase difference
        """
        plt.figure(figsize=(12, 6))

        # Plot amplitude
        plt.subplot(2, 1, 1)
        plt.plot(xf, amplitude, label='Amplitude')
        plt.xlabel('Frequency (Hz)')
        plt.xscale('log')
        plt.ylabel('Amplitude')
        plt.title('Amplitude Spectrum')
        plt.legend()

        # Plot phase difference
        plt.subplot(2, 1, 2)
        plt.plot(xf, phase_diff, label='Phase Difference', color='r')
        plt.xlabel('Frequency (Hz)')
        plt.xscale('log')
        plt.ylabel('Phase Difference (degrees)')
        plt.title('Phase Difference Spectrum')
        plt.legend()

        plt.tight_layout()
        plt.savefig(output_plot_file)
        plt.show()

    def plot_phase_results(self, xf, phase1, phase2, phase_diff, output_plot_file, freq):
        """
        Plot amplitude and phase difference with a vertical line at specified frequency
        """
        plt.figure(figsize=(12, 6))

        # Plot input phase
        plt.subplot(2, 1, 1)
        plt.plot(xf, phase1, label='input')
        plt.axvline(x=freq, color='g', linestyle='--', label=f'{freq} Hz')  # 縦線を追加
        plt.xlabel('Frequency (Hz)')
        plt.xscale('log')
        plt.ylabel('input')
        plt.title('Input Spectrum')
        plt.legend()

        # Plot output phase
        plt.subplot(2, 1, 2)
        plt.plot(xf, phase2, label='output', color='r')
        plt.axvline(x=freq, color='g', linestyle='--', label=f'{freq} Hz')  # 縦線を追加
        plt.xlabel('Frequency (Hz)')
        plt.xscale('log')
        plt.ylabel('output')
        plt.title('Output Spectrum')
        plt.legend()

        # Plot phase difference
        plt.subplot(2, 1, 2)
        plt.plot(xf, phase_diff, label='Phase Difference', color='r')
        plt.xlabel('Frequency (Hz)')
        plt.xscale('log')
        plt.ylabel('Phase Difference (degrees)')
        plt.title('Phase Difference Spectrum')
        plt.legend()

        plt.tight_layout()
        plt.savefig(output_plot_file)
        plt.show()

    def almost_equal(self, value, target, tolerance):
        """
        Check if a value is approximately equal to a target within a given tolerance.

        Args:
            value (float): The value to check.
            target (float): The target value.
            tolerance (float): The acceptable range of difference from the target.

        Returns:
            bool: True if the value is within the tolerance of the target, False otherwise.
        """
        return target - tolerance <= value <= target + tolerance


    def update_signal(self, target_degree, tolerance, sample_spacing):
        # Perform FFT on the initial signal
        xf1, amplitude1, phase1 = self.perform_fft(self.signal1, sample_spacing)
        phase1_at_freq = np.interp(freq, xf1, phase1)
        shift_count = 0
        max_shifts = len(self.signal1)

        while self.almost_equal(phase1_at_freq, target_degree, tolerance) == False and shift_count < max_shifts:
            # Perform FFT
            xf1, amplitude1, phase1 = self.perform_fft(self.signal1, sample_spacing)

            # Interpolate to find the phase at the specified frequency
            phase1_at_freq = np.interp(freq, xf1, phase1)
            #print(f"{shift_count}: angle: {phase1_at_freq}")

            if self.almost_equal(phase1_at_freq, target_degree, tolerance) == False:
                # Shift the signal to the left by one sample
                c = int(1/freq)
                if c == 0:
                    c = 1
                self.signal1 = np.roll(self.signal1, -c)
                self.signal2 = np.roll(self.signal2, -c)
                shift_count += c
            else:
                break

        if shift_count >= max_shifts:
            print("Could not find a shift that brings the phase to 90 degrees. Proceeding with available data.")

    def calc_phase_diff(self, filtered_df1, filtered_df2):
        timestamps1 = filtered_df1['timestamp'].values
        timestamps2 = filtered_df2['timestamp'].values

        peaks1 = self.find_peaks_in_signal(self.signal1)
        peaks2 = self.find_peaks_in_signal(self.signal2)

        # Calculate time differences between consecutive peaks
        time_diffs1 = self.calculate_peak_time_differences(timestamps1, peaks1)
        time_diffs2 = self.calculate_peak_time_differences(timestamps2, peaks2)

        # Calculate average periods
        period1 = self.calculate_average_period(time_diffs1)
        period2 = self.calculate_average_period(time_diffs2)
        #print("period1:", period1)
        # Calculate the time difference between the first peaks of both signals
        if len(peaks1) > 0 and len(peaks2) > 0:
            # Take the minimum number of peaks to avoid index out of bounds
            min_peaks = min(len(peaks1), len(peaks2))

            # Calculate time differences between the corresponding peaks
            time_diff_peaks = []
            for i in range(min_peaks):
                time_diff = (timestamps1[peaks1[i]] - timestamps2[peaks2[i]]).astype('timedelta64[ms]').astype(float) / 1000
                time_diff_peaks.append(time_diff)

            # Calculate the average time difference
            average_time_diff = np.mean(time_diff_peaks)
        else:
            average_time_diff = None
        #print("time_diff_peaks: ", average_time_diff)
        # Calculate phase difference based on the peak time difference and the average period
        phase_at_freq = (average_time_diff/period1)*360
        return phase_at_freq

    def analyze_signals(self, input_file1, input_file2, start_time, freq, input_file1_label, input_file2_label, input_inverse=False, output_inverse=False, max_val=2896):
        """
        Load, filter, perform FFT, and calculate gain and phase difference for two signals.

        Args:
            input_file1 (str): Path to the input signal CSV file.
            input_file2 (str): Path to the output signal CSV file.
            start_time (float): Start time in seconds for filtering the data.
            freq (float): Frequency for which to calculate gain and phase.
            input_file1_label (str): Label for the input signal in the CSV file.
            input_file2_label (str): Label for the output signal in the CSV file.
            input_inverse (bool): Whether to invert the input signal.
            output_inverse (bool): Whether to invert the output signal.
            max_val (float): Maximum value for normalization.

        Returns:
            (float, float): Gain in dB and phase difference at the specified frequency.
        """
        # Load data
        df1 = self.load_csv(input_file1)
        df2 = self.load_csv(input_file2)

        # Filter by time
        end_time = df1['timestamp'].iloc[-1]
        start_time = pd.Timestamp(start_time, unit='s')
        filtered_df1 = self.filter_by_time(df1, start_time, end_time)
        filtered_df2 = self.filter_by_time(df2, start_time, end_time)

        # Check if filtered data is empty or has insufficient rows
        if len(filtered_df1) < 2 or len(filtered_df2) < 2:
            print("Filtered data is insufficient for FFT analysis. Please check the time range or input data.")
            sys.exit(1)

        # Remove last row if it contains garbage data
        if len(filtered_df1) > 1:
            filtered_df1 = filtered_df1[:-1]
        if len(filtered_df2) > 1:
            filtered_df2 = filtered_df2[:-1]

        # Invert signal if specified
        if input_inverse:
            filtered_df1[input_file1_label] = -filtered_df1[input_file1_label]
        if output_inverse:
            filtered_df2[input_file2_label] = -filtered_df2[input_file2_label]

        # Start shifting process to make phase1 reach 90 degrees
        #self.signal1 = self.normalize_signal(filtered_df1[input_file1_label].values, max_val)
        self.signal1 = filtered_df1[input_file1_label].values
        self.signal2 = filtered_df2[input_file2_label].values
        sample_spacing = (filtered_df1['timestamp'].iloc[1] - filtered_df1['timestamp'].iloc[0]).total_seconds()

        #self.update_signal(target_degree=90, tolerance= 1, sample_spacing=sample_spacing)


        phase_at_freq = self.calc_phase_diff(filtered_df1, filtered_df2)

        xf1, amplitude1, phase1 = self.perform_fft(self.signal1, sample_spacing)
        xf2, amplitude2, phase2 = self.perform_fft(self.signal2, sample_spacing)

        # Ensure xf1 and gain_db have the same length
        min_length = min(len(xf1), len(amplitude1), len(amplitude2))
        xf1 = xf1[:min_length]
        amplitude1 = amplitude1[:min_length]
        amplitude2 = amplitude2[:min_length]


        spline1 = CubicSpline(xf1, amplitude1[:min_length])
        spline2 = CubicSpline(xf1, amplitude2[:min_length])

        gain1_at_freq = spline1(freq)
        gain2_at_freq = spline2(freq)
        gain = gain2_at_freq / gain1_at_freq  # Amplitude ratio
        gain_at_freq = 20 * np.log10(gain)  # Convert to dB
        #gain_at_freq = np.interp(freq, xf1, gain_db)
        #print(f"max:gain1_at_freq: {freq}, {max(amplitude1)}")
        #print(f"max:gain2_at_freq: {freq}, {max(amplitude2)}")
        #print(f"gain1_at_freq: {freq}, {gain1_at_freq}")
        #print(f"gain2_at_freq: {freq}, {gain2_at_freq}")
        #print(f"gain_at_freq: {freq}, {gain_at_freq}")
        phase1_at_freq = np.interp(freq, xf1, phase1[:min_length])
        phase2_at_freq = np.interp(freq, xf1, phase2[:min_length])
        #phase_at_freq = phase2_at_freq - phase1_at_freq

        return gain_at_freq, phase_at_freq, phase1_at_freq, phase2_at_freq

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
        input_inverse = config_data['evaluation']['freq_evaluation'].get('input_inverse', False)
        output_inverse = config_data['evaluation']['freq_evaluation'].get('output_inverse', False)
        input_max_val = config_data['evaluation']['input_data']['max_val']

        # Analyze signals and get results
        #print("input_file1: ", input_file1)
        #print("input_file2: ", input_file2)
        gain, phase, phase1_at_freq, phase2_at_freq = analyzer.analyze_signals(input_file1, input_file2, start_time, freq, 
                                               input_file1_label, input_file2_label, input_inverse=input_inverse, output_inverse=output_inverse, max_val=input_max_val)
        print(f"{freq}, {math.log10(freq):.2f}, {gain:.2f}, {phase:.2f}, {phase1_at_freq:.2f}, {phase2_at_freq:.2f}")