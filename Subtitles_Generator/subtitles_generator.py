import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip, AudioFileClip

def extract_audio(file_path):
    # Extract audio from video
    if file_path.lower().endswith(('.mp4', '.mkv', '.avi', '.mov')):
        clip = VideoFileClip(file_path)
        audio_path = file_path.replace(file_path.split('.')[-1], 'wav')
        clip.audio.write_audiofile(audio_path)
        return audio_path
    elif file_path.lower().endswith(('.mp3', '.wav', '.flac', '.aac', '.ogg')):
        return file_path
    else:
        raise ValueError("Unsupported file type.")

def generate_subtitles(audio_path, txt_output_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio_path)

    with audio_file as source:
        audio_data = recognizer.record(source)

    # Recognize speech using Google Web Speech API
    try:
        transcript = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        transcript = "[Unintelligible]"
    except sr.RequestError as e:
        transcript = f"[Error]: {e}"

    # Save to txt file with timestamps
    with open(txt_output_path, 'w') as f:
        lines = transcript.split('. ')
        for idx, line in enumerate(lines):
            start_time = idx * 2  # Adjust time interval for each line
            end_time = (idx + 1) * 2
            f.write(f"{start_time}-{end_time}: {line}\n")

def process_folder(input_folder, output_folder):
    for root, _, files in os.walk(input_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                audio_path = extract_audio(file_path)
                output_path = os.path.join(output_folder, os.path.relpath(root, input_folder))
                os.makedirs(output_path, exist_ok=True)
                txt_output_path = os.path.join(output_path, f"{os.path.splitext(file)[0]}.txt")
                generate_subtitles(audio_path, txt_output_path)
                print(f"Subtitles generated for {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

# Replace with your input and output folder paths
input_folder = 'input'
output_folder = 'output'

process_folder(input_folder, output_folder)
