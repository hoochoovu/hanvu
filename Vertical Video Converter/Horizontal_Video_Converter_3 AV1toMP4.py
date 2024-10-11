import os
import subprocess

# Define the input and output directories
input_folder = r'E:\Davinci\Sample'
output_folder = r'E:\Davinci\Sample\Output'

# Scaling factor: 1.0 means no scaling, >1 means magnification, <1 means reduction
scaling_factor = 1.00

# Create the output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all the files in the input directory
for filename in os.listdir(input_folder):
    if filename.endswith('.mp4'):
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '_scaled_H264.mp4')

        # Adjust these parameters to control quality
        crf_value = 23  # Constant Rate Factor (lower is better quality)
        # bitrate = '5M'  # Bitrate setting (alternative to CRF)

        # Calculate zoom scale and offset for centering
        scale_x = scaling_factor
        scale_y = scaling_factor
        scaled_width = int(1920 * scale_x)
        scaled_height = int(1080 * scale_y)

        # Ensure cropped dimensions are within the scaled dimensions
        crop_width = min(scaled_width, 1920)  # Correct order: width, then height
        crop_height = min(scaled_height, 1080) # Correct order: width, then height

        # Calculate offsets to center the crop
        x_offset = (scaled_width - crop_width) / 2
        y_offset = (scaled_height - crop_height) / 2

        # Scale and crop filter to zoom in and center
        zoom_filter = f'scale={scaled_width}:{scaled_height},crop={crop_width}:{crop_height}:{x_offset}:{y_offset}'

        # Construct the FFmpeg command with NVIDIA NVENC for H.264
        command = [
            'ffmpeg',
            '-hwaccel', 'cuda',             # Enable CUDA hardware acceleration
            '-i', input_path,
            '-vf', zoom_filter,            # Apply zoom and crop
            '-c:v', 'h264_nvenc',           # Use NVIDIA's H.264 encoder
            '-preset', 'slow',              # Use a slower preset for better quality
            '-crf', str(crf_value),         # Use CRF for quality control
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