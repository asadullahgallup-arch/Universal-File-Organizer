import os
import pandas as pd

def get_file_columns(file_path):
    """
    Reads only the column headers of an Excel or CSV file 
    without loading the full data into memory.
    """
    if not os.path.exists(file_path):
        return []
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, nrows=0)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path, nrows=0)
        else:
            return []
        return list(df.columns)
    except Exception:
        return []

def split_file_by_column(file_path, target_column, output_dir):
    """
    Reads a master Excel/CSV file and splits it into multiple files 
    based on the unique categories found inside the target_column.
    """
    if not os.path.exists(file_path):
        return False, "Selected master file does not exist."
        
    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            return False, "Unsupported file format. Please use CSV or Excel (.xlsx)."

        if target_column not in df.columns:
            return False, f"Column '{target_column}' not found."

        unique_values = df[target_column].dropna().unique()

        # Create a unique subfolder inside the USER-SELECTED output folder
        final_output_dir = os.path.join(output_dir, f"Separated_{target_column}_Files")
        os.makedirs(final_output_dir, exist_ok=True)

        for val in unique_values:
            safe_val_name = "".join([c for c in str(val) if c.isalnum() or c in ' _-']).strip()
            filtered_df = df[df[target_column] == val]
            
            file_root, file_extension = os.path.splitext(os.path.basename(file_path))
            new_filename = f"{safe_val_name}_Division{file_extension}"
            output_file_path = os.path.join(final_output_dir, new_filename)

            if file_extension == '.csv':
                filtered_df.to_csv(output_file_path, index=False)
            else:
                filtered_df.to_excel(output_file_path, index=False)

        return True, f"Successfully split data into {len(unique_values)} files inside: \n{final_output_dir}"

    except Exception as e:
        return False, f"An unexpected processing error occurred: {str(e)}"
