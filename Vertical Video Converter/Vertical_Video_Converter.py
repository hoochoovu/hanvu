import os
import subprocess

# Define the input and output directories
input_folder = r'E:\Dataset\All Audio Quotes\TEST\Input'
output_folder = r'E:\Dataset\All Audio Quotes\TEST\Output'

# Scaling factor: 1.0 means no scaling, >1 means magnification, <1 means reduction
scaling_factor = 1

# Create the output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all the files in the input directory
for filename in os.listdir(input_folder):
    if filename.endswith('.mp4'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '_scaled_AV1.mp4')

        # Adjust these parameters to control quality
        crf_value = 23  # Constant Rate Factor (lower is better quality)
        bitrate = '5M'  # Bitrate setting (alternative to CRF)

        # Construct the FFmpeg command with NVIDIA NVENC for AV1
        command = [
            'ffmpeg',
            '-hwaccel', 'cuda',             # Enable CUDA hardware acceleration
            '-i', input_path,
            '-vf', f'scale={int(1920 * scaling_factor)}:1080',  # Scaling to fit 1080 width and maintain aspect ratio
            '-c:v', 'av1_nvenc',            # Use NVIDIA's AV1 encoder
            '-crf', str(crf_value),         # Use CRF for quality control (optional)
            # '-b:v', bitrate,              # Alternative: use bitrate to control quality (comment out if using CRF)
            '-c:a', 'aac',                  # Use AAC for audio encoding
            output_path
        ]

        # Execute the command
        try:
            subprocess.run(command, check=True)
            print(f"Successfully processed {filename}")
        except subprocess.CalledProcessError as e:
            print(f"Error processing {filename}: {e}")

print("Conversion completed!")