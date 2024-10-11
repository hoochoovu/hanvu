import os
import subprocess

# Set the input and output directories
input_folder = 'input'
output_folder = 'output'

# Set the desired dB change (positive for increase, negative for decrease)
volume_db_change = 12  # Adjust this value as needed

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all .mp4 files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.mp4'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # Construct the ffmpeg command
        command = [
            'ffmpeg',
            '-hwaccel', 'cuda',              # Enable NVIDIA GPU acceleration if available
            '-i', input_path,                # Input file
            '-af', f'volume={volume_db_change}dB',  # Audio filter to change volume
            '-c:v', 'copy',                  # Copy video codec (no re-encoding)
            '-c:a', 'aac',                   # Re-encode audio with AAC codec
            '-y',                            # Overwrite output file if it exists
            output_path                      # Output file
        ]
        
        # Execute the ffmpeg command
        subprocess.run(command, check=True)
        print(f"Processed {filename} and saved to {output_path}")

print("Processing complete!")
