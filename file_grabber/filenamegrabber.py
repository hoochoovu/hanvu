import os
import shutil

def copy_sizexsize_files(input_folder, output_folder):
    """
    Copies files containing "SIZExSIZE" in their names from the input folder and its subfolders to the output folder.

    Args:
        input_folder: The path to the folder containing subfolders.
        output_folder: The path to the folder where the "SIZExSIZE" files will be copied.
    """

    for root, dirs, files in os.walk(input_folder):
        for file_name in files:
            if file_size in file_name:
                source_path = os.path.join(root, file_name)
                destination_path = os.path.join(output_folder, file_name)
                
                # Create output folder if it doesn't exist
                os.makedirs(output_folder, exist_ok=True)
                
                # Copy the file
                shutil.copy2(source_path, destination_path)

if __name__ == "__main__":
    input_folder = r"E:\ETSY ETSY ETSY\Design for Trends\Scary Halloween Faces\Digital Posters (All Ratios)\JPG"
    output_folder = "output"
    file_size = "5x7"

    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    copy_sizexsize_files(input_folder, output_folder)
    print("Files containing '" + file_size + "' copied successfully!")
