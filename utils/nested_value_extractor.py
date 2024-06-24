class NestedValueExtractor:
    @staticmethod
    def extract_nested_value(data, path):
        keys = path.split('.')
        value = data
        for key in keys:
            value = value.get(key)
            if value is None:
                raise ValueError(f"Key {path} not found in response")
        return value
