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
    original_audio_path = r"E:\Python_Practice\FFMPEG_VIDEO_MAKER\audiofiletomake\[Complete]-CLEANTHES-He-needs-little-who-desires.mp3"
    video_input_folder = r"E:\Dataset\PEXELS\All_Scrape\All_Videos"
    audio_input_folder = r"E:\Dataset\PEXELS\ALL_AUDIO_converted_finished"
    output_folder = "output"
    finished_videos_folder = os.path.join(output_folder, "Finished Videos")  # Create "Finished Videos" folder
    target_resolution = (1920, 1080)
    target_fps = 24

    # Settings for audio volumes (To increase volume by 6db, add 1 to the number)
    original_audio_volume = 1.50  # Default 1 = 100%
    merged_audio_volume = 0.25  # Default -0.50 = 50%

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create "Finished Videos" folder if it doesn't exist
    if not os.path.exists(finished_videos_folder):
        os.makedirs(finished_videos_folder)

    # Delete potential files from previous runs
    for file_name in ['merged_audio.mp3', 'merged_video.mp4', 'merged_audio.aac', 'mixed_audio.aac', 'original_audio.mp3', 'reencoded_merged_audio.mp3', 'reencoded_original_audio.mp3', 'final_audio.mp3', 'trimmed_audio.mp3', 'trimmed_video.mp4']:
        file_path = os.path.join(output_folder, file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    start_time = datetime.datetime.now()  # Start timer        

    # 1. Get original audio duration
    original_audio_duration = get_file_duration(original_audio_path)
    print(f"Original audio duration: {original_audio_duration}")

    # 2. Merge videos (mute and trim to original audio duration)
    video_files = []
    for root, _, files in os.walk(video_input_folder):
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
    for i, video_file in enumerate(merged_videos):
        if not video_file.lower().endswith(".mp4"):
            converted_video_path = os.path.splitext(video_file)[0] + ".mp4"
            convert_video_to_mp4(video_file, converted_video_path)
            merged_videos[i] = converted_video_path
    merged_video_path = os.path.join(output_folder, "merged_video.mp4")
    inputs = ['-i', merged_videos[0]]
    for i in range(1, len(merged_videos)):
        inputs.extend(['-i', merged_videos[i]])

    filter_complex_parts = []
    for i in range(len(merged_videos)):
        filter_complex_parts.append(f"[{i}:v]scale={target_resolution[0]}:{target_resolution[1]}[v{i}];")

    concat_filter = f"concat=n={len(merged_videos)}:v=1[outv]"
    filter_complex_parts.append("".join(f"[v{i}]" for i in range(len(merged_videos))))
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

    # 3. Merge audio (convert to AAC first, then to MP3 if needed, and trim)
    audio_files = []
    for root, _, files in os.walk(audio_input_folder):
        for file in files:
            if file.lower().endswith(('.mp3', '.wav', '.ogg')):
                audio_files.append(os.path.join(root, file))

    merged_audios = []
    total_audio_duration = 0
    while total_audio_duration < original_audio_duration:
        random_audio = random.choice(audio_files)

        # Convert to AAC if necessary
        if not validate_audio_stream(random_audio):
            converted_audio_path = os.path.join(output_folder, f"converted_audio_{len(merged_audios)}.mp3")
            convert_audio_sample_rate(random_audio, converted_audio_path)
            merged_audios.append(converted_audio_path)
        else:
            merged_audios.append(random_audio)
        total_audio_duration += get_file_duration(random_audio)

    # Merge audio using AAC codec
    merged_audio_path = os.path.join(output_folder, "merged_audio.aac")  # Save as AAC first
    inputs = ['-i', merged_audios[0]]
    for i in range(1, len(merged_audios)):
        inputs.extend(['-i', merged_audios[i]])

    filter_complex = "".join(f"[{i}:a]" for i in range(len(merged_audios))) + f"concat=n={len(merged_audios)}:v=0:a=1[outa]"

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

    # 4. Re-encode original audio (to the correct sample rate)
    reencoded_original_audio_path = os.path.join(output_folder, "reencoded_original_audio.mp3")
    convert_audio_sample_rate(original_audio_path, reencoded_original_audio_path)

    # 5. Mix re-encoded merged audio (AAC) with re-encoded original audio (MP3) 
    # (Convert merged audio to MP3 after mixing to prevent issues)
    mixed_audio_path = os.path.join(output_folder, "mixed_audio.aac") 
    ffmpeg_command = [
        'ffmpeg',
        '-i', merged_audio_path,  # Use AAC-encoded merged audio
        '-i', reencoded_original_audio_path,
        '-filter_complex', 
        f'[0:a]volume={merged_audio_volume}[audio1];'  # Adjust merged audio volume
        f'[1:a]volume={original_audio_volume}[audio2];'  # Adjust original audio volume
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
    final_audio_path = os.path.join(output_folder, "final_audio.mp3")
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

    # 6. Merge final video and audio
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    final_video_path = os.path.join(finished_videos_folder, f"new_video_{timestamp}.mp4")  # Use timestamp and "Finished Videos" folder
    ffmpeg_command = [
        'ffmpeg',
        '-i', merged_video_path,
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
    shutil.copyfile(original_audio_path, os.path.join(output_folder, "original_audio.mp3"))

    end_time = datetime.datetime.now()  # End timer
    total_time = end_time - start_time
    print(f"Total runtime: {total_time}")
    print(f"Original audio duration: {original_audio_duration}")    

if __name__ == "__main__":
    main()