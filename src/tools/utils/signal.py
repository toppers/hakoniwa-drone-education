import numpy as np
from scipy.signal import chirp

def signal_generate(interval, total_time, offset=0, type='sine', frequency=1.0, chirp_f0=0, chirp_f1=1):
    """
    Generates different types of signals including sine and chirp.
    
    Parameters:
    interval (float): Time interval between samples.
    total_time (float): Total duration for the signal.
    offset (float): Vertical offset for the signal.
    type (str): Type of signal to generate ('sine' or 'chirp').
    frequency (float): Frequency of the sine wave in Hz (used only for sine).
    chirp_f0 (float): Starting frequency for chirp signal (only for chirp).
    chirp_f1 (float): Ending frequency for chirp signal (only for chirp).
    
    Returns:
    list: List of generated signal values.
    """
    # Create a time array
    time_points = np.arange(0, total_time, interval)
    print(f"interval: {interval} total_time: {total_time} len: {len(time_points)}")
    if type == 'sine':
        # Period for sine wave
        period = 1 / frequency
        # Generate sine wave and apply offset
        sine_values = np.sin(2 * np.pi * time_points / period) + offset
        return sine_values.tolist()
    
    elif type == 'chirp':
        # Generate chirp signal (frequency sweep from chirp_f0 to chirp_f1)
        chirp_values = chirp(time_points, f0=chirp_f0, f1=chirp_f1, t1=total_time, method='linear') + offset
        return chirp_values.tolist()

    else:
        raise ValueError(f"Unsupported signal type: {type}")
