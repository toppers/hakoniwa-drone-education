import json

class InputParamLoader:
    def __init__(self, file_path):
        """
        Initializes the InputParamLoader with the path to the JSON configuration file.
        
        Parameters:
        file_path (str): Path to the JSON file containing simulation parameters.
        """
        self.file_path = file_path

    def load_params(self):
        """
        Loads the simulation parameters from the JSON file.
        
        Returns:
        dict: Dictionary containing the loaded simulation parameters.
        """
        try:
            with open(self.file_path, 'r') as file:
                params = json.load(file)
                return params
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at {self.file_path} was not found.")
        except json.JSONDecodeError:
            raise ValueError(f"The file at {self.file_path} is not a valid JSON file.")

# Example usage
if __name__ == "__main__":
    # Assume we have a JSON file named 'simulation_params.json'
    loader = InputParamLoader('simulation_params.json')
    try:
        params = loader.load_params()
        print("Loaded Parameters:", params)
    except (FileNotFoundError, ValueError) as e:
        print(e)
