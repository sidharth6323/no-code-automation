import requests
import time

class APIClient:
    DEFAULT_TIMEOUT = 10
    DEFAULT_RETRY_COUNT = 3

    def call_api(self, url, method, headers=None, data=None, timeout=DEFAULT_TIMEOUT, retry_count=DEFAULT_RETRY_COUNT):
        for attempt in range(int(retry_count)):
            try:
                if method.lower() == 'get':
                    response = requests.get(url, headers=headers, timeout=timeout)
                elif method.lower() == 'post':
                    response = requests.post(url, headers=headers, json=data, timeout=timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                if attempt < retry_count - 1:
                    time.sleep(1)
                    continue
                else:
                    raise e
