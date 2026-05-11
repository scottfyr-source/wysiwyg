import os
import sys

try:
    import openpyxl
    import pandas as pd
    print("Found openpyxl and pandas")
except ImportError:
    print("openpyxl or pandas not installed. Attempting simple openpyxl import only.")
    try:
        import openpyxl
        print("Found openpyxl")
    except ImportError:
        print("Neither openpyxl nor pandas found in environment.")
        sys.exit(1)

def explore_excel(filepath):
    # Peek at the file
    wb = openpyxl.load_workbook(filepath, read_only=True)
    sheet = wb.active
    print(f"Sheet Name: {sheet.title}")
    
    # Get headers (first row)
    rows = list(sheet.iter_rows(max_row=5, values_only=True))
    if not rows:
        print("Empty sheet.")
        return
    
    headers = rows[0]
    print("\nColumns:")
    for i, h in enumerate(headers):
        print(f"{i}: {h}")
    
    print("\nFirst 3 rows of data:")
    for i, row in enumerate(rows[1:4]):
        print(f"Row {i+1}: {row}")

if __name__ == "__main__":
    path = r"c:\Git\Forever_Tools\WysiWyg - release\MusicStack\MusicStack-Inventory-2026-04-01-Forever-Young-Records.xlsx"
    if os.path.exists(path):
        explore_excel(path)
    else:
        print(f"File not found: {path}")
