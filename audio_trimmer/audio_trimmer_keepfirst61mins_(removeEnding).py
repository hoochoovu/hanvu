import os
import subprocess

# Set the input and output directories
input_folder = 'output'
output_folder = r'E:\Dataset\ALL BG Music\1 hour Sub-Conscious Sleep Music 1 hour'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all audio files in the input folder
for filename in os.listdir(input_folder):
    # Check for common audio file extensions (case insensitive)
    if filename.lower().endswith(('.mp3', '.wav', '.aac', '.flac', '.m4a')):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # Debug print statement to verify the file being processed
        print(f"Processing audio file: {input_path}")
        
        # Set the duration to 61 minutes (3660 seconds)
        duration_to_keep = 3660
        
        # Construct the ffmpeg command to trim the audio
        command_trim_audio = [
            'ffmpeg',
            '-hwaccel', 'cuda',  # Enable NVIDIA GPU acceleration (if available)
            '-i', input_path,     # Input audio file
            '-t', str(duration_to_keep),  # Set the duration to keep (61 minutes)
            '-c', 'copy',         # Copy audio codec without re-encoding
            '-y',                 # Overwrite output file if it exists
            output_path           # Output file
        ]
        
        # Execute the ffmpeg command
        subprocess.run(command_trim_audio, check=True)
        
        print(f"Processed {filename} and saved to {output_path}")

print("Processing complete!")
