import os
import time

def rename_files(folder_path):
    start_time = time.time()
    file_count = 0
    error_log = []

    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            if "" in filename:
                pretext = "apose0000"

                ### THIS IS TO SKIP CERTAIN FILES###
                if any(keyword in filename for keyword in ["hello", "hello"]):
                    continue

                try:
                    new_filename = pretext + '' + str(file_count) + '' + '.png'
                    file_path = os.path.join(root, filename)
                    new_file_path = os.path.join(root, new_filename)
                    os.rename(file_path, new_file_path)
                    file_count += 1
                except Exception as e:
                    error_log.append(f"Error renaming file: {filename} - {str(e)}")

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
rename_files(folder_path)