import pandas as pd
import ast

file_path = "/Users/kush/Files/Intern/Data/Railwar-station-locations.xlsx"
try:
    df = pd.read_excel(file_path)
    result_list = df.values.tolist()
    print(result_list)
except Exception as e:
    print(f"Error reading the Excel file: {e}")