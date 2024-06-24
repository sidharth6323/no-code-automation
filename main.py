import time
import json
import pandas as pd
from config.config_loader import ConfigLoader
from api.api_client import APIClient
from placeholder.placeholder_manager import PlaceholderManager
from validation.validator import Validator
from utils.nested_value_extractor import NestedValueExtractor

# Path to your CSV file
csv_file_path = 'sample_automation.xlsx'


def main():
    # Initialize components
    config_loader = ConfigLoader(csv_file_path)
    api_client = APIClient()
    placeholder_manager = PlaceholderManager()
    validator = Validator()
    nested_value_extractor = NestedValueExtractor()

    # Load steps from config
    steps = config_loader.get_steps()
    
    # Initialize dictionaries to store results and variables
    results = {}
    variables = {}

    # Iterate over each step
    for step in steps:
        print(f"Started step {step['Step']}")
        action = step['Action']
        sleep_time = step['Sleep'] if pd.notna(step['Sleep']) else 0
        timeout = step['Timeout'] if pd.notna(step['Timeout']) else APIClient.DEFAULT_TIMEOUT
        retry_count = step['Retry Count'] if pd.notna(step['Retry Count']) else APIClient.DEFAULT_RETRY_COUNT
        validation_error_message = step['Validation Error Message'] if pd.notna(step['Validation Error Message']) else "Validation failed"

        if action == 'api_call':
            url = step['URL']
            print(f"Making api call {url}")
            method = step['Method']
            headers = json.loads(step['Headers']) if pd.notna(step['Headers']) else None
            data = step['Data']
            
            if pd.notna(data):
                data = json.loads(placeholder_manager.replace_placeholders(data, results, variables))
            
            # Call the API and store the result
            response = api_client.call_api(url, method, headers, data, timeout, retry_count)
            results[step['Step']] = response

        elif action == 'validate':
            step_to_validate = step['Step To Validate']
            validation_type = step['Validation Type']
            expected_value = step['Expected Value']
            
            if pd.notna(expected_value):
                expected_value = json.loads(placeholder_manager.replace_placeholders(expected_value, results, variables))
            
            # Validate the result
            try:
                validator.validate(results[step_to_validate], validation_type, expected_value, validation_error_message, results, variables, placeholder_manager)
                print(f"Validation passed for step {step_to_validate}")
            except AssertionError as e:
                print(f"Validation failed for step {step_to_validate}: {e}")
                break
        
        elif action == 'extract_var':
            step_to_validate = step['Step To Validate']
            variable_name = step['Variable Name']
            variable_path = step['Variable Path']
            
            # Extract the variable from the specified step result
            step_result = results[int(step_to_validate)]
            value = nested_value_extractor.extract_nested_value(step_result, variable_path)
            variables[variable_name] = value

        else:
            raise ValueError(f"Unsupported action: {action}")

        # Sleep between API calls if specified
        time.sleep(sleep_time)

    print("Automation suite completed.")

if __name__ == "__main__":
    main()
