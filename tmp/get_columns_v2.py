import openpyxl
import json

def get_full_columns(filepath):
    try:
        # Load only the first 1 row to get headers
        wb = openpyxl.load_workbook(filepath, read_only=True)
        sheet = wb.active
        
        # Get headers (first row)
        for row in sheet.iter_rows(max_row=1, values_only=True):
            headers = list(row)
            print(json.dumps(headers, indent=2))
            break
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    path = r"c:\Git\Forever_Tools\WysiWyg - release\MusicStack\MusicStack-Inventory-2026-04-01-Forever-Young-Records.xlsx"
    get_full_columns(path)
