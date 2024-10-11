import requests
import os
import subprocess
import random
import shutil
import json
import datetime
import chardet
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold


# Constants
CHUNK_SIZE = 1024
XI_API_KEY = "id_key"
VOICE_ID = "id_key"

# Folder paths
INPUT_TEXT_FOLDER = "input_text"
OUTPUT_TEXT_FOLDER = "output_text"
GEN_AUDIO_FOLDER = "gen_audio"
VIDEO_INPUT_FOLDER = r"E:\Dataset\PEXELS\All_Monk_Pray_Happiness_Peace_Animals"
AUDIO_INPUT_FOLDER = r"E:\Dataset\PEXELS\ALL_AUDIO_converted_finished"
OUTPUT_FOLDER = "output"
FINISHED_VIDEOS_FOLDER = os.path.join(OUTPUT_FOLDER, "Finished Videos")
PROCESSED_FOLDER = "Processed"
WORK_TEXT_FOLDER = "work_text"  # New folder for working copies

# Create output folders if they don't exist
os.makedirs(OUTPUT_TEXT_FOLDER, exist_ok=True)
os.makedirs(GEN_AUDIO_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(FINISHED_VIDEOS_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(WORK_TEXT_FOLDER, exist_ok=True) 

# --- Text Content Generation ---

def generate_text_content(filepath, custom_prompt_file):
    """Generates text content using Gemini and saves it to a file."""

    # Read custom prompt from file
    with open(custom_prompt_file, "r", encoding='utf-8') as f:
        custom_prompt = f.read()

    # Gemini processing
    genai.configure(api_key = "id_key")
    model = genai.GenerativeModel('gemini-1.5-flash')

    with open(filepath, "r", encoding='utf-8') as f:
        file_content = f.read()
    prompt = f"{file_content}\n\n{custom_prompt}"
    response = model.generate_content(
        prompt,
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    )

    output_filename = f"[Original]-{os.path.basename(filepath)}"
    output_filepath = os.path.join(OUTPUT_TEXT_FOLDER, output_filename)

    with open(output_filepath, "w", encoding='utf-8') as f:
        f.write(response.text)
    print(f"Processed file: {os.path.basename(filepath)}")

    # Move processed file to "Processed" folder
    shutil.move(filepath, os.path.join(PROCESSED_FOLDER, output_filename))


# --- Audio Content Generation ---

def generate_audio_content(text_path, gen_audio_folder):
    """Generates audio content from text using ElevenLabs and saves it."""

    with open(text_path, 'rb') as f:
        data = f.read()
        encoding = chardet.detect(data)['encoding']
        with open(text_path, "r", encoding=encoding) as f:
            TEXT_TO_SPEAK = f.read()

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
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

    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    if response.ok:
        output_filename = f"{os.path.splitext(os.path.basename(text_path))[0]}.mp3"
        output_path = os.path.join(gen_audio_folder, output_filename)

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        print(f"Audio stream saved successfully to: {output_path}")

        # Move processed file to "Processed" folder
        shutil.move(text_path, os.path.join(PROCESSED_FOLDER, output_filename))
    else:
        print(response.text)

# --- Audio/Video Content Generation ---

def get_file_duration(file_path):
    print(f"Getting duration for: {file_path}")
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    try:
        output = subprocess.check_output(command).decode('utf-8').strip()
        return float(output)
    except subprocess.CalledProcessError as e:
        print(f"Error getting file duration: {e}")
        return 0.0

def get_audio_stats(file_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,bit_rate,duration', '-of', 'json', file_path]
    try:
        output = subprocess.check_output(command).decode('utf-8')
        return output
    except subprocess.CalledProcessError as e:
        print(f"Error getting audio stats: {e}")
        return "{}"

def validate_audio_stream(file_path):
    command = ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,sample_rate,channels,bit_rate,duration', '-of', 'json', file_path]
    try:
        output = subprocess.check_output(command).decode('utf-8')
        audio_info = json.loads(output)

        if 'streams' in audio_info and len(audio_info['streams']) > 0:
            stream = audio_info['streams'][0]
            codec = stream['codec_name']
            sample_rate = int(stream['sample_rate'])
            channels = stream['channels']
            bit_rate = stream['bit_rate']
            duration = stream['duration']

            if codec not in ['aac', 'mp3', 'flac']:
                print(f"Invalid codec: {codec}")
                return False

            if sample_rate != 44100:
                print(f"Invalid sample rate: {sample_rate}")
                return False

            return True
        else:
            print("No audio streams found in the file.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error validating audio stream: {e}")
        return False

def convert_audio_sample_rate(input_file, output_file, target_sample_rate=44100):
    """Converts the sample rate of an audio file using FFmpeg only if necessary."""
    audio_info = get_audio_stats(input_file)  # Get audio stats first
    audio_info = json.loads(audio_info)
    if 'streams' in audio_info and len(audio_info['streams']) > 0:
        stream = audio_info['streams'][0]
        current_sample_rate = int(stream['sample_rate'])
        if current_sample_rate == target_sample_rate:
            print(f"Skipping conversion: {input_file} already has the desired sample rate.")
            shutil.copyfile(input_file, output_file)  # Copy the file if it's already correct
            return

    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-ar', str(target_sample_rate),
        '-c:a', 'libmp3lame',  # Use libmp3lame encoder
        output_file
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting audio sample rate: {e}")

def convert_video_to_mp4(input_file, output_file):
    ffmpeg_command = [
        'ffmpeg',
        '-i', input_file,
        '-c:v', 'libx264',  # Choose an encoder (like libx264)
        '-c:a', 'aac',  # Choose an audio codec (like aac)
        output_file
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error converting video to MP4: {e}")

def merge_media(input_videos, input_audios, output_folder, target_duration, target_resolution, target_fps=24):
    """Merges videos and audios to match the target duration."""
    print("Attempting Media Merge")
    total_duration = 0
    merged_videos = []
    merged_audios = []

    while total_duration < target_duration:
        # Choose random video and audio
        random_video = random.choice(input_videos)
        random_audio = random.choice(input_audios)

        merged_videos.append(random_video)
        merged_audios.append(random_audio)

        total_duration += get_file_duration(random_video)  # Use video duration for overall time

    # Convert videos to MP4 if necessary
    for i, video_file in enumerate(merged_videos):
        if not video_file.lower().endswith(".mp4"):
            converted_video_path = os.path.splitext(video_file)[0] + ".mp4"
            convert_video_to_mp4(video_file, converted_video_path)
            merged_videos[i] = converted_video_path

    # Convert audio sample rate only when needed (during merging)
    for i, audio_file in enumerate(merged_audios):
        audio_info = get_audio_stats(audio_file)
        audio_info_dict = json.loads(audio_info)
        if 'streams' in audio_info_dict and len(audio_info_dict['streams']) > 0:
            stream = audio_info_dict['streams'][0]
            current_sample_rate = int(stream['sample_rate'])
            if current_sample_rate != 44100:
                converted_audio_path = os.path.join(output_folder, f"converted_audio_{i}.mp3")
                convert_audio_sample_rate(audio_file, converted_audio_path)
                merged_audios[i] = converted_audio_path

    # Trim audio and video if total duration exceeds target duration
    if total_duration > target_duration:
        # Trim video
        trim_command = ['ffmpeg', '-i', merged_videos[0], '-t', str(target_duration), '-c:v', 'copy', '-c:a', 'copy', os.path.join(output_folder, "trimmed_video.mp4")]
        print(f"Running FFmpeg command: {' '.join(trim_command)}")
        try:
            subprocess.run(trim_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error trimming video: {e}")
            return

        # Trim audio
        trim_command = ['ffmpeg', '-i', merged_audios[0], '-t', str(target_duration), '-c:a', 'copy', os.path.join(output_folder, "trimmed_audio.mp3")]
        print(f"Running FFmpeg command: {' '.join(trim_command)}")
        try:
            subprocess.run(trim_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error trimming audio: {e}")
            return

        merged_videos = [os.path.join(output_folder, "trimmed_video.mp4")]
        merged_audios = [os.path.join(output_folder, "trimmed_audio.mp3")]

    # Combine videos using ffmpeg
    inputs = []
    for video in merged_videos:
        inputs.extend(['-i', video])

    filter_complex_parts = []
    for i in range(len(merged_videos)):
        filter_complex_parts.append(f"[{i}:v]scale={target_resolution[0]}:{target_resolution[1]}[v{i}];")

    concat_filter = f"concat=n={len(merged_videos)}:v=1[outv]"
    filter_complex_parts.append("".join(f"[v{i}]" for i in range(len(merged_videos))))
    filter_complex_parts.append(concat_filter)
    filter_complex = "".join(filter_complex_parts)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    merged_video_path = os.path.join(output_folder, f"merged_video_{timestamp}.mp4")

    ffmpeg_command = [
        'ffmpeg',
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-c:v', 'libx264',
        '-r', str(target_fps),
        '-t', str(target_duration),  # Trim video to target duration
        merged_video_path
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error merging videos: {e}")
        return

    # Combine audios using ffmpeg
    inputs = [item for audio in merged_audios for item in ('-i', audio)]
    filter_complex = "".join(f"[{i}:a]" for i in range(len(merged_audios))) + f"concat=n={len(merged_audios)}:v=0:a=1[outa]"

    merged_audio_path = os.path.join(output_folder, "merged_audio.mp3")
    ffmpeg_command = [
        'ffmpeg', 
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outa]', 
        '-c:a', 'libmp3lame',
        '-ar', '44100',
        '-t', str(target_duration),  # Trim audio to target duration
        merged_audio_path
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
        if not os.path.exists(merged_audio_path):
            print(f"Error: Merged audio file {merged_audio_path} was not created.")
            return None, None
    except subprocess.CalledProcessError as e:
        print(f"Error merging audio: {e}")
        return None, None

    return merged_video_path, merged_audio_path

def main():
    target_resolution = (1920, 1080)
    target_fps = 24
    original_audio_volume = 4.0
    merged_audio_volume = 0.10

    # Get text files from input_text folder
    text_files = [os.path.join(INPUT_TEXT_FOLDER, f) for f in os.listdir(INPUT_TEXT_FOLDER) if f.endswith(".txt")]
    
    # Outer loop iterates through each text file
    for text_file in text_files:
        print(f"Processing text file: {text_file}")
        i = 0
        # Delete temporary files created during this iteration
        files_to_delete = [
            f"final_audio_{i+1}.mp3",
            f"merged_audio_{i+1}.aac",
            f"merged_video_{i+1}.mp4",
            f"mixed_audio_{i+1}.aac",
            f"original_audio_{i+1}.mp3",
            f"reencoded_original_audio_{i+1}.mp3"
        ]
        for file_name in files_to_delete:
            file_path = os.path.join(OUTPUT_FOLDER, file_name)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except FileNotFoundError:
                # File doesn't exist, so do nothing
                pass

        start_time = datetime.datetime.now()  # Start timer   

        # 0. Copy text files to "work_text" folder
        shutil.copyfile(text_file, os.path.join(WORK_TEXT_FOLDER, os.path.basename(text_file)))

        # 1. Text Content Generation
        custom_prompt_file = "prompt.txt"  # Path to your prompt file
        filepath = os.path.join(WORK_TEXT_FOLDER, os.listdir(WORK_TEXT_FOLDER)[0])
        generate_text_content(filepath, custom_prompt_file)

        # 2. Audio Content Generation (within the same loop as text generation)
        filepath = os.path.join(OUTPUT_TEXT_FOLDER, os.listdir(OUTPUT_TEXT_FOLDER)[0])
        generate_audio_content(filepath, GEN_AUDIO_FOLDER)

        # 3. Audio/Video Content Generation (Iterate through audio files)
        original_audio_files = [os.path.join(GEN_AUDIO_FOLDER, f) for f in os.listdir(GEN_AUDIO_FOLDER) if f.endswith(('.mp3', '.wav', '.ogg'))]
        for i, original_audio_file in enumerate(original_audio_files):
            print(f"Processing audio file {i+1}")

            # Get original audio duration
            original_audio_duration = get_file_duration(original_audio_file)
            print(f"Original audio duration: {original_audio_duration}")

            # 3.1 Merge videos (mute and trim)
            video_files = []
            for root, _, files in os.walk(VIDEO_INPUT_FOLDER):
                for file in files:
                    if file.lower().endswith(('.mp4', '.mov', '.avi')):
                        video_files.append(os.path.join(root, file))

            merged_videos = []
            total_video_duration = 0
            while total_video_duration < original_audio_duration:
                random_video = random.choice(video_files)
                merged_videos.append(random_video)
                total_video_duration += get_file_duration(random_video)

            # Convert to MP4 if necessary and trim
            for j, video_file in enumerate(merged_videos):
                if not video_file.lower().endswith(".mp4"):
                    converted_video_path = os.path.splitext(video_file)[0] + ".mp4"
                    convert_video_to_mp4(video_file, converted_video_path)
                    merged_videos[j] = converted_video_path
            merged_video_path = os.path.join(OUTPUT_FOLDER, f"merged_video_{i+1}.mp4")
            inputs = ['-i', merged_videos[0]]
            for j in range(1, len(merged_videos)):
                inputs.extend(['-i', merged_videos[j]])

            filter_complex_parts = []
            for j in range(len(merged_videos)):
                filter_complex_parts.append(f"[{j}:v]scale={target_resolution[0]}:{target_resolution[1]}[v{j}];")

            concat_filter = f"concat=n={len(merged_videos)}:v=1[outv]"
            filter_complex_parts.append("".join(f"[v{j}]" for j in range(len(merged_videos))))
            filter_complex_parts.append(concat_filter)
            filter_complex = "".join(filter_complex_parts)

            ffmpeg_command = [
                'ffmpeg',
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-c:v', 'libx264',
                '-r', str(target_fps),
                '-t', str(original_audio_duration),  # Trim to original audio duration
                '-an',  # Mute the video
                merged_video_path
            ]
            print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
            try:
                subprocess.run(ffmpeg_command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error merging videos: {e}")
                return

            # 3.2 Merge audio (convert to AAC if necessary, then to MP3 if needed, and trim)
            audio_files = []
            for root, _, files in os.walk(AUDIO_INPUT_FOLDER):
                for file in files:
                    if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                        audio_files.append(os.path.join(root, file))

            merged_audios = []
            total_audio_duration = 0
            while total_audio_duration < original_audio_duration:
                random_audio = random.choice(audio_files)

                # Convert to AAC if necessary
                if not validate_audio_stream(random_audio):
                    converted_audio_path = os.path.join(OUTPUT_FOLDER, f"converted_audio_{i+1}_{len(merged_audios)}.mp3")
                    convert_audio_sample_rate(random_audio, converted_audio_path)
                    merged_audios.append(converted_audio_path)
                else:
                    merged_audios.append(random_audio)
                total_audio_duration += get_file_duration(random_audio)

            # Merge audio using AAC codec
            merged_audio_path = os.path.join(OUTPUT_FOLDER, f"merged_audio_{i+1}.aac")  # Save as AAC first
            inputs = ['-i', merged_audios[0]]
            for j in range(1, len(merged_audios)):
                inputs.extend(['-i', merged_audios[j]])

            filter_complex = "".join(f"[{j}:a]" for j in range(len(merged_audios))) + f"concat=n={len(merged_audios)}:v=0:a=1[outa]"

            ffmpeg_command = [
                'ffmpeg',
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[outa]',
                '-c:a', 'aac',  # Encode to AAC
                '-ar', '44100',
                '-t', str(original_audio_duration),
                merged_audio_path
            ]
            print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
            try:
                subprocess.run(ffmpeg_command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error merging audio: {e}")
                return

            # 3.3 Re-encode original audio (to the correct sample rate)
            reencoded_original_audio_path = os.path.join(OUTPUT_FOLDER, f"reencoded_original_audio_{i+1}.mp3")
            convert_audio_sample_rate(original_audio_file, reencoded_original_audio_path)

            # 3.4 Mix re-encoded merged audio (AAC) with re-encoded original audio (MP3)
            mixed_audio_path = os.path.join(OUTPUT_FOLDER, f"mixed_audio_{i+1}.aac")
            ffmpeg_command = [
                'ffmpeg',
                '-i', merged_audio_path,  # Use AAC-encoded merged audio
                '-i', reencoded_original_audio_path,
                '-filter_complex',
                f'[0:a]volume={merged_audio_volume}[audio1];'
                f'[1:a]volume={original_audio_volume}[audio2];'
                f'[audio1][audio2]amix=inputs=2[outa]',
                '-map', '[outa]',
                '-c:a', 'aac',  # Encode to AAC
                mixed_audio_path
            ]
            print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
            try:
                subprocess.run(ffmpeg_command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error mixing audio: {e}")
                return

            # Convert the mixed audio to MP3
            final_audio_path = os.path.join(OUTPUT_FOLDER, f"final_audio_{i+1}.mp3")
            ffmpeg_command = [
                'ffmpeg',
                '-i', mixed_audio_path,
                '-c:a', 'libmp3lame',  # Encode to MP3
                '-ar', '44100',
                final_audio_path
            ]
            print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
            try:
                subprocess.run(ffmpeg_command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error converting final audio to MP3: {e}")
                return

            # 3.5 Merge final video and audio
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            final_video_path = os.path.join(FINISHED_VIDEOS_FOLDER, f"new_video_{timestamp}_{i+1}.mp4")
            ffmpeg_command = [
                'ffmpeg',
                '-i', os.path.join(OUTPUT_FOLDER, f"merged_video_{i+1}.mp4"),
                '-i', final_audio_path,
                '-c:v', 'copy', '-c:a', 'copy',
                final_video_path
            ]
            print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
            try:
                subprocess.run(ffmpeg_command, check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error merging final video: {e}")
                return

            print(f"Final video path: {final_video_path}")
            shutil.copyfile(original_audio_file, os.path.join(OUTPUT_FOLDER, f"original_audio_{i+1}.mp3"))

            # Move processed files to "Processed" folder
            for folder in [GEN_AUDIO_FOLDER, OUTPUT_TEXT_FOLDER, WORK_TEXT_FOLDER]:
                for filename in os.listdir(folder):
                    if filename.endswith((".txt", ".mp3")):  # Adjust file extensions if needed
                        shutil.move(os.path.join(folder, filename), os.path.join(PROCESSED_FOLDER, filename))

        # Move processed files to "Processed" folder
        for folder in [GEN_AUDIO_FOLDER, OUTPUT_TEXT_FOLDER, WORK_TEXT_FOLDER]:
            for filename in os.listdir(folder):
                if filename.endswith((".txt", ".mp3")):  # Adjust file extensions if needed
                    shutil.move(os.path.join(folder, filename), os.path.join(PROCESSED_FOLDER, filename))

        end_time = datetime.datetime.now()
        total_time = end_time - start_time
        print(f"Total runtime for this text file: {total_time}")
        print(f"Original audio duration: {original_audio_duration}")  # This will print the duration of the last processed file

if __name__ == "__main__":
    main()