import os
import subprocess
import json

# Function to get the duration of the audio file using ffprobe
def get_audio_duration(input_path):
    try:
        # Run ffprobe to get the metadata of the file in JSON format
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', input_path],
            capture_output=True, text=True, check=True
        )
        # Parse the JSON output
        metadata = json.loads(result.stdout)
        # Return the duration in seconds
        return float(metadata['format']['duration'])
    except Exception as e:
        print(f"Error getting duration for {input_path}: {e}")
        return None

# Function to process the audio file
def process_audio(input_path, output_path):
    # Get the duration of the audio file
    duration_seconds = get_audio_duration(input_path)
    
    if duration_seconds is None:
        print(f"Skipping {input_path} due to duration retrieval error.")
        return

    # Subtract 2 minutes from the total duration
    end_time = max(0, duration_seconds - 240)

    # ffmpeg command to reduce duration, resample to 44.1kHz, and save the output
    command = [
        'ffmpeg',
        '-i', input_path,                    # Input file
        '-t', str(end_time),                 # Duration to keep
        '-ar', '44100',                      # Set audio sample rate to 44.1 kHz
        '-y',                                # Overwrite the output if it exists
        output_path                          # Output file
    ]

    # Execute the ffmpeg command
    try:
        subprocess.run(command, check=True)
        print(f"Processed {os.path.basename(input_path)} -> {os.path.basename(output_path)}")
    except subprocess.CalledProcessError as e:
        print(f"Error processing {input_path}: {e}")

# Function to process a folder of audio files
def process_audio_folder(input_folder, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Supported audio formats
    supported_formats = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a')

    # Loop through the input folder to find audio files
    for filename in os.listdir(input_folder):
        if filename.endswith(supported_formats):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # Process each audio file
            process_audio(input_path, output_path)

    print("All files processed successfully!")


if __name__ == '__main__':
    # Example usage
    input_folder = r"E:\Dataset\ALL BG Music\1 hour Sub-Conscious Sleep Music 1 hour"
    output_folder = 'output'

    process_audio_folder(input_folder, output_folder)
