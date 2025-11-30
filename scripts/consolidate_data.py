"""
Data Consolidation Script for Tender App
Consolidates multiple standardized Excel master files into a single dataset
for upload to Supabase database.

Author: Ryan Dilger
Date: November 30, 2025
"""

import pandas as pd
import os
from datetime import datetime
import numpy as np

def consolidate_study_files(input_dir, output_file):
    """
    Consolidate all standardized master files from study files directory
    
    Args:
        input_dir (str): Path to directory containing Excel files
        output_file (str): Path for output consolidated CSV file
    
    Returns:
        pd.DataFrame: Consolidated dataframe
    """
    
    print("Starting data consolidation...")
    print(f"Input directory: {input_dir}")
    print(f"Output file: {output_file}\n")
    
    # Get all Excel files
    excel_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx')]
    excel_files.sort()  # Sort for consistent ordering
    
    print(f"Found {len(excel_files)} Excel files to process:\n")
    for f in excel_files:
        print(f"  - {f}")
    print()
    
    # List to store individual dataframes
    dfs = []
    
    # Process each file
    for idx, filename in enumerate(excel_files, 1):
        filepath = os.path.join(input_dir, filename)
        print(f"[{idx}/{len(excel_files)}] Processing: {filename}")
        
        try:
            # Read Excel file
            df = pd.read_excel(filepath, sheet_name=0)
            
            # Add source file column for traceability
            df['source_file'] = filename
            
            # Add processing timestamp
            df['import_date'] = datetime.now().isoformat()
            
            dfs.append(df)
            print(f"    ✓ Loaded {len(df)} rows")
            
        except Exception as e:
            print(f"    ✗ Error processing {filename}: {str(e)}")
            continue
    
    # Concatenate all dataframes
    print(f"\nCombining {len(dfs)} dataframes...")
    consolidated_df = pd.concat(dfs, ignore_index=True)
    
    # Data cleaning and standardization
    print("Performing data cleaning...")
    
    # Replace '.' with NaN for missing values
    consolidated_df.replace('.', np.nan, inplace=True)
    
    # Standardize column names (snake_case for database)
    column_mapping = {
        'Study#': 'study_number',
        'Original Chop ID': 'original_chop_id',
        'Standardized Chop ID': 'standardized_chop_id',
        'Block': 'block',
        'Setting': 'setting',
        'Sex': 'sex',
        'Sireline': 'sireline',
        'd aging': 'days_aging',
        'd of display': 'days_display',
        'pH': 'ph',
        'Ventral Color': 'ventral_color',
        'Ventral Marbling': 'ventral_marbling',
        'Ventral Firmness': 'ventral_firmness',
        'Minolta Ventral L*': 'minolta_ventral_l',
        'Minolta Ventral a*': 'minolta_ventral_a',
        'Minolta Ventral b*': 'minolta_ventral_b',
        'Chop Color': 'chop_color',
        'Chop Marbling': 'chop_marbling',
        'Chop Firmness': 'chop_firmness',
        'Minolta Chop L*': 'minolta_chop_l',
        'Minolta Chop a*': 'minolta_chop_a',
        'Minolta Chop b*': 'minolta_chop_b',
        'Moisture %': 'moisture_percent',
        'Fat %': 'fat_percent'
    }
    
    consolidated_df.rename(columns=column_mapping, inplace=True)
    
    # Convert numeric columns to appropriate types
    numeric_columns = [
        'study_number', 'original_chop_id', 'block',
        'ph', 'ventral_color', 'ventral_marbling', 'ventral_firmness',
        'minolta_ventral_l', 'minolta_ventral_a', 'minolta_ventral_b',
        'chop_color', 'chop_marbling', 'chop_firmness',
        'minolta_chop_l', 'minolta_chop_a', 'minolta_chop_b',
        'moisture_percent', 'fat_percent'
    ]
    
    for col in numeric_columns:
        if col in consolidated_df.columns:
            consolidated_df[col] = pd.to_numeric(consolidated_df[col], errors='coerce')
    
    # Save consolidated data
    print(f"\nSaving consolidated data to: {output_file}")
    consolidated_df.to_csv(output_file, index=False)
    
    # Generate summary statistics
    print("\n" + "="*60)
    print("CONSOLIDATION SUMMARY")
    print("="*60)
    print(f"Total records: {len(consolidated_df)}")
    print(f"Total columns: {len(consolidated_df.columns)}")
    print(f"Source files processed: {len(excel_files)}")
    print(f"\nRecords per study:")
    print(consolidated_df['study_number'].value_counts().sort_index())
    print(f"\nMissing values per column:")
    missing = consolidated_df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    if len(missing) > 0:
        print(missing)
    else:
        print("  No missing values found!")
    
    print(f"\nData quality metrics:")
    print(f"  - Unique standardized chop IDs: {consolidated_df['standardized_chop_id'].nunique()}")
    print(f"  - Unique studies: {consolidated_df['study_number'].nunique()}")
    print(f"  - Date range: {consolidated_df['study_number'].min()} to {consolidated_df['study_number'].max()}")
    
    print("\n" + "="*60)
    print("✓ Consolidation complete!")
    print("="*60)
    
    return consolidated_df


def main():
    """Main execution function"""
    
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    input_dir = os.path.join(project_root, "study files")
    output_dir = os.path.join(project_root, "database")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"consolidated_data_{timestamp}.csv")
    
    # Also create a 'latest' version without timestamp
    latest_output = os.path.join(output_dir, "consolidated_data_latest.csv")
    
    # Run consolidation
    df = consolidate_study_files(input_dir, output_file)
    
    # Save latest version
    df.to_csv(latest_output, index=False)
    print(f"\nAlso saved as: {latest_output}")
    
    # Optional: Generate SQL-ready output with additional formatting
    sql_output = os.path.join(output_dir, f"consolidated_data_for_sql_{timestamp}.csv")
    df.to_csv(sql_output, index=False, quoting=1)  # Quote all fields for SQL import
    print(f"SQL-ready version: {sql_output}")


if __name__ == "__main__":
    main()
