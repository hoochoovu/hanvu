import os
import subprocess

# Define input and output folders
input_folder = r"E:\Dataset\All Video BG\Watermarked\Horizontal\Smoke"
output_folder = "output2mins"

# Settings for encoding
codec = "h264"  # Options: 'h264' or 'av1'
crf = 23        # Constant Rate Factor for AV1 and H264 (lower is better quality)
bitrate = "5M"  # Bitrate (e.g., '5M' for 5 Mbps)
preset = "slow" # Options for H264 encoding (faster, slow, etc.)

# Nvidia GPU settings
gpu_id = 1  # Select GPU ID (0, 1, etc.)

def convert_video(input_file, output_file, codec, crf, bitrate, preset, gpu_id):
    if codec == "h264":
        command = [
            "ffmpeg", "-y", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
            "-i", input_file,
            "-c:v", "h264_nvenc", "-preset", preset, "-b:v", bitrate,
            "-c:a", "aac", "-b:a", "192k",
            "-gpu", str(gpu_id),
            output_file
        ]
    elif codec == "av1":
        command = [
            "ffmpeg", "-y", "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
            "-i", input_file,
            "-c:v", "av1_nvenc", "-crf", str(crf), "-b:v", bitrate,
            "-c:a", "aac", "-b:a", "192k",
            "-gpu", str(gpu_id),
            output_file
        ]
    else:
        raise ValueError("Invalid codec specified. Use 'h264' or 'av1'.")
    
    print(f"Converting {input_file} to {output_file} using {codec} codec...")
    subprocess.run(command)

def process_videos(input_folder, output_folder, codec, crf, bitrate, preset, gpu_id):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith(".mp4"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}_{codec}.mp4")
            convert_video(input_file, output_file, codec, crf, bitrate, preset, gpu_id)

if __name__ == "__main__":
    # Process videos
    process_videos(input_folder, output_folder, codec, crf, bitrate, preset, gpu_id)
