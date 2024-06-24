import re
from datetime import datetime, timedelta

class PlaceholderManager:
    def replace_placeholders(self, item, results, variables):
        if isinstance(item, dict):
            return {k: self.replace_placeholders(v, results, variables) for k, v in item.items()}
        elif isinstance(item, list):
            return [self.replace_placeholders(i, results, variables) for i in item]
        elif isinstance(item, str):
            item = self._replace_step_based_placeholders(item, results)
            item = self._replace_variable_based_placeholders(item, variables)
            item = self._replace_date_time_placeholders(item)
            return item
        else:
            return item

    def _replace_step_based_placeholders(self, item, results):
        pattern = r'\$\.(\d+)\.(.+)'
        matches = re.findall(pattern, item)
        for match in matches:
            step, key = match
            step_result = results[int(step)]
            value = step_result
            for part in key.split('.'):
                value = value.get(part)
                if value is None:
                    raise ValueError(f"Key {key} not found in step {step} result")
            item = item.replace(f'$.{step}.{key}', str(value))
        return item

    def _replace_variable_based_placeholders(self, item, variables):
        pattern = r'\$\{(\w+)\}'
        matches = re.findall(pattern, item)
        for match in matches:
            if match in variables:
                item = item.replace(f'${{{match}}}', str(variables[match]))
            else:
                raise ValueError(f"Variable {match} not found")
        return item

    def _replace_date_time_placeholders(self, item):
        current_datetime = datetime.now()
        item = re.sub(r'\$\{current_date\}', current_datetime.strftime('%Y-%m-%d'), item)
        item = re.sub(r'\$\{current_time\}', current_datetime.strftime('%H:%M:%S'), item)
        item = re.sub(r'\$\{current_datetime\}', current_datetime.strftime('%Y-%m-%d %H:%M:%S'), item)

        arithmetic_pattern = r'\$\{(current_date|current_time|current_datetime) *([-+]) *(\d+)([dhms])\}'
        matches = re.findall(arithmetic_pattern, item)
        for match in matches:
            date_type, operator, amount, unit = match
            amount = int(amount)
            if operator == '-':
                amount = -amount
            if unit == 'd':
                delta = timedelta(days=amount)
            elif unit == 'h':
                delta = timedelta(hours=amount)
            elif unit == 'm':
                delta = timedelta(minutes=amount)
            elif unit == 's':
                delta = timedelta(seconds=amount)
            else:
                raise ValueError(f"Unsupported time unit: {unit}")
            
            if date_type == 'current_date':
                new_datetime = current_datetime + delta
                item = re.sub(r'\$\{current_date *[-+] *\d+[dhms]\}', new_datetime.strftime('%Y-%m-%d'), item)
            elif date_type == 'current_time':
                new_datetime = current_datetime + delta
                item = re.sub(r'\$\{current_time *[-+] *\d+[dhms]\}', new_datetime.strftime('%H:%M:%S'), item)
            elif date_type == 'current_datetime':
                new_datetime = current_datetime + delta
                item = re.sub(r'\$\{current_datetime *[-+] *\d+[dhms]\}', new_datetime.strftime('%Y-%m-%d %H:%M:%S'), item)
        return item
