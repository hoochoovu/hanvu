import os
import subprocess
from pathlib import Path

# Function to convert video to .mp3 audio with 44.1 kHz
def convert_video_to_mp3(input_video_path, output_audio_path):
    # Use FFmpeg to extract audio and convert to mp3, 44.1 kHz
    command = [
        'ffmpeg',
        '-i', input_video_path,          # Input video file
        '-vn',                           # Disable video
        '-ar', '44100',                  # Set audio sample rate to 44.1 kHz
        '-ac', '2',                      # Set audio channels to 2
        '-b:a', '192k',                  # Set audio bitrate (standard for mp3)
        '-y',                            # Overwrite output files
        output_audio_path                # Output .mp3 file
    ]
    
    try:
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Converted: {input_video_path} to {output_audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_video_path}: {e}")

# Function to replicate the subfolder structure and convert videos
def process_videos_in_folder(input_folder, output_folder):
    # Walk through the input folder recursively
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.webm')):  # Add other video extensions if necessary
                input_video_path = os.path.join(root, file)
                
                # Create the corresponding output folder structure
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)
                
                # Set output audio file path
                output_audio_name = Path(file).stem + '.mp3'  # Change extension to .mp3
                output_audio_path = os.path.join(output_subfolder, output_audio_name)
                
                # Convert the video to mp3
                convert_video_to_mp3(input_video_path, output_audio_path)

if __name__ == "__main__":
    # Define input and output folder paths
    input_folder = r"E:\Dataset\PODCAST VIDEOS\Eric Thomas\Clips"  # Replace with the path to your input folder
    output_folder = r"output"  # Replace with the path to your output folder

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Start processing videos
    process_videos_in_folder(input_folder, output_folder)
