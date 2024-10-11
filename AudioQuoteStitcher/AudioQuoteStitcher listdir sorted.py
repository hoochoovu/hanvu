import os
import pydub

# Function to append 2 seconds of silence
def add_silence(audio_segment):
  silence = pydub.AudioSegment.silent(duration=2000)  # 2 seconds in milliseconds
  return audio_segment + silence

# Path to the folder containing audio files
audio_folder = r"E:\ChatBot Therapy\Marcus Aurelius\Marcus Aurelius Audio Files\8th Book"

# Set the output path for the stitched audio file
output_path = r"Output/The 8th Book (All Chapters).mp3"  # Replace with your desired output path

# Create an empty list to store the audio segments
audio_segments = []

# Iterate through all files in the folder
for filename in os.listdir(audio_folder):
    if filename.endswith(('.wav', '.mp3')):  # Adjust file extensions if needed
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