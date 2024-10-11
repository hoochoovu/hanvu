import os
import subprocess
import random

def get_video_files(folder):
    """
    Recursively gets all video files from a folder and its subfolders.
    
    Args:
        folder: Path to the folder to search.
    
    Returns:
        List of full paths to video files.
    """
    video_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):  # Add more video extensions if needed
                video_files.append(os.path.join(root, file))
    return video_files

def append_videos_randomly(video_folder, target_duration):
    """
    Appends videos randomly from a folder until the target duration is met without duplicates.
    
    Args:
        video_folder: Path to the folder containing videos.
        target_duration: Target duration in seconds.
    
    Returns:
        List of paths to the selected videos.
    """
    video_files = get_video_files(video_folder)
    selected_videos = []
    current_duration = 0

    while current_duration < target_duration and video_files:
        video_path = random.choice(video_files)
        
        # Get video duration
        duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]).decode('utf-8').strip())
        
        if current_duration + duration <= target_duration:
            selected_videos.append(video_path)
            current_duration += duration
        
        video_files.remove(video_path)

    return selected_videos

def append_videos(video_list, output_path, chunk_size=20):
    """
    Appends multiple videos into a single video file, splitting into chunks if needed.
    
    Args:
        video_list: List of video file paths.
        output_path: Path to save the appended video.
        chunk_size: Maximum number of videos to concatenate at once (default: 20)
    """
    if len(video_list) <= chunk_size:
        # Concatenate directly if less than or equal to chunk size
        input_files = ''.join([f"-i {video} " for video in video_list])
        
        # Correctly build the filter graph
        filter_complex = ""
        for i in range(len(video_list)):
            filter_complex += f"[{i}:v][{i}:a]" 
        filter_complex += f"concat=n={len(video_list)}:v=1:a=1[outv][outa]"

        command = f"ffmpeg {input_files} -filter_complex '{filter_complex}' -map '[outv]' -map '[outa]' {output_path}"
        print("Running command:", command)  # Print the command
        subprocess.run(command, shell=True, check=True, capture_output=True)
    else:
        # Split into chunks and concatenate them recursively
        chunks = [video_list[i:i+chunk_size] for i in range(0, len(video_list), chunk_size)]
        temp_outputs = []
        for i, chunk in enumerate(chunks):
            temp_output = os.path.join(os.path.dirname(output_path), f"temp_{i}.mp4")
            append_videos(chunk, temp_output, chunk_size)
            temp_outputs.append(temp_output)
        # Concatenate the temporary outputs
        append_videos(temp_outputs, output_path, chunk_size)
        # Clean up temporary files
        for file in temp_outputs:
            if os.path.exists(file):
                os.remove(file)

def merge_audio(audio_list, output_path):
    """
    Merges multiple audio files into a single audio file.
    
    Args:
        audio_list: List of audio file paths.
        output_path: Path to save the merged audio.
    """
    input_files = ''.join([f"-i {audio} " for audio in audio_list])
    filter_complex = f"amix=inputs={len(audio_list)}:duration=longest"
    
    command = f"ffmpeg {input_files} -filter_complex '{filter_complex}' {output_path}"
    subprocess.run(command, shell=True, check=True)

def apply_color_keying(input_video, output_video):
    """
    Applies color keying to remove black pixels from the video.
    
    Args:
        input_video: Path to the input video.
        output_video: Path to save the color-keyed video.
    """
    command = [
        "ffmpeg",
        "-i", input_video,
        "-vf", "colorkey=0x000000:0.1:0.1",
        "-c:a", "copy",
        output_video
    ]
    subprocess.run(command, check=True)

def merge_videos_with_audio(bg_video, fg_video, audio, output_video):
    """
    Merges background and foreground videos with audio using H.264 encoding.
    
    Args:
        bg_video: Path to the background video.
        fg_video: Path to the foreground video.
        audio: Path to the audio file.
        output_video: Path to save the final merged video.
    """
    command = [
        "ffmpeg",
        "-i", bg_video,
        "-i", fg_video,
        "-i", audio,
        "-filter_complex", "[0:v][1:v]overlay=shortest=1[v]",
        "-map", "[v]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "128k",
        output_video
    ]
    subprocess.run(command, check=True)

def process_videos(bg_folder, fg_folder, output_folder, target_duration):
    """
    Processes videos according to the specified requirements.
    
    Args:
        bg_folder: Path to the folder containing background videos.
        fg_folder: Path to the folder containing foreground videos.
        output_folder: Path to the folder where output videos will be saved.
        target_duration: Target duration for the appended video in seconds.
    """
    os.makedirs(output_folder, exist_ok=True)

    print(f"Foreground videos: {get_video_files(fg_folder)}")
    print(f"Background videos: {get_video_files(bg_folder)}")

    # Append foreground videos randomly
    fg_videos = append_videos_randomly(fg_folder, target_duration)
    if not fg_videos:
        print("No suitable foreground videos found.")
        return

    # Append selected videos
    appended_video = os.path.join(output_folder, "appended_video.mp4")
    append_videos(fg_videos, appended_video)
    if not os.path.exists(appended_video):
        print(f"Failed to create appended video: {appended_video}")
        return

    # Extract and merge audio from appended videos
    audio_files = [os.path.join(output_folder, f"audio_{i}.aac") for i in range(len(fg_videos))]
    for video, audio in zip(fg_videos, audio_files):
        subprocess.run(f"ffmpeg -i {video} -vn -acodec copy {audio}", shell=True, check=True)
    
    merged_audio = os.path.join(output_folder, "merged_audio.aac")
    merge_audio(audio_files, merged_audio)
    if not os.path.exists(merged_audio):
        print(f"Failed to create merged audio: {merged_audio}")
        return

    # Apply color keying to remove black pixels
    keyed_video = os.path.join(output_folder, "keyed_video.mp4")
    apply_color_keying(appended_video, keyed_video)
    if not os.path.exists(keyed_video):
        print(f"Failed to create keyed video: {keyed_video}")
        return

    # Select a random background video
    bg_videos = get_video_files(bg_folder)
    if not bg_videos:
        print("No background videos found.")
        return
    bg_video = random.choice(bg_videos)

    # Merge background and keyed videos with audio
    final_output = os.path.join(output_folder, "final_output.mp4")
    merge_videos_with_audio(bg_video, keyed_video, merged_audio, final_output)
    
    # Clean up temporary files
    for file in [appended_video, keyed_video, merged_audio] + audio_files:
        if os.path.exists(file):
            os.remove(file)

    print(f"Final output saved to: {final_output}")

if __name__ == "__main__":
    bg_folder = "bg"
    fg_folder = "fg"
    output_folder = "output"
    target_duration = 300  # 5 minutes

    process_videos(bg_folder, fg_folder, output_folder, target_duration)