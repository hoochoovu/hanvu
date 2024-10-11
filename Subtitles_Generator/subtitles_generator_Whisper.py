import os
import torch
import numpy as np
from whisper import load_model
from moviepy.editor import VideoFileClip
import librosa

# Set up paths
input_folder = 'input'
output_folder = 'output'

# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

# Load Whisper model
device = "cuda" if torch.cuda.is_available() else "cpu"
model = load_model("base").to(device)

# Function to read audio from file (audio or video)
def read_audio(file_path):
    if file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):  # Video files
        video = VideoFileClip(file_path)
        audio = video.audio.to_soundarray(fps=16000)
        video.close()
        if audio.ndim == 2:
            audio = audio.mean(axis=1)  # Convert stereo to mono
    else:  # Audio files
        audio, _ = librosa.load(file_path, sr=16000)
    
    # Ensure audio is float32 and scale to [-1, 1]
    audio = librosa.util.normalize(audio.astype(np.float32))
    return audio

# Process each file
for file_name in os.listdir(input_folder):
    if file_name.lower().endswith(('.wav', '.mp3', '.flac', '.mp4', '.avi', '.mov', '.mkv')):
        file_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, os.path.splitext(file_name)[0] + '.txt')

        # Read audio data
        audio = read_audio(file_path)

        # Perform inference with Whisper
        with torch.no_grad():
            result = model.transcribe(audio)

        # Write the transcript to a file
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for segment in result['segments']:
                start_time = segment['start']
                text = segment['text'].strip()
                output_file.write(f"{start_time:.2f}\t{text}\n")

        print(f"Subtitles generated for {file_name} at {output_path}")

print("Subtitle generation completed.")