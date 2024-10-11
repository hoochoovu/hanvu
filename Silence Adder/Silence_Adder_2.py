import os
import pydub

# Set the input and output folder paths
input_folder = r"E:\Dataset\All Audiobook\Stoic Texts\Original"
output_folder = r"E:\Dataset\All Audiobook\Stoic Texts\Silence Added"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate through all MP3 files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".mp3"):
        # Construct the full path to the file
        file_path = os.path.join(input_folder, filename)

        # Load the audio file using pydub
        audio = pydub.AudioSegment.from_mp3(file_path)

        # Create silence segments
        start_silence = pydub.AudioSegment.silent(duration=500)  # .5 second silence
        end_silence = pydub.AudioSegment.silent(duration=2500)  # 2.5 seconds silence

        # Append silence to the beginning and end
        audio_with_silence = start_silence + audio + end_silence

        # Output the modified audio file to the output folder
        output_file_path = os.path.join(output_folder, filename)
        audio_with_silence.export(output_file_path, format="mp3")

        print(f"Added 0.5 second silence at the beginning and 2.5 seconds at the end of {filename}")