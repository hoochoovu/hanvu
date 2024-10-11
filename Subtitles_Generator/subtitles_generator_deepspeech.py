import os
import wave
import numpy as np
import tensorflow as tf
from deepspeech import Model

# Set up paths
input_folder = 'input'
output_folder = 'output'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Path to your DeepSpeech model and scorer
model_path = 'deepspeech-0.9.3-models.pbmm'
scorer_path = 'deepspeech-0.9.3-models.scorer'

# Load DeepSpeech model
ds_model = Model(model_path)
ds_model.enableExternalScorer(scorer_path)

# Function to read audio file
def read_wav_file(filename):
    with wave.open(filename, 'rb') as w:
        frames = w.getnframes()
        buffer = w.readframes(frames)
        rate = w.getframerate()
        return buffer, rate

# Process each audio file
for file_name in os.listdir(input_folder):
    if file_name.endswith('.wav'):
        file_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + '.txt')

        # Read audio data
        audio_data, sample_rate = read_wav_file(file_path)
        audio_data = np.frombuffer(audio_data, dtype=np.int16)

        # Use the TensorFlow GPU to perform inference
        with tf.device('/GPU:0'):  # Force the use of GPU
            ds_model.setBeamWidth(500)  # Optionally adjust the beam width
            ds_model.setScorerAlphaBeta(0.75, 1.85)
            transcript = ds_model.sttWithMetadata(audio_data, sample_rate)
        
        # Write the transcript to a file
        with open(output_path, 'w') as output_file:
            for item in transcript.transcripts[0].tokens:
                time_offset = item.start_time  # Start time of the word
                word = item.text  # The word itself
                output_file.write(f"{time_offset:.2f}\t{word}\n")

        print(f"Subtitles generated for {file_name} at {output_path}")

print("Subtitle generation completed.")
