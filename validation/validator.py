import json
import jsonschema
from jsonschema import validate
from math import isclose

class Validator:
    def validate(self, response, validation_type, expected_value, error_message, results, variables, placeholder_manager):
        if isinstance(expected_value, str) and (expected_value.startswith('$.') or expected_value.startswith('${')):
            expected_value = json.loads(placeholder_manager.replace_placeholders(expected_value, results, variables))
        
        if validation_type == 'equals':
            if response != expected_value:
                raise AssertionError(error_message)
        elif validation_type == 'contains':
            if not all(item in response.items() for item in expected_value.items()):
                raise AssertionError(error_message)
        elif validation_type == 'string_equals':
            if not isinstance(response, str) or response != expected_value:
                raise AssertionError(f"Validation failed: {error_message}")

        elif validation_type == 'int_equals':
            if not isinstance(response, int) or response != int(expected_value):
                raise AssertionError(f"Validation failed: {error_message}")

        elif validation_type == 'float_equals':
            if not isinstance(response, float) or not isclose(response, float(expected_value), rel_tol=1e-9):
                raise AssertionError(f"Validation failed: {error_message}")
        elif validation_type == 'expression':
            try:
                result = eval(expected_value, {}, {'response': response})
                if not result:
                    raise AssertionError(f"Validation failed: {error_message}")
            except Exception as e:
                raise AssertionError(f"Expression validation error: {str(e)}")
        elif validation_type == 'schema':
            try:
                validate(instance=response, schema=expected_value)
            except Exception as e:
                raise AssertionError(f"{error_message}: {e.message}")
        else:
            raise ValueError(f"Unsupported validation type: {validation_type}")
