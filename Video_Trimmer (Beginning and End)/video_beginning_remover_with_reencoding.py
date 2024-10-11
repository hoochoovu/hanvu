import os
import subprocess

# Set the input and output directories
input_folder = r'input'
output_folder = r'output'

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# User-defined encoding settings
codec_choice = 'h264'  # Options: 'av1' or 'h264'
crf_value = 23  # Constant Rate Factor for quality control
bitrate = '6M'  # Bitrate for the output video
gpu_id = '0'  # Set GPU ID for hardware acceleration (if needed)

# Loop through all .mp4 files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith('.mp4'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)
        
        # Set the start time (skip the first part in seconds)
        start_time = 14400
        
        # Base ffmpeg command
        command = [
            'ffmpeg',
            '-hwaccel', 'cuda',  # Enable NVIDIA GPU acceleration
            '-hwaccel_device', gpu_id,  # Set the GPU ID
            '-ss', str(start_time),  # Start time to trim
            '-i', input_path,     # Input file
        ]
        
        # Codec-specific settings
        if codec_choice == 'av1':
            # AV1 encoding settings
            command.extend([
                '-c:v', 'libaom-av1',  # Use AV1 codec
                '-crf', str(crf_value),  # CRF for AV1 (quality control)
                '-b:v', bitrate,        # Bitrate for AV1
            ])
        elif codec_choice == 'h264':
            # H.264 encoding settings
            command.extend([
                '-c:v', 'libx264',      # Use H.264 codec
                '-crf', str(crf_value),  # CRF for H.264
                '-b:v', bitrate,         # Bitrate for H.264
                '-preset', 'slow',       # H.264 slow preset for better compression
            ])
        
        # Complete the command
        command.extend([
            '-y',                 # Overwrite output file if it exists
            output_path           # Output file
        ])
        
        # Execute the ffmpeg command
        subprocess.run(command, check=True)
        print(f"Processed {filename} and saved to {output_path}")

print("Processing complete!")
