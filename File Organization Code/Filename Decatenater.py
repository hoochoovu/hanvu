import os
import time

folder_path = r'FOLDER PATH DIR'  # Replace with the actual folder path

error_log = []
file_count = 0

start_time = time.time()

# 1. Check files in a folder
for filename in os.listdir(folder_path):
    try:
        file_count += 1

        # 2. Delete the first 15 letters of the file name
        new_filename = filename[8:]

        # Perform any desired operations with the file, such as renaming or deleting
        old_file_path = os.path.join(folder_path, filename)
        new_file_path = os.path.join(folder_path, new_filename)
        os.rename(old_file_path, new_file_path)

    except Exception as e:
        # 3. Record any errors in an error log
        error_log.append(f"Error processing file '{filename}': {str(e)}")

end_time = time.time()
elapsed_time = end_time - start_time

# 4. Count the loop and print at the end
print(f"Processed {file_count} files.")

# 5. Capture the time elapsed and print at the end
print(f"Elapsed time: {elapsed_time} seconds.")

# Print the error log, if any
if error_log:
    print("\nError Log:")
    for error in error_log:
        print(error)