import os
import shutil

def copy_py_files(src_folder, dest_folder):
    """
    Copies the folder structure from src_folder to dest_folder and only copies .py files.
    
    Args:
    src_folder (str): The source directory path.
    dest_folder (str): The destination directory path.
    """
    # Walk through the directory tree of the source folder
    for root, dirs, files in os.walk(src_folder):
        # Determine the corresponding destination directory
        relative_path = os.path.relpath(root, src_folder)
        dest_path = os.path.join(dest_folder, relative_path)

        # Create the destination directory if it doesn't exist
        os.makedirs(dest_path, exist_ok=True)

        # Copy only the .py files
        for file in files:
            if file.endswith(".py"):
                src_file_path = os.path.join(root, file)
                dest_file_path = os.path.join(dest_path, file)
                
                # Copy the .py file
                shutil.copy2(src_file_path, dest_file_path)
                print(f"Copied: {src_file_path} -> {dest_file_path}")

if __name__ == "__main__":
    # Example usage
    src_folder = r"E:\Python_Practice"  # Replace with your source folder path
    dest_folder = r"E:\Python Git Uploads\V2 Uploads"  # Replace with your output folder path

    # Call the function to copy .py files
    copy_py_files(src_folder, dest_folder)
