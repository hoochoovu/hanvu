import os
import subprocess

# Set the GPU ID to use
gpu_id = 1
os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)

# Define the input and output directories
input_folder = r'E:\Python_Practice\Vertical Video Converter\input\2080ti'
output_folder = r'output'
background_image = r"E:\Python_Practice\Vertical Video Converter\1920x1080blackbg.png"  # Path to the 1920x1080 black image

# Scaling factor: 1.0 means no scaling, >1 means magnification, <1 means reduction
scaling_factor = 0.50

# X and Y offset for video overlay position (horizontal centered, vertical bottom aligned)
x_offset = 0  # Horizontal offset, center by default
y_offset = "H-h"  # Align to the bottom

# Create the output directory if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all subfolders in the input directory
for subfolder in os.listdir(input_folder):
    input_subfolder = os.path.join(input_folder, subfolder)
    if os.path.isdir(input_subfolder):
        output_subfolder = os.path.join(output_folder, subfolder)
        os.makedirs(output_subfolder, exist_ok=True)

        # Loop through all the .mp4 files in the subfolder
        for filename in os.listdir(input_subfolder):
            if filename.endswith('.mp4'):
                input_path = os.path.join(input_subfolder, filename)
                output_path = os.path.join(output_subfolder, os.path.splitext(filename)[0] + '_converted.mp4')

                # Adjust these parameters to control quality
                crf_value = 23  # Constant Rate Factor (lower is better quality)
                
                # FFmpeg filter to scale the vertical video and overlay it on the background (bottom aligned)
                overlay_filter = (
                    f"[1:v]scale=iw*{scaling_factor}:-1[scaled];"  # Scale the video
                    f"[0:v][scaled]overlay=(W-w)/2+{x_offset}:{y_offset}"  # Bottom align overlay on black background
                )
                
                # Construct the FFmpeg command with NVIDIA NVENC for h264
                command = [
                    'ffmpeg',
                    '-hwaccel', 'cuda',             # Enable CUDA hardware acceleration
                    '-i', background_image,         # Black background input
                    '-i', input_path,               # Vertical video input
                    '-filter_complex', overlay_filter,  # Apply overlay filter
                    '-c:v', 'h264_nvenc',           # Use NVIDIA's h264 encoder
                    '-crf', str(crf_value),         # CRF for quality control
                    '-c:a', 'aac',                  # Audio codec
                    '-y',                           # Overwrite output file if it exists
                    output_path
                ]

                # Execute the command
                try:
                    subprocess.run(command, check=True)
                    print(f"Successfully processed {filename} in subfolder: {subfolder}")
                except subprocess.CalledProcessError as e:
                    print(f"Error processing {filename} in subfolder: {subfolder}: {e}")

print("Conversion completed!")
