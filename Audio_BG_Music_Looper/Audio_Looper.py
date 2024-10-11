import os
import subprocess

# Set the input folder, output folder, and desired duration in seconds
input_folder = r"E:\Dataset\ALL BG Music\I Am A Man Who Will Fight For Your Honor"
output_folder = r"E:\Dataset\ALL BG Music\58 mins Sub-Conscious Sleep Music 58 mins"
desired_duration = 3600 # e.g., 40271 seconds

# Ensure the output folder exists
os.makedirs(output_folder, exist_ok=True)

def process_audio_file(input_file, output_file, desired_duration):
    # Use ffmpeg to loop the audio and trim to the exact duration
    cmd = [
        "ffmpeg",
        "-stream_loop", "-1",  # Loop indefinitely
        "-i", input_file,
        "-t", str(desired_duration),  # Set the exact duration
        "-c", "copy",
        "-y",  # Overwrite output file without asking
        output_file
    ]
    
    # Execute the command
    subprocess.run(cmd)

def main():
    # Iterate through each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith((".mp3", ".wav", ".flac", ".aac")):  # Add other formats if needed
            input_file = os.path.join(input_folder, filename)
            output_file_name = f"_{os.path.splitext(filename)[0]}.mp3"
            output_file = os.path.join(output_folder, output_file_name)

            # Process the audio file
            process_audio_file(input_file, output_file, desired_duration)

if __name__ == "__main__":
    main()
