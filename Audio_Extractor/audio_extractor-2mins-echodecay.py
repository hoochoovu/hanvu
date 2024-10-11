import os
import subprocess
from pathlib import Path

# Function to get the duration of the video in seconds
def get_video_duration(input_video_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Error getting duration for {input_video_path}: {e}")
        return 0

# Function to extract audio in 120-second chunks with fade-in, fade-out, and delayed reverb (echo) effects
def split_video_to_mp3_chunks(input_video_path, output_folder, chunk_duration=120, fade_duration=3):
    # Get the duration of the video
    video_duration = get_video_duration(input_video_path)
    
    # Calculate how many chunks we will have
    num_chunks = int(video_duration // chunk_duration) + 1
    
    for chunk_idx in range(num_chunks):
        start_time = chunk_idx * chunk_duration
        output_audio_name = f"{Path(input_video_path).stem}_chunk_{chunk_idx + 1}.mp3"
        output_audio_path = os.path.join(output_folder, output_audio_name)
        
        # Apply fade-in, fade-out, and delayed reverb (echo) effects
        # FFmpeg command to extract 120-second audio chunk with fade and echo effects
        command = [
            'ffmpeg',
            '-ss', str(start_time),             # Start time of the chunk
            '-t', str(chunk_duration),          # Duration of the chunk
            '-i', input_video_path,             # Input video file
            '-vn',                              # Disable video
            '-ar', '44100',                     # Set audio sample rate to 44.1 kHz
            '-ac', '2',                         # Set audio channels to 2
            '-b:a', '192k',                     # Set audio bitrate (standard for mp3)
            '-af', f"afade=in:st=0:d={fade_duration},"
                   f"afade=out:st={chunk_duration-fade_duration}:d={fade_duration},"
                   f"aecho=0.8:0.88:60:0.4",    # Delayed reverb (echo) effect: 0.8 decay, 60ms delay
            '-y',                               # Overwrite output files
            output_audio_path                   # Output .mp3 file
        ]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Extracted and processed chunk with echo: {output_audio_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting chunk from {input_video_path}: {e}")

# Function to replicate the subfolder structure and split videos into audio chunks
def process_videos_in_folder(input_folder, output_folder, chunk_duration=120, fade_duration=3):
    # Walk through the input folder recursively
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith(('.mp4', '.mov', '.avi', '.mkv', '.flv', '.webm')):  # Add other video extensions if necessary
                input_video_path = os.path.join(root, file)
                
                # Create the corresponding output folder structure
                relative_path = os.path.relpath(root, input_folder)
                output_subfolder = os.path.join(output_folder, relative_path)
                os.makedirs(output_subfolder, exist_ok=True)
                
                # Split the video into 120-second audio chunks with fade-in, fade-out, and echo effects
                split_video_to_mp3_chunks(input_video_path, output_subfolder, chunk_duration, fade_duration)

if __name__ == "__main__":
    # Define input and output folder paths
    input_folder = r"E:\Dataset\PODCAST VIDEOS\Jim Rohn"  # Replace with the path to your input folder
    output_folder = r"E:\Dataset\PODCAST VIDEOS\Jim Rohn\2 min audio"  # Replace with the path to your output folder

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Start processing videos (120-second chunks with 3-second fade and echo by default)
    process_videos_in_folder(input_folder, output_folder, chunk_duration=120, fade_duration=3)
