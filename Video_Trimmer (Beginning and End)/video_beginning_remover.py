import os
import subprocess
import ffmpeg

# Set the input and output directories
input_folder = r'E:\Python_Practice\Video_Trimmer (Beginning and End)\input'
output_folder = 'output'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all .mp4 files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.mp4'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # Set the start time (skip the first part in seconds)
        start_time = 14400
        
        # Construct the ffmpeg command
        command = [
            'ffmpeg',
            '-hwaccel', 'cuda',  # Enable NVIDIA GPU acceleration
            '-ss', str(start_time),  # Start time to trim
            '-i', input_path,     # Input file
            '-c', 'copy',         # Copy codecs (no re-encoding)
            '-y',                 # Overwrite output file if it exists
            output_path           # Output file
        ]
        
        # Execute the ffmpeg command
        subprocess.run(command, check=True)
        print(f"Processed {filename} and saved to {output_path}")

print("Processing complete!")
