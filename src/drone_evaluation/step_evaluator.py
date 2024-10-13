import pandas as pd
import numpy as np
import sys
import json

class EvaluationParameters:
    DEFAULT_PARAMS = {
        "VARIANCE_THRESHOLD": 1.0,
        "RISE_TIME_10_PERCENT": 0.1,
        "RISE_TIME_90_PERCENT": 0.9,
        "DELAY_TIME_PERCENT": 0.5,
        "SETTLING_TIME_PERCENT": 0.05,
        "TARGET_CV": 0.01
    }

    def __init__(self, config=None, target_params=None):
        self.params = self.DEFAULT_PARAMS.copy()
        if config:
            self.params.update(config)
        if target_params:
            self.params.update(target_params)


class DataEvaluator:
    def __init__(self, input_file, evaluation_params: EvaluationParameters):
        self.params = evaluation_params.params
        self.data = pd.read_csv(input_file)
        self.results = {}
        self.params["NUM_LAST_POINTS"] = len(self.data) // 10  # Calculate NUM_LAST_POINTS from data
        self.preprocess_data()

    def preprocess_data(self):
        # Remove the last row if it contains garbage data
        self.data = self.data[:-1]
        # Convert timestamps to seconds
        self.data['timestamp'] = self.data['timestamp'] / 1e6  # Convert from usec to sec
        # Select the axis and apply inversion if specified
        axis = self.params['AXIS']
        if self.params['INVERT_AXIS']:
            self.data[axis] = -1.0 * self.data[axis]
        # Convert radians to degrees if specified
        if self.params.get('CONVERT_TO_DEGREE', False):
            self.data[axis] = np.degrees(self.data[axis])
        # Filter data starting from the evaluation start time
        evaluation_start_time = self.params['EVALUATION_START_TIME']
        self.data = self.data[self.data['timestamp'] >= evaluation_start_time].copy()
        # Adjust timestamps to start from the evaluation start time
        self.data['timestamp'] -= evaluation_start_time

    def calculate_steady_state(self):
        # Calculate steady-state value (average of the last NUM_LAST_POINTS values)
        steady_state_data = self.data[self.params['AXIS']][-self.params['NUM_LAST_POINTS']:]
        steady_value = steady_state_data.mean()
        variance = steady_state_data.var()
        return steady_value, variance

    def check_steady_state(self, steady_value, variance):
        # Exit if variance is too high
        if variance > self.params['VARIANCE_THRESHOLD']:
            print("Variance is too high. Steady state value is unstable.")
            return False
        return True
    
    def calculate_performance_metrics(self, steady_value):
        org_steady_value = steady_value
        axis = self.params['AXIS']
        target_value = self.params['TARGET_VALUE']

        # Determine if the value is increasing or decreasing based on the initial and steady values
        is_increase = steady_value > self.data[axis].iloc[0]
        if not is_increase:
            # Decreasing case
            initial_value = self.data[axis].iloc[0]
            steady_value = initial_value - steady_value
            self.data[axis] = initial_value - self.data[axis]

        # Process as increasing case for calculations
        rise_threshold_10_percent = steady_value * self.params['RISE_TIME_10_PERCENT']
        rise_threshold_90_percent = steady_value * self.params['RISE_TIME_90_PERCENT']
        delay_threshold = steady_value * self.params['DELAY_TIME_PERCENT']

        # Calculate rise time start
        rise_time_start_condition = self.data[axis] >= rise_threshold_10_percent
        if rise_time_start_condition.any():
            rise_time_start = self.data.loc[rise_time_start_condition, 'timestamp'].min()
        else:
            rise_time_start = None

        # Calculate rise time end
        rise_time_end_condition = self.data[axis] >= rise_threshold_90_percent
        if rise_time_end_condition.any():
            rise_time_end = self.data.loc[rise_time_end_condition, 'timestamp'].min()
        else:
            rise_time_end = None

        # Calculate delay time
        delay_time_condition = self.data[axis] >= delay_threshold
        if delay_time_condition.any():
            delay_time = self.data.loc[delay_time_condition, 'timestamp'].min()
        else:
            delay_time = None

        max_value = self.data[axis].max()

        T_r = rise_time_end - rise_time_start
        T_d = delay_time
        O_s = max_value - steady_value if is_increase else 0

        # Settling time T_s
        settled = np.abs(self.data[axis] - steady_value) <= np.abs(steady_value * self.params['SETTLING_TIME_PERCENT'])
        T_s = None
        for i in range(len(settled)):
            if settled.iloc[i]:
                others_settled = np.all(settled.iloc[i:])
                if others_settled:
                    T_s = self.data['timestamp'].iloc[i]
                    break

        if T_s is None:
            T_s = 10000.0

        return T_r, T_d, O_s, T_s, target_value, org_steady_value

    def evaluate_performance(self, T_r, T_d, O_s, T_s, target_value, steady_value):
        # Determine results
        cs_result = "OK" if np.abs(steady_value - target_value) <= target_value * self.params['TARGET_CV'] else "NG"
        tr_result = "OK" if T_r <= self.params['TARGET_TR'] else "NG"
        td_result = "OK" if T_d <= self.params['TARGET_TD'] else "NG"
        os_result = "OK" if O_s <= self.params['TARGET_OS'] else "NG"
        ts_result = "OK" if T_s is not None and T_s <= self.params['TARGET_TS'] else "NG"

        # Store results
        self.results = {
            "steady_state": (cs_result, steady_value),
            "rise_time": (tr_result, T_r),
            "delay_time": (td_result, T_d),
            "overshoot": (os_result, O_s),
            "settling_time": (ts_result, T_s)
        }

    def display_results(self):
        # Output results
        print(f"{self.results['steady_state'][0]} c(Steady state value)  : {self.results['steady_state'][1]:.3f}   (Target: {self.params['TARGET_VALUE']}±{self.params['TARGET_VALUE'] * self.params['TARGET_CV']:.3f} m)")
        print(f"{self.results['rise_time'][0]} T_r(Rise time)         : {self.results['rise_time'][1]:.3f} s (Target: ≤ {self.params['TARGET_TR']:.3f} s)")
        print(f"{self.results['delay_time'][0]} T_d(Delay time)        : {self.results['delay_time'][1]:.3f} s (Target: ≤ {self.params['TARGET_TD']:.3f} s)")
        print(f"{self.results['overshoot'][0]} O_s(Maximum overshoot) : {self.results['overshoot'][1]:.3f}   (Target: ≤ {self.params['TARGET_OS']:.3f} m)")
        print(f"{self.results['settling_time'][0]} T_s(5% settling time)  : {self.results['settling_time'][1]:.3f} s (Target: ≤ {self.params['TARGET_TS']:.3f} s)")

    def run_evaluation(self):
        steady_value, variance = self.calculate_steady_state()
        if not self.check_steady_state(steady_value, variance):
            return
        T_r, T_d, O_s, T_s, target_value, steady_value = self.calculate_performance_metrics(steady_value)
        self.evaluate_performance(T_r, T_d, O_s, T_s, target_value, steady_value)
        self.display_results()


def main(input_file, config_params=None, target_params=None):
    """
    Main function to evaluate drone data.

    Args:
        input_file (str): Path to the CSV file containing the drone data.
        config_params (dict, optional): Configuration parameters for evaluation.
            Example:
            {
                "AXIS": "Z",
                "INVERT_AXIS": True,
                "EVALUATION_START_TIME": 0.0,
                "CONVERT_TO_DEGREE": False
            }
        target_params (dict, optional): Target parameters for evaluation.
            Example:
            {
                "TARGET_TR": 15.0,
                "TARGET_TD": 10.0,
                "TARGET_OS": 1.5,
                "TARGET_TS": 30.0,
                "TARGET_VALUE": 12.0
            }

    Returns:
        None
    """
    evaluation_params = EvaluationParameters(config=config_params, target_params=target_params)
    evaluator = DataEvaluator(input_file, evaluation_params)
    evaluator.run_evaluation()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <simulation_config_file>")
    else:
        # Load JSON file with simulation and evaluation parameters
        with open(sys.argv[1], "r") as json_file:
            config_data = json.load(json_file)

        # Extract configuration and target parameters from the loaded JSON
        config_params = config_data["evaluation"]["step_evaluation"]["config_params"]
        target_params = config_data["evaluation"]["step_evaluation"]["target_params"]

        # Sample CSV file path (replace with your actual file path)
        input_file = config_data["evaluation"]["output_data"]["log_file"]

        # Running the main function with extracted parameters
        main(input_file, config_params, target_params)
