import os
import subprocess
import ffmpeg

# Set the input and output directories
input_folder = 'input'
output_folder = 'output'

# Minimum duration in seconds (e.g., 15 seconds)
MIN_DURATION = 15

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all .mp4 files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.mp4'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # Get video duration in seconds using ffmpeg
        try:
            probe = ffmpeg.probe(input_path)
            duration = float(probe['format']['duration'])
            print(f"{filename} duration: {duration} seconds")
            
            # Process only videos that are 15 seconds or greater
            if duration >= MIN_DURATION:
                # Calculate the end time (total duration - 2 minutes)
                end_time = max(0, duration - 0.50)  # Keep all but the last 2 minutes (120 seconds)
                
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
            else:
                print(f"Skipping {filename}: video is shorter than {MIN_DURATION} seconds.")
        
        except ffmpeg.Error as e:
            print(f"Error processing {filename}: {str(e)}")

print("Processing complete!")
