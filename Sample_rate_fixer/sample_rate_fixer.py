import os
import subprocess

def convert_audio_sample_rate(input_folder):
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.endswith((".mp4", ".mkv", ".mov", ".avi")):  # Add other video file extensions if needed
                file_path = os.path.join(root, file)
                output_file_name = f"{os.path.splitext(file)[0]} (44.1kHz){os.path.splitext(file)[1]}"
                output_file_path = os.path.join(root, output_file_name)
                
                # FFmpeg command with NVIDIA GPU acceleration (h264_nvenc codec)
                ffmpeg_command = [
                    'ffmpeg',
                    '-y',  # Overwrite output files without asking
                    '-i', file_path,  # Input file
                    '-c:v', 'h264_nvenc',  # Use NVIDIA GPU for video encoding
                    '-b:v', '16M',  # Video bitrate (adjust as needed)
                    '-c:a', 'aac',  # Audio codec
                    '-ar', '44100',  # Resample audio to 44.1kHz
                    '-crf', '1',  # Constant Rate Factor for quality (lower is better quality)
                    output_file_path  # Output file
                ]
                
                # Run the FFmpeg command
                subprocess.run(ffmpeg_command, check=True)
                
                # Delete the original file
                os.remove(file_path)

if __name__ == "__main__":
    input_folder = r"E:\Dataset\All Authors - 44.1khz"
    convert_audio_sample_rate(input_folder)