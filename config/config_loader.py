import pandas as pd

class ConfigLoader:
    def __init__(self, excel_file_path):
        self.excel_file_path = excel_file_path
        self.df = pd.read_excel(excel_file_path)
    
    def get_steps(self):
        return self.df.to_dict('records')
