from isignal_generator import ISignalGenerator
from impl.signal_generator import SineSignalGenerator, ChirpSignalGenerator, StepSignalGenerator


class SignalFactory:
    def __init__(self, param_loader):
        """
        Initializes the SignalFactory with an InputParamLoader instance.
        
        Parameters:
        param_loader (InputParamLoader): Instance of InputParamLoader to load parameters from.
        """
        self.param_loader = param_loader
        self.params = self.param_loader.load_params()

    def create_signal_generator(self, signal_name):
        """
        Creates a list of signal generator instances based on the loaded parameters for the specified signal name.
        
        Parameters:
        signal_name (str): The name of the signal to create generators for.
        
        Returns:
        list: A list of specific signal generator instances (Sine, Chirp, Step) for each element in the parameter arrays.
        """
        signals = self.params['simulation']['signals']
        if signal_name not in signals:
            return None

        signal_params = signals[signal_name]
        signal_type = signal_params['type']
        
        if signal_type == 'sine':
            amps = signal_params['parameters']['amp']
            frequencies = signal_params['parameters']['freq']
            offsets = signal_params['parameters']['offsets']
            signal_generators = []
            for amp, frequency, offset in zip(amps, frequencies, offsets):
                signal_generators.append(SineSignalGenerator(frequency=frequency, amp=amp, offset=offset))
            return signal_generators
        elif signal_type == 'chirp':
            chirp_f0s = signal_params['parameters']['chirp_f0']
            chirp_f1s = signal_params['parameters']['chirp_f1']
            offsets = signal_params['parameters']['offsets']
            signal_generators = []
            for chirp_f0, chirp_f1, offset in zip(chirp_f0s, chirp_f1s, offsets):
                signal_generators.append(ChirpSignalGenerator(chirp_f0=chirp_f0, chirp_f1=chirp_f1, offset=offset))
            return signal_generators
        elif signal_type == 'step':
            offsets = signal_params['parameters']['offsets']
            signal_generators = []
            for offset in offsets:
                signal_generators.append(StepSignalGenerator(offset=offset))
            return signal_generators
        else:
            raise ValueError(f"Unsupported signal type: {signal_type}")

# Example usage
if __name__ == "__main__":
    from input_param_loader import InputParamLoader

    # Assume we have a JSON file named 'simulation_params.json'
    loader = InputParamLoader('simulation_params.json')
    factory = SignalFactory(loader)
    
    try:
        signal_name = 'sine1'  # Specify the signal name you want to use
        signal_generators = factory.create_signal_generator(signal_name)
        if signal_generators is None:
            print(f"Signal with name '{signal_name}' not found.")
        else:
            for generator in signal_generators:
                # Example of using each signal generator
                signal = generator.generate_signal(interval=0.01, total_time=10)
                print("Generated Signal:", signal)
    except ValueError as e:
        print(e)
    