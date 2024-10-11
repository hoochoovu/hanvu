import os
import subprocess

# Define folder paths
input_folder = r"E:\Python_Practice\AVIF_Converter\Input"
output_folder = r"E:\Python_Practice\AVIF_Converter\Output"
finished_folder = r"E:\Python_Practice\AVIF_Converter\Finished"

# Create output and finished folders if they don't exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
if not os.path.exists(finished_folder):
    os.makedirs(finished_folder)

# Loop through files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".avif"):
        input_file = os.path.join(input_folder, filename)
        output_file = os.path.join(output_folder, filename[:-5] + ".jpg")

        # Convert the file using ffmpeg
        command = ["ffmpeg", "-i", input_file, output_file]
        subprocess.run(command)

        print(f"Converted {filename} to {output_file}")

        # Move the original AVIF file to the Finished folder
        os.rename(input_file, os.path.join(finished_folder, filename))

print("All Image files processed and moved to Finished folder.")