import os

def rename_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if ".jpg" in file:
                old_path = os.path.join(root, file)
                new_file = file.replace("hvvj man", "")
                new_path = os.path.join(root, new_file)
                os.rename(old_path, new_path)
                print(f"Renamed: {old_path} -> {new_path}")

# Specify the directory to process
directory_to_process = r"C:\Users\Han Vu\Pictures\Self Pic\Training\Kohya"

# Call the function
rename_files(directory_to_process)