import os
import subprocess

# Input and output folder paths
input_folder = r'E:\Dataset\All Samurai Photos\V2'
output_folder = r'E:\Dataset\All Samurai Photos\1 min'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Loop through the images in the input folder
for image_file in os.listdir(input_folder):
    if image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif')):
        input_path = os.path.join(input_folder, image_file)
        output_filename = os.path.splitext(image_file)[0] + '.mp4'
        output_path = os.path.join(output_folder, output_filename)
        
        # Define quality settings
        crf = '23'  # Set CRF value (lower means better quality, higher means lower quality)
        bitrate = '8M'  # Set bitrate (e.g., 2M for 2 Mbps)

        # Use FFMPEG to convert image to 1-second AV1 encoded video with Nvidia GPU acceleration
        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Overwrite output if exists
            '-loop', '1',  # Loop the image
            '-i', input_path,  # Input image
            '-c:v', 'av1',  # AV1 codec
            '-vf', 'scale=1920:1080',  # Scale to 1920x1080
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-r', '24',  # Frame rate of 24 fps
            '-t', '60',  # Duration of 1 second
            '-crf', crf,  # CRF quality setting
            '-b:v', bitrate,  # Bitrate setting
            '-c:v', 'av1_nvenc',  # Nvidia GPU accelerated H.264 encoding
            output_path  # Output video file path
        ]

        # Run the FFMPEG command
        subprocess.run(ffmpeg_command, check=True)

        print(f"Converted {image_file} to video: {output_filename}")
