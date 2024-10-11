import os
import pydub

# Set the input and output folder paths
input_folder = r"E:\Python_Practice\Silence Adder\Input"
output_folder = r"E:\Python_Practice\Silence Adder\Output"

# Create the output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate through all MP3 files in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".mp3"):
        # Construct the full path to the file
        file_path = os.path.join(input_folder, filename)

        # Load the audio file using pydub
        audio = pydub.AudioSegment.from_mp3(file_path)

        # Create a 3-second silence segment
        silence = pydub.AudioSegment.silent(duration=3000)

        # Append the silence to the end of the audio
        audio_with_silence = audio + silence

        # Output the modified audio file to the output folder
        output_file_path = os.path.join(output_folder, filename)
        audio_with_silence.export(output_file_path, format="mp3")

        print(f"Added 3 seconds of silence to {filename}")