import os
import random
import subprocess
from datetime import datetime

QUALITY_SETTINGS = {
    "Default": "2000k",
    "High": "4000k",
    "Higher": "6000k",
    "Intense": "8000k",
    "Extreme": "10000k"
}

def get_video_info(video_path):
    """Retrieve video width and height using ffprobe."""
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                           "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", video_path],
                          capture_output=True, text=True).stdout.strip().split('x')
    return int(info[0]), int(info[1])

def get_video_duration(video_path):
    """Retrieve video duration using ffprobe."""
    duration = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                               "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                              capture_output=True, text=True).stdout.strip()
    return float(duration)

def merge_videos(bg_paths, fg_path, output_video_path, zoom=1.0, x_offset=0, y_offset=0, quality="Default"):
    """Merges background and foreground videos using color keying, applying zoom and offsets."""
    fg_width, fg_height = get_video_info(fg_path)
    bg_width, bg_height = get_video_info(bg_paths[0])  # Assume all background videos have the same resolution
    
    # Adjust offsets for centering the foreground video
    scaled_fg_width = int(fg_width * zoom)
    scaled_fg_height = int(fg_height * zoom)
    x_center_offset = (bg_width - scaled_fg_width) // 2 + x_offset
    y_center_offset = (bg_height - scaled_fg_height) // 2 + y_offset

    bitrate = QUALITY_SETTINGS.get(quality, "2000k")  # Default to "2000k" if quality not found

    # Concatenate background videos if multiple
    if len(bg_paths) > 1:
        with open("bg_concat_list.txt", "w") as f:
            for bg_path in bg_paths:
                f.write(f"file '{bg_path}'\n")
        
        bg_concat_path = "concatenated_bg.mp4"
        command = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", "bg_concat_list.txt",
            "-c:v", "copy", "-y", bg_concat_path
        ]
        subprocess.run(command, check=True)
    else:
        bg_concat_path = bg_paths[0]

    # Build ffmpeg command for video merging
    command = [
        "ffmpeg", "-hwaccel", "cuda", "-i", bg_concat_path, "-i", fg_path,
        "-filter_complex",
        f"[1:v]colorkey=0x000000:0.1:0.1,scale={scaled_fg_width}:{scaled_fg_height}[fg];"
        f"[0:v][fg]overlay=x={x_center_offset}:y={y_center_offset}[video]",
        "-map", "[video]", "-c:v", "av1_nvenc", "-preset", "fast", "-b:v", bitrate, "-y", output_video_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

    # Cleanup
    if len(bg_paths) > 1:
        os.remove(bg_concat_path)
        os.remove("bg_concat_list.txt")

def merge_audio(bg_path, fg_path, output_audio_path):
    command = [
        "ffmpeg", "-i", bg_path, "-i", fg_path,
        "-filter_complex", "[0:a]volume=0.5[bg];[1:a]volume=0.5[fg];[bg][fg]amix=inputs=2:duration=longest[out]",
        "-map", "[out]", "-c:a", "aac", "-b:a", "192k", "-y", output_audio_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

    if not os.path.exists(output_audio_path):
        raise FileNotFoundError(f"Audio file not created: {output_audio_path}")

def select_random_video(folder, used_videos):
    videos = [os.path.join(root, file)
              for root, _, files in os.walk(folder)
              for file in files if file.endswith(".mp4") and os.path.join(root, file) not in used_videos]
    if not videos:
        raise FileNotFoundError(f"No unused videos found in {folder}.")
    selected_video = random.choice(videos)
    used_videos.add(selected_video)
    return selected_video

def select_random_audio(folder, used_audios):
    """Selects a random audio file from a folder."""
    audios = [os.path.join(folder, f) for f in os.listdir(folder)
              if (f.endswith(".mp3") or f.endswith(".wav")) and os.path.join(folder, f) not in used_audios]
    if not audios:
        raise FileNotFoundError(f"No unused audio files found in {folder}.")
    selected_audio = random.choice(audios)
    used_audios.add(selected_audio)
    return selected_audio

def merge_audio_to_video(video_path, bg_music, bg_music_volume=0, used_audios=set()):
    """Merges background music into a video and returns the output path."""
    video_duration = get_video_duration(video_path)

    if os.path.isdir(bg_music):
        bg_music_path = select_random_audio(bg_music, used_audios)
    else:
        bg_music_path = bg_music

    # Create background music looped to video duration
    looped_audio_path = "looped_audio.wav"
    subprocess.run(["ffmpeg", "-stream_loop", "-1", "-i", bg_music_path, "-t", str(video_duration), "-y", looped_audio_path], check=True)

    # Merge the video with the looped background music
    output_video_path = f"{os.path.splitext(video_path)[0]}_with_audio.mp4"
    command = [
        "ffmpeg", "-hwaccel", "cuda", "-i", video_path, "-i", looped_audio_path,
        "-filter_complex", f"[1:a]volume={bg_music_volume}dB[aud];[0:a][aud]amix=inputs=2:duration=first[a]",
        "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-y", output_video_path
    ]
    subprocess.run(command, check=True)
    
    # Cleanup intermediate files
    os.remove(looped_audio_path)
    return output_video_path

def create_final_video_sequence(bg_folder, fg_folder, title_folder, stoistica_folder, output_folder, resolution, duration, iterations, quality, bg_music, bg_music_volume):
    duration_folders = {
        59: "1 Minute",
        119: "2 Minute",
        599: "2 Minute",
        30 * 60: "2 Minute",  # Use 10-minute folder for long-form content
        60 * 60: "2 Minute"   # Use 10-minute folder for long-form content
    }

    if duration not in duration_folders:
        raise ValueError("Unsupported duration value")

    os.makedirs(output_folder, exist_ok=True)
    duration_folder = os.path.join(bg_folder, duration_folders[duration])

    used_videos = set()
    used_audios = set()

    for i in range(iterations):
        # Initial title video
        title_video_path = select_random_video(title_folder, used_videos)
        
        video_sequence = [title_video_path]
        total_duration = get_video_duration(title_video_path)
        
        while total_duration < duration:
            fg_video_path = select_random_video(fg_folder, used_videos)
            video_sequence.append(fg_video_path)
            total_duration += get_video_duration(fg_video_path)

            if total_duration < duration and (len(video_sequence) - 1) % 3 == 0:
                stoistica_video_path = select_random_video(stoistica_folder, used_videos)
                video_sequence.append(stoistica_video_path)
                total_duration += get_video_duration(stoistica_video_path)

        # Merge the videos into one
        final_fg_video_path = os.path.join(output_folder, f"final_foreground_{i}.mp4")

        with open("concat_list.txt", "w") as f:
            for video_path in video_sequence:
                f.write(f"file '{video_path}'\n")

        command = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", "concat_list.txt",
            "-c:v", "av1_nvenc", "-preset", "fast", "-y", final_fg_video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

        # Prepare background videos
        final_bg_video_paths = []
        bg_duration = 0
        while bg_duration < total_duration:
            bg_video_path = select_random_video(duration_folder, used_videos)
            final_bg_video_paths.append(bg_video_path)
            bg_duration += get_video_duration(bg_video_path)

        # Merge final foreground video with the selected background video
        output_video_path = os.path.join(output_folder, f"final_video_{duration // 60}min_{resolution}_{i}.mp4")
        output_audio_path = os.path.join(output_folder, f"final_audio_{duration // 60}min_{resolution}_{i}.m4a")

        merge_videos(final_bg_video_paths, final_fg_video_path, output_video_path, quality=quality)
        merge_audio(final_bg_video_paths[0], final_fg_video_path, output_audio_path)

        # Combine video and audio into the final output
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_output_path = os.path.join(output_folder, f"final_output_{duration // 60}min_{resolution}_{i}_{timestamp}_av1.mp4")
        command = [
            "ffmpeg", "-i", output_video_path, "-i", output_audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-y", final_output_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

        # Merge background music
        final_output_with_music_path = merge_audio_to_video(final_output_path, bg_music, bg_music_volume, used_audios)

        # Cleanup intermediate files
        if os.path.exists(output_video_path):
            os.remove(output_video_path)
        if os.path.exists(output_audio_path):
            os.remove(output_audio_path)
        if os.path.exists(final_fg_video_path):
            os.remove(final_fg_video_path)
        os.remove("concat_list.txt")

        print(f"Final video created: {final_output_with_music_path}")

if __name__ == "__main__":
    bg_folder = r"E:\Dataset\All Video BG\Watermarked\Horizontal"
    fg_folder = r"E:\Dataset\All Audio Quotes\Video Clips (Full Letters)\Golden 2s Added"
    title_folder = r"E:\Dataset\All 200+ Stoic Quotes\Video Clips\2s Added" # Horizontal
    stoistica_folder = r"E:\Dataset\All STOISTICA Audio\Video Clips\2s Added" # Horizontal
    output_folder = "output"
    bg_music = r"E:\Dataset\ALL BG Music\[-6db] LOWERED - I Am a Man Who Will Fight for Your Honor.mp3"  # Can be a folder or a file path

    # Example usage
    resolution = "Horizontal"  # Options: "Vertical", "Horizontal", "Square"
    duration = 60 * 60  # Options: duration in seconds (e.g., 59, 119, 599, 30 * 60, 60 * 60)
    iterations = 1  # Number of iterations to generate
    quality = "Higher"  # Options: "Default", "High", "Higher", "Intense", "Extreme"
    bg_music_volume = 0  # Volume adjustment in decibels, 0 is default, negative values reduce volume

    create_final_video_sequence(bg_folder, fg_folder, title_folder, stoistica_folder, output_folder, resolution, duration, iterations, quality, bg_music, bg_music_volume)
