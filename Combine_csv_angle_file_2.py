import pandas as pd
import os
import re
import tkinter as tk
from tkinter import filedialog

def natural_sort_key(s):
    """ Key function for natural alphanumeric sorting (e.g., 1, 2, 10 instead of 1, 10, 2) """
    return [int(text) if text.isdigit() else text.lower() for text in re.split('([0-9]+)', s)]

def combine_contact_angles_clean():
    # 1. Pop up screen to choose the folder
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title='Select Folder containing Contact Angle CSVs')
    
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    # Get file list and sort it naturally
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    all_files.sort(key=natural_sort_key)

    left_data = []
    right_data = []

    for filename in all_files:
        # Skip the output file to avoid self-processing
        if filename == "Combined_Contact_Angles.csv":
            continue
            
        file_full_path = os.path.join(folder_path, filename)
        
        try:
            df = pd.read_csv(file_full_path)
            
            # Remove the .csv extension for the display name
            clean_name = os.path.splitext(filename)[0]
            
            # Row 2 (Left) is index 0, Row 3 (Right) is index 1
            left_angle = df.loc[0, 'Angle']
            right_angle = df.loc[1, 'Angle']
            
            left_data.append({'Name of File': clean_name, 'Left_Angle': left_angle})
            right_data.append({'Name of File': clean_name, 'Right_Angle': right_angle})
            
        except Exception as e:
            print(f"Could not process {filename}: {e}")

    # Create DataFrames
    df_left = pd.DataFrame(left_data)
    df_right = pd.DataFrame(right_data)

    # 2. Save to CSV
    output_path = os.path.join(folder_path, "Combined_Contact_Angles.csv")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Table 1: Left_Angle\n")
        df_left.to_csv(f, index=False)
        f.write("\n") 
        f.write("Table 2: Right_Angle\n")
        df_right.to_csv(f, index=False)

    print(f"Success! Cleaned and sorted file saved at: {output_path}")

if __name__ == "__main__":
    combine_contact_angles_clean()
