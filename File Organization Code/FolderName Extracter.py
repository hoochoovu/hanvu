import os
import time

def record_subfolder_names(folder_path, output_file_path):
    start_time = time.time()
    subfolder_names = []
    
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            subfolder_names.append(dir_name)
    
    with open(output_file_path, 'w') as output_file:
        for subfolder_name in subfolder_names:
            output_file.write(subfolder_name + '\n')
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Number of subfolders: {len(subfolder_names)}")
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

# Specify the folder path and output file path
folder_path = r"FOLDER PATH DIR"
output_file_path = r'FOLDER PATH DIR'

record_subfolder_names(folder_path, output_file_path)