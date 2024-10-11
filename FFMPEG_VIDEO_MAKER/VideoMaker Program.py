import os
import subprocess
import random
import shutil

def get_file_duration(file_path):
    print(f"Getting duration for: {file_path}")
    """Gets the duration of a video or audio file using FFprobe."""
    command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
    output = subprocess.check_output(command).decode('utf-8').strip()
    return float(output)

def merge_videos(input_videos, output_file, target_duration, target_resolution):
    print("Attempting Video Merge")
    """Merges multiple video files using FFmpeg until the target duration is reached, 
    scaling videos to the target resolution.
    """
    total_duration = 0
    merged_videos = []
    while total_duration < target_duration:
        random_video = random.choice(input_videos)
        merged_videos.append(random_video)
        total_duration += get_file_duration(random_video)

    # Construct the FFmpeg command to concatenate videos with resolution scaling
    inputs = []  # Initialize the inputs list
    for video in merged_videos:
        inputs.extend(['-i', video])  # Add video input
    
    filter_complex_parts = []
    for i in range(len(merged_videos)):
        filter_complex_parts.append(f"[{i}:v]scale={target_resolution[0]}:{target_resolution[1]}[v{i}];")
        filter_complex_parts.append(f"[{i}:a]acopy[a{i}];")  # Extract audio from corresponding input

    # Connect video and audio streams for concatenation
    filter_complex_parts.append("".join(f"[v{i}][a{i}]" for i in range(len(merged_videos))))
    filter_complex_parts.append(f"concat=n={len(merged_videos)}:v=1:a=1[outv][outa]")

    filter_complex = "".join(filter_complex_parts)

    ffmpeg_command = [
        'ffmpeg', 
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outv]', '-map', '[outa]', 
        '-c:v', 'libx264', '-c:a', 'aac', 
        output_file
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    subprocess.run(ffmpeg_command, check=True)

def merge_audio(input_audios, output_file, target_duration):
    print("Attempting Audio Merge")
    """Merges multiple audio files using FFmpeg until the target duration is reached."""
    total_duration = 0
    merged_audios = []
    while total_duration < target_duration:
        random_audio = random.choice(input_audios)
        merged_audios.append(random_audio)
        total_duration += get_file_duration(random_audio)
    
    # Construct the FFmpeg command to concatenate audios
    inputs = [item for audio in merged_audios for item in ('-i', audio)]
    filter_complex = "".join(f"[{i}:a]" for i in range(len(merged_audios))) + f"concat=n={len(merged_audios)}:v=0:a=1[outa]"
    
    ffmpeg_command = [
        'ffmpeg', 
        *inputs,
        '-filter_complex', filter_complex,
        '-map', '[outa]', 
        '-c:a', 'aac', 
        output_file
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    subprocess.run(ffmpeg_command, check=True)

    # Trim the merged audio to the target duration
    trim_command = ['ffmpeg', '-i', output_file, '-t', str(target_duration), '-c:a', 'copy', output_file]
    print(f"Running FFmpeg command: {' '.join(trim_command)}")
    subprocess.run(trim_command, check=True)

def reencode_audio(input_file, output_file):
    reencode_command = ['ffmpeg', '-i', input_file, '-c:a', 'libmp3lame', '-ar', '44100', '-ac', '2', output_file]
    print(f"Running FFmpeg command: {' '.join(reencode_command)}")
    subprocess.run(reencode_command, check=True)

def main():
    # Define input and output paths
    original_audio_path = r"E:\Python_Practice\FFMPEG VIDEO MAKER\audiofiletomake\[Complete]-CLEANTHES-He-needs-little-who-desires.mp3"
    video_input_folder = r"E:\Dataset\PEXELS\All_Scrape\All_Videos"
    audio_input_folder = r"E:\Dataset\PEXELS\All_Audio"
    output_folder = "output"

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get original audio duration
    original_audio_duration = get_file_duration(original_audio_path)

    # Find video files in the input folder
    video_files = []
    for root, _, files in os.walk(video_input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mov', '.avi')):
                video_files.append(os.path.join(root, file))

    # Merge audio files until duration exceeds the original audio
    merged_audio_path = os.path.join(output_folder, "merged_audio.mp3")
    audio_files = []
    for root, _, files in os.walk(audio_input_folder):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                audio_files.append(os.path.join(root, file))
    merge_audio(audio_files, merged_audio_path, original_audio_duration)

    # Re-encode the merged audio
    reencoded_merged_audio_path = os.path.join(output_folder, "reencoded_merged_audio.mp3")
    reencode_audio(merged_audio_path, reencoded_merged_audio_path)

    # Re-encode the original audio
    reencoded_original_audio_path = os.path.join(output_folder, "reencoded_original_audio.mp3")
    reencode_audio(original_audio_path, reencoded_original_audio_path)

    # Merge videos until duration exceeds the original audio
    merged_video_path = os.path.join(output_folder, "merged_video.mp4")
    target_resolution = (1920, 1080)
    merge_videos(video_files, merged_video_path, original_audio_duration, target_resolution)

    # Merge the merged audio with the video (with volume reduction)
    final_video_path = os.path.join(output_folder, "new_video.mp4")
    ffmpeg_command = [
        'ffmpeg',
        '-i', merged_video_path,
        '-i', reencoded_original_audio_path,  # Use reencoded audio
        '-filter_complex', '[1:a]volume=0.5[audio2]; [0:a][audio2]amix=inputs=2[outa]',  # Use amix instead of amerge
        '-map', '0:v', '-map', '[outa]',
        '-c:v', 'copy', '-c:a', 'aac',
        final_video_path
    ]
    print(f"Running FFmpeg command: {' '.join(ffmpeg_command)}")
    subprocess.run(ffmpeg_command, check=True)

    # Copy the original audio file to the output folder
    shutil.copyfile(original_audio_path, os.path.join(output_folder, "original_audio.mp3"))

if __name__ == "__main__":
    main()
