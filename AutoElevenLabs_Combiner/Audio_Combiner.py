import os
from pydub import AudioSegment

def combine_audio(input_folder, output_folder, filenames):
  """
  Combines multiple audio files into one, appending them in the specified order.

  Args:
    input_folder: The folder containing the input audio files.
    output_folder: The folder where the combined audio file will be saved.
    filenames: A list of filenames in the order they should be combined.
  """

  combined_audio = AudioSegment.empty()
  for filename in filenames:
    audio_file = os.path.join(input_folder, filename)
    segment = AudioSegment.from_mp3(audio_file)
    combined_audio += segment

  output_filename = "combined_audio.mp3"
  output_path = os.path.join(output_folder, output_filename)

  combined_audio.export(output_path, format="mp3")

  print(f"Audio files combined and saved to: {output_path}")

# Input and output folder paths
input_folder = r"E:\Python_Practice\AutoElevenLabs_Combiner\OUTPUT"  # Change this to your actual input folder
output_folder = r"E:\Python_Practice\AutoElevenLabs_Combiner\FINAL" # Change this to your actual output folder

# File names in order
filenames = ["Zeno.mp3", "Stoic_Philosopher.mp3", "Zen_Monk.mp3"]

# Combine the audio files
combine_audio(input_folder, output_folder, filenames)