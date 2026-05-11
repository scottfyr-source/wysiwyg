import pandas as pd
import json

def get_columns(filepath):
    # Use pandas to read just the header
    df = pd.read_excel(filepath, nrows=0)
    columns = df.columns.tolist()
    print(json.dumps(columns, indent=2))

if __name__ == "__main__":
    path = r"c:\Git\Forever_Tools\WysiWyg - release\MusicStack\MusicStack-Inventory-2026-04-01-Forever-Young-Records.xlsx"
    get_columns(path)
