import os
import shutil
import time

import os
import shutil
import time

def move_files_to_subfolders(folder_path, files_folder_path):
    start_time = time.time()
    file_count = 0
    skipped_count = 0
    error_log = []

    for subfolder_name in os.listdir(folder_path):
        subfolder_path = os.path.join(folder_path, subfolder_name)

        if os.path.isdir(subfolder_path):
            subfolder_name_parts = [part for part in subfolder_name.split() if part != "Women's"]

            for filename in os.listdir(files_folder_path):
                try:
                    file_path = os.path.join(files_folder_path, filename)
                    if os.path.isfile(file_path):
                        if any(part in filename for part in subfolder_name_parts):
                            destination_path = os.path.join(subfolder_path, filename)
                            if not os.path.exists(destination_path):
                                shutil.move(file_path, destination_path)
                                file_count += 1
                            else:
                                skipped_count += 1
                except Exception as e:
                    error_log.append(f"Error moving file: {filename} - {str(e)}")

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Files processed: {file_count}")
    print(f"Skipped files: {skipped_count}")
    print(f"Time elapsed: {elapsed_time} seconds")

    if error_log:
        print("Errors encountered:")
        for error in error_log:
            print(error)

# Example usage:
folder_path = r"FOLDER PATH DIR"  # Folder to check subfolder names
files_folder_path = r"FOLDER PATH DIR"  # Folder where the files are located
move_files_to_subfolders(folder_path, files_folder_path)