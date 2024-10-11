import requests
import json
import os
import chardet
import time
from pydub import AudioSegment

# Define constants for the script
CHUNK_SIZE = 1024
XI_API_KEY = "id_key"
VOICE_IDS = {
    "Zeno.txt": "pzrhJDAsvLBKznXczPvF",  # Voice ID for Zeno
    "Stoic Philosopher.txt": "GRxyBIYvuPkKIpWjqzA2", # Voice ID for Stoic Philosopher
    "Zen Monk.txt": "LipOM79LKgtTo7mSJlVl"  # Voice ID for Zen Monk
} 
OUTPUT_FOLDER = r"E:\Python_Practice\AutoElevenLabs_Combiner\OUTPUT"  # Folder to save output audio files
FINAL_FOLDER = r"E:\Python_Practice\AutoElevenLabs_Combiner\FINAL"  # Folder to save the final combined audio
TEXT_FOLDER = r"E:\Python_Practice\AutoElevenLabs_Combiner\TEXT"  # Folder to read text files

# Create output folders if they don't exist
def create_output_folders():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(FINAL_FOLDER, exist_ok=True)

# Function to process a single text file
def process_text_file(text_file):
    # Construct the full path to the text file
    text_path = os.path.join(TEXT_FOLDER, text_file)

    # Read the text file with encoding detection
    with open(text_path, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)['encoding']
        with open(text_path, "r", encoding=encoding) as f:
            TEXT_TO_SPEAK = f.read()

    # Get the appropriate voice ID for the file
    voice_id = VOICE_IDS.get(text_file)
    if not voice_id:
        print(f"No voice ID found for {text_file}. Skipping...")
        return

    # Construct the TTS API request URL
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

    # Set up headers and data for the API request
    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }
    data = {
        "text": TEXT_TO_SPEAK,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    # Make the POST request to the TTS API and stream the response
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    # Check if the request was successful
    if response.ok:
        # Create an output filename and path
        output_filename = f"{os.path.splitext(text_file)[0]}.mp3"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Write the streamed response to the output file
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)

        # Inform the user of success and move the text file (optional)
        print(f"Audio stream saved successfully to: {output_path}")
        processed_folder = "processed_text"
        os.makedirs(processed_folder, exist_ok=True)
        os.rename(text_path, os.path.join(processed_folder, text_file))
    else:
        print(response.text)

    time.sleep(1)

# Function to combine multiple audio files
def combine_audio(OUTPUT_FOLDER, FINAL_FOLDER, filenames):
    combined_audio = AudioSegment.empty()
    for filename in filenames:
        audio_file = os.path.join(OUTPUT_FOLDER, filename)
        segment = AudioSegment.from_mp3(audio_file)
        combined_audio += segment

    output_filename = "combined_audio.mp3"
    output_path = os.path.join(FINAL_FOLDER, output_filename)
    combined_audio.export(output_path, format="mp3")

    print(f"Audio files combined and saved to: {output_path}")

    # Move the processed audio files to a "processed" folder
    processed_audio = "processed_audio"
    os.makedirs(processed_audio, exist_ok=True)
    for filename in filenames:
        audio_path = os.path.join(OUTPUT_FOLDER, filename)
        os.rename(audio_path, os.path.join(processed_audio, filename))

# Main loop to process text files
def main():
    create_output_folders()
    while True:
        text_files = [f for f in os.listdir(TEXT_FOLDER) if f.endswith(".txt")]
        if not text_files:
            print("No text files found. Waiting for 5 seconds...")
            time.sleep(5)
            break  # Break the loop if no files found.

        for text_file in text_files:
            process_text_file(text_file)

    # File names in order
    filenames = ["Zeno.mp3", "Stoic Philosopher.mp3", "Zen Monk.mp3"]

    # Combine the audio files
    combine_audio(OUTPUT_FOLDER, FINAL_FOLDER, filenames)

if __name__ == "__main__":
    main()