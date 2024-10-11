import os
import random
import pydub

# Function to append 2 seconds of silence
def add_silence(audio_segment):
  silence = pydub.AudioSegment.silent(duration=2000)  # 2 seconds in milliseconds
  return audio_segment + silence

# Path to the folder containing audio files
audio_folder = r"E:\Dataset\All Audio Quotes"

# Set the output path for the stitched audio file
output_path = r"Output/output.mp3"

# Target duration for the final audio in seconds
target_duration_seconds = 120  # Example: 120 seconds (2 minutes)

# Convert seconds to milliseconds
target_duration = target_duration_seconds * 1000

# Get all audio files in the folder
audio_files = [
    os.path.join(audio_folder, filename) 
    for filename in os.listdir(audio_folder) 
    if filename.endswith(('.wav', '.mp3'))
]

# Initialize the final audio segment
final_audio = pydub.AudioSegment.empty()

# Randomly stitch audio until target duration is reached
while len(final_audio) < target_duration:
  # Randomly select an audio file
  random_file = random.choice(audio_files)

  # Load the audio file
  audio = pydub.AudioSegment.from_file(random_file)

  # Append silence
  audio_with_silence = add_silence(audio)

  # Append to the final audio
  final_audio += audio_with_silence

# Trim the audio if it exceeds the target duration
if len(final_audio) > target_duration:
  final_audio = final_audio[:target_duration]

# Export the final audio file
final_audio.export(output_path, format="mp3")

print(f"Audio files stitched and saved as {output_path}")