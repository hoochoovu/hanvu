import os
import shutil
import time

def move_files(folder_path, destination_folder):
    start_time = time.time()
    file_count = 0
    error_log = []

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            try:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):  # Check if it's a file, not a directory
                    #Move or Copy function
                    shutil.copy(file_path, destination_folder)
                    file_count += 1
            except Exception as e:
                error_log.append(f"Error moving file: {filename} - {str(e)}")

    end_time = time.time()
    elapsed_time = end_time - start_time

    print(f"Files processed: {file_count}")
    print(f"Time elapsed: {elapsed_time} seconds")

    if error_log:
        print("Errors encountered:")
        for error in error_log:
            print(error)

# Example usage:
folder_path = r"FOLDER PATH DIR"
destination_folder = r"FOLDER PATH DIR"
move_files(folder_path, destination_folder)