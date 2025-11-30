"""
Quick inspection script to examine the structure of Excel files
"""
import pandas as pd
import os

# Path to study files
study_files_dir = r"c:\Users\rndpi\Documents\Coding Projects\MSL-tender\study files"

# Get first file to inspect
files = [f for f in os.listdir(study_files_dir) if f.endswith('.xlsx')]
if files:
    first_file = os.path.join(study_files_dir, files[0])
    print(f"Inspecting: {files[0]}\n")
    
    # Get sheet names
    xl_file = pd.ExcelFile(first_file)
    print(f"Sheet names: {xl_file.sheet_names}\n")
    
    # Read first sheet
    df = pd.read_excel(first_file, sheet_name=0)
    print(f"Shape: {df.shape}")
    print(f"\nColumns:\n{df.columns.tolist()}\n")
    print(f"\nFirst 5 rows:\n{df.head()}\n")
    print(f"\nData types:\n{df.dtypes}\n")
    print(f"\nSample data from first row:\n{df.iloc[0]}")
