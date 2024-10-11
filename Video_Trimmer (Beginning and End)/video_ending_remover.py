import os
import subprocess
import ffmpeg

# Set the input and output directories
input_folder = r'E:\Python_Practice\Random_Quote_Combiner\output\Book Outputs\For TikTok'
output_folder = 'output'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all .mp4 files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.mp4'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # Get video duration in seconds using ffmpeg
        probe = ffmpeg.probe(input_path)
        duration = float(probe['format']['duration'])
        
        # Calculate the duration to keep (total duration - 2 minutes)
        end_time = max(0, duration - 120)  # Keep all but the last 2 minutes (120 seconds)
        
        # Construct the ffmpeg command
        command = [
            'ffmpeg',
            '-hwaccel', 'cuda',  # Enable NVIDIA GPU acceleration
            '-i', input_path,     # Input file
            '-t', str(end_time),  # Duration to keep
            '-c', 'copy',         # Copy codecs (no re-encoding)
            '-y',                 # Overwrite output file if it exists
            output_path           # Output file
        ]
        
        # Execute the ffmpeg command
        subprocess.run(command, check=True)
        print(f"Processed {filename} and saved to {output_path}")

print("Processing complete!")