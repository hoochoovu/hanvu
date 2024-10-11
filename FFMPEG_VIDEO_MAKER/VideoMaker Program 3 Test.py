import os
import subprocess
import random
import shutil
import json
import datetime

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

def merge_videos(input_videos, output_folder, target_duration, target_resolution, target_fps=24):
    print("Attempting Video Merge")
    total_duration = 0
    merged_videos = []
    while total_duration < target_duration:
        random_video = random.choice(input_videos)
        merged_videos.append(random_video)
        total_duration += get_file_duration(random_video)

    # Convert all videos to MP4 (if necessary)
    for i, video_file in enumerate(merged_videos):
        if not video_file.lower().endswith(".mp4"):
            converted_video_path = os.path.splitext(video_file)[0] + ".mp4"
            convert_video_to_mp4(video_file, converted_video_path)  # Function to convert
            merged_videos[i] = converted_video_path

    # No audio processing needed here

    inputs = [] 
    for video in merged_videos:
        inputs.extend(['-i', video])

    filter_complex_parts = []
    for i in range(len(merged_videos)):
        # Only scale the video, no audio processing
        filter_complex_parts.append(f"[{i}:v]scale={target_resolution[0]}:{target_resolution[1]}[v{i}];") 

    # Dynamically create the concat filter string
    concat_filter = f"concat=n={len(merged_videos)}:v=1[outv]"  # Only concatenate video
    filter_complex_parts.append("".join(f"[v{i}]" for i in range(len(merged_videos))))  # No audio mapping
    filter_complex_parts.append(concat_filter)

    filter_complex = "".join(filter_complex_parts)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_folder, f"merged_video_{timestamp}.mp4")

    ffmpeg_command = [
        'ffmpeg', 
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outv]',
        '-c:v', 'libx264',  # Only encode video
        '-r', str(target_fps),  # Set the target frame rate
        output_file
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error merging videos: {e}")

def merge_audio(input_audios, output_file, target_duration, reencoded_merged_audio_path, reencoded_original_audio_path):
    print("Attempting Audio Merge")
    # Create the "converted" folder if it doesn't exist
    converted_folder = os.path.join(os.path.dirname(output_file), "converted") 
    if not os.path.exists(converted_folder):
        os.makedirs(converted_folder)

    # 1. Convert audio files to 44100 Hz sample rate and move to the "converted" folder
    # (You can add this conversion step if you need it)

    # 2. Validate audio streams (after conversion)
    for i, audio_file in enumerate(input_audios):
        audio_info = get_audio_stats(audio_file)
        audio_info_dict = json.loads(audio_info)  # Convert to dictionary
        print(f"Audio File {i+1}: {audio_info_dict}")

        if 'streams' not in audio_info_dict or len(audio_info_dict['streams']) == 0:
            print(f"Invalid audio stream in file: {audio_file}")
            return

    # 3. Calculate total duration and select audio segments
    total_duration = 0
    merged_audios = []
    while total_duration < target_duration:
        random_audio = random.choice(input_audios)
        merged_audios.append(random_audio)
        total_duration += get_file_duration(random_audio)

    # 4. Trim excess audio
    if total_duration > target_duration:
        trim_command = ['ffmpeg', '-i', output_file, '-t', str(target_duration), '-c:a', 'copy', output_file]
        print(f"Running FFmpeg command: {' '.join(trim_command)}")
        try:
            subprocess.run(trim_command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error trimming audio: {e}")
            return

    # 5. Construct the FFmpeg command to concatenate audios
    inputs = [item for audio in merged_audios for item in ('-i', audio)]
    filter_complex = "".join(f"[{i}:a]" for i in range(len(merged_audios))) + f"concat=n={len(merged_audios)}:v=0:a=1[outa]"
    
    ffmpeg_command = [
        'ffmpeg', 
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outa]', 
        '-c:a', 'libmp3lame',
        '-ar', '44100',  # Set sample rate if needed
        output_file
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error merging audio: {e}")
        return

    # 6. Mix original audio with merged audio
    mix_command = [
            'ffmpeg',
            '-i', reencoded_merged_audio_path, 
            '-i', reencoded_original_audio_path,
            '-filter_complex', '[0:a]volume=0.5[audio1];[1:a]volume=0.5[audio2];[audio1][audio2]amix=inputs=2[outa]',
            '-map', '0:v', '-map', '[outa]',
            '-c:v', 'copy', '-c:a', 'aac',
            os.path.join(output_folder, "final_audio.mp3")  # Corrected output path
        ]
    print(f"Running FFmpeg command: {' '.join(mix_command)}")
    try:
        subprocess.run(mix_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error mixing audio: {e}")
        return

    merged_audio_info = get_audio_stats(output_file)
    print(f"Merged Audio: {merged_audio_info}")

    if validate_audio_stream(output_file):
        print("Merged audio file is valid.")
    else:
        print("Merged audio file is invalid.")

def reencode_audio(input_file, output_file):
    reencode_command = ['ffmpeg', '-i', input_file, '-c:a', 'libmp3lame', '-ar', '44100', '-ac', '2', output_file]
    print(f"Running FFmpeg command: {' '.join(reencode_command)}")
    try:
        subprocess.run(reencode_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error re-encoding audio: {e}")

      
def main():
    original_audio_path = r"E:\Python_Practice\FFMPEG_VIDEO_MAKER\audiofiletomake\[Complete]-CLEANTHES-He-needs-little-who-desires.mp3"
    video_input_folder = r"E:\Dataset\PEXELS\All_Scrape\All_Videos"
    audio_input_folder = r"E:\Python_Practice\FFMPEG_VIDEO_MAKER\output\converted_finished"  # Original audio input folder
    output_folder = "output"

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Delete potential files from previous runs
    for file_name in ['merged_audio.mp3', 'original_audio.mp3', 'reencoded_merged_audio.mp3', 'reencoded_original_audio.mp3', 'final_audio']:
        file_path = os.path.join(output_folder, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    # Get original audio duration
    original_audio_duration = get_file_duration(original_audio_path)
    print(f"Original audio duration: {original_audio_duration}")

    video_files = []
    for root, _, files in os.walk(video_input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.avi')):
                video_files.append(os.path.join(root, file))

    print("Attempting Merge")
    merged_audio_path = os.path.join(output_folder, "merged_audio.mp3")

    # 1. Load and Convert Audio Files
    converted_audio_folder = os.path.join(output_folder, "converted") 
    if not os.path.exists(converted_audio_folder):
        os.makedirs(converted_audio_folder)

    audio_files = []
    for root, _, files in os.walk(audio_input_folder):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                audio_files.append(os.path.join(root, file))
                
    # Convert audio files to 44100 Hz sample rate
    for audio_file in audio_files:
        converted_audio_path = os.path.join(converted_audio_folder, os.path.basename(audio_file) + "_converted.mp3")
        convert_audio_sample_rate(audio_file, converted_audio_path)

    # 2. Merge Audio (now using the converted audio)
    audio_files = []  # Reset audio_files
    for root, _, files in os.walk(converted_audio_folder):  # Look for files in "converted" folder
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                audio_files.append(os.path.join(root, file))

    reencoded_merged_audio_path = os.path.join(output_folder, "reencoded_merged_audio.mp3")
    reencode_audio(merged_audio_path, reencoded_merged_audio_path)

    reencoded_original_audio_path = os.path.join(output_folder, "reencoded_original_audio.mp3")
    reencode_audio(original_audio_path, reencoded_original_audio_path)

    target_resolution = (1920, 1080)
    merge_videos(video_files, output_folder, original_audio_duration, target_resolution)

    # Call merge_audio only once for the final merge
    merge_audio(audio_files, merged_audio_path, original_audio_duration, reencoded_merged_audio_path, reencoded_original_audio_path)

    final_video_path = os.path.join(output_folder, "new_video.mp4")
    ffmpeg_command = [
        'ffmpeg',
        '-i', merged_video_path,
        '-i', reencoded_original_audio_path,
        '-filter_complex', '[1:a]volume=0.5[audio2]; [0:a][audio2]amix=inputs=2[outa]',
        '-map', '0:v', '-map', '[outa]',
        '-c:v', 'copy', '-c:a', 'aac',
        final_video_path
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    try:
        subprocess.run(ffmpeg_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error merging final video: {e}")

    shutil.copyfile(original_audio_path, os.path.join(output_folder, "original_audio.mp3"))

if __name__ == "__main__":
    main()