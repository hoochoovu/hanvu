import os
import pydub
from natsort import natsorted  # Install: pip install natsort

# Function to append 2 seconds of silence
def add_silence(audio_segment):
  silence = pydub.AudioSegment.silent(duration=2000)  # 2 seconds in milliseconds
  return audio_segment + silence

# Path to the folder containing audio files
audio_folder = r"E:\ChatBot Therapy\Marcus Aurelius\Marcus Aurelius Audio Files\0. All Chapters"

# Set the output path for the stitched audio file
output_path = r"E:\ChatBot Therapy\Marcus Aurelius\Marcus Aurelius Audio Files\Marcus Aurelius Meditations - Full Audiobook.mp3"

# Create an empty list to store the audio segments
audio_segments = []

# Get all audio files in the folder, sorted numerically
for filename in natsorted(os.listdir(audio_folder)):
    if filename.endswith(('.wav', '.mp3')):
        filepath = os.path.join(audio_folder, filename)
        
        # Load the audio file
        audio = pydub.AudioSegment.from_file(filepath)

        # Append silence
        audio_with_silence = add_silence(audio)

        # Append to the list of audio segments
        audio_segments.append(audio_with_silence)

# Concatenate all the audio segments
final_audio = sum(audio_segments)

# Export the final audio file
final_audio.export(output_path, format="mp3")

print(f"Audio files stitched and saved as {output_path}")