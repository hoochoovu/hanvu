import os
import shutil

def copy_folder_structure(src, dst):
    for dirpath, dirnames, filenames in os.walk(src):
        # Compute the destination path
        dest_dirpath = os.path.join(dst, os.path.relpath(dirpath, src))
        
        # Create the destination directory if it doesn't exist
        if not os.path.exists(dest_dirpath):
            os.makedirs(dest_dirpath)

if __name__ == "__main__":
    src_folder = r"E:\Dataset\All Authors\Vertical"  # Replace with the source folder path
    dst_folder = r"E:\Dataset\All Authors\Horizontal"  # Replace with the destination folder path
    
    # Copy folder structure
    copy_folder_structure(src_folder, dst_folder)

    print("Folder structure copied successfully!")
