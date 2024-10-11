import os
import shutil

# Set the input and output folder paths
input_folder = r"E:\Python_Practice\RATIO Printify Portrait Ratio Maker\output\Warm Colorgrade" 
output_folder = "output" 

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate through all files in the input folder
for root, dirs, files in os.walk(input_folder): 
    for filename in files:
        # Get the file's base name and extension
        base_name, extension = os.path.splitext(filename)

        # Construct the new filename with "-colorgraded" added
        new_filename = f"{base_name}-colorgraded{extension}"

        # Construct the full paths for the input and output files
        input_file_path = os.path.join(root, filename)  # Use 'root' here
        output_file_path = os.path.join(output_folder, new_filename)

        # Copy the file to the output folder with the new name
        shutil.copy2(input_file_path, output_file_path)

print("Files copied and renamed successfully!") 