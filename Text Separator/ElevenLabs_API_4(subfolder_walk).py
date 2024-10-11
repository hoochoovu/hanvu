import requests
import json
import os
import chardet
import time

# Define constants for the script
CHUNK_SIZE = 4096
XI_API_KEY = "id_key"
VOICE_ID = "id_key"
INPUT_FOLDER = r"E:\Python_Practice\Text Separator\New Quotes List\output"  # Main input folder

# Construct the URL for the Text-to-Speech API request
tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

# Set up headers for the API request, including the API key for authentication
headers = {
    "Accept": "application/json",
    "xi-api-key": XI_API_KEY
}

def process_text_file(text_path, audio_path):
    try:
        with open(text_path, 'rb') as f:
            data = f.read()
            encoding = chardet.detect(data)['encoding']  # Detect encoding
            
            with open(text_path, "r", encoding=encoding) as f:  # Read with detected encoding
                TEXT_TO_SPEAK = f.read()
    except Exception as e:
        print(f"Error reading file {text_path}: {e}")
        return False

    # Set up the data payload for the API request
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

    # Make the POST request to the TTS API with headers and data, enabling streaming response
    try:
        response = requests.post(tts_url, headers=headers, json=data, stream=True)
    except Exception as e:
        print(f"Error making API request for {text_path}: {e}")
        return False

    # Check if the request was successful
    if response.ok:
        try:
            # Open the output file in write-binary mode
            with open(audio_path, "wb") as f:
                # Read the response in chunks and write to the file
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    f.write(chunk)
            # Inform the user of success
            print(f"Audio stream saved successfully to: {audio_path}")
            return True
        except Exception as e:
            print(f"Error saving audio for {text_path}: {e}")
            return False
    else:
        # Print the error message if the request was not successful
        print(response.text)
        return False

# Main loop to process text files in the folder
while True:
    # Get list of subfolders in the input folder
    subfolders = [f.path for f in os.scandir(INPUT_FOLDER) if f.is_dir()]

    # If no subfolders found, sleep for 5 seconds and continue
    if not subfolders:
        print("No subfolders found. Waiting for 5 seconds...")
        time.sleep(5)
        continue

    # Iterate through each subfolder
    for subfolder in subfolders:
        text_folder = os.path.join(subfolder, "Text")
        audio_folder = os.path.join(subfolder, "Audio")

        # Ensure audio folder exists
        os.makedirs(audio_folder, exist_ok=True)

        # Get list of .txt files in the text folder
        text_files = [f for f in os.listdir(text_folder) if f.endswith(".txt")]

        # If no files found, continue to next subfolder
        if not text_files:
            print(f"No text files found in {text_folder}. Moving to next subfolder...")
            continue

        # Iterate through each .txt file
        for text_file in text_files:
            # Construct the full paths
            text_path = os.path.join(text_folder, text_file)
            audio_filename = f"{os.path.splitext(text_file)[0]}.mp3"
            audio_path = os.path.join(audio_folder, audio_filename)

            # Process the text file
            if process_text_file(text_path, audio_path):
                # If successful, remove the original text file
                os.remove(text_path)
            else:
                # If failed, move to next file
                continue

        # Wait for 1 second before processing the next subfolder
        time.sleep(1)