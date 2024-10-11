import os
import random
import subprocess

def get_video_info(video_path):
    """Retrieve video width and height using ffprobe."""
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                           "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", video_path],
                          capture_output=True, text=True).stdout.strip().split('x')
    return int(info[0]), int(info[1])

def merge_videos(bg_path, fg_path, output_video_path, zoom=1.0, x_offset=0, y_offset=0):
    """Merges background and foreground videos using color keying, applying zoom and offsets."""
    bg_width, bg_height = get_video_info(bg_path)
    fg_width, fg_height = get_video_info(fg_path)
    
    # Adjust offsets for centering the foreground video
    scaled_fg_width = int(fg_width * zoom)
    scaled_fg_height = int(fg_height * zoom)
    x_center_offset = (bg_width - scaled_fg_width) // 2 + x_offset
    y_center_offset = (bg_height - scaled_fg_height) // 2 + y_offset

    # Build ffmpeg command for video merging
    command = [
        "ffmpeg", "-hwaccel", "cuda", "-i", bg_path, "-i", fg_path,
        "-filter_complex",
        f"[1:v]colorkey=0x000000:0.1:0.1,scale={scaled_fg_width}:{scaled_fg_height}[fg];"
        f"[0:v][fg]overlay=x={x_center_offset}:y={y_center_offset}:shortest=1[video]",
        "-map", "[video]", "-c:v", "h264_nvenc", "-preset", "fast", "-y", output_video_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

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

def select_random_video(folder):
    videos = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".mp4"):
                videos.append(os.path.join(root, file))
    return random.choice(videos) if videos else None

def create_final_video_sequence(bg_folder, fg_folder, title_folder, stoistica_folder, output_folder, resolution, duration, iterations):
    if duration <= 59:
        duration_folder = os.path.join(bg_folder, "1 Minute")
    elif 60 <= duration <= 119:
        duration_folder = os.path.join(bg_folder, "2 Minute")
    elif 120 <= duration <= 599:
        duration_folder = os.path.join(bg_folder, "10 Minute")
    elif duration == 30 * 60:
        duration_folder = os.path.join(bg_folder, "30 Minute")
    elif duration == 60 * 60:
        duration_folder = os.path.join(bg_folder, "60 Minute")
    else:
        raise ValueError("Unsupported duration value")

    os.makedirs(output_folder, exist_ok=True)

    for i in range(iterations):
        # Initial title video
        title_video_path = select_random_video(title_folder)
        
        if not title_video_path:
            raise FileNotFoundError("Title video not found in the specified folder.")

        # Prepare the sequence
        video_sequence = [title_video_path]

        # Calculate the number of video clips needed
        num_clips = (duration - 2) // 2  # Adjusting duration for the title video (assuming it is 2 seconds long)

        # Add foreground and stoistica videos
        for _ in range(num_clips):
            fg_video_path = select_random_video(fg_folder)
            if fg_video_path:
                video_sequence.append(fg_video_path)
            else:
                raise FileNotFoundError("Foreground video not found in the specified folder.")

            video_sequence.append(select_random_video(stoistica_folder))

        # Merge the videos into one
        final_fg_video_path = os.path.join(output_folder, f"final_foreground_{i}.mp4")
        final_bg_video_path = select_random_video(duration_folder)
        
        if not final_bg_video_path:
            raise FileNotFoundError(f"Background video not found in the folder {duration_folder}.")

        with open("concat_list.txt", "w") as f:
            for video_path in video_sequence:
                f.write(f"file '{video_path}'\n")

        command = [
            "ffmpeg", "-f", "concat", "-safe", "0", "-i", "concat_list.txt",
            "-c:v", "h264_nvenc", "-preset", "fast", "-t", str(duration), "-y", final_fg_video_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)
        
        # Merge final foreground video with the selected background video
        output_video_path = os.path.join(output_folder, f"final_video_{duration // 60}min_{resolution}_{i}.mp4")
        output_audio_path = os.path.join(output_folder, f"final_audio_{duration // 60}min_{resolution}_{i}.m4a")

        merge_videos(final_bg_video_path, final_fg_video_path, output_video_path)
        merge_audio(final_bg_video_path, final_fg_video_path, output_audio_path)

        # Combine video and audio into the final output
        final_output_path = os.path.join(output_folder, f"final_output_{duration // 60}min_{resolution}_{i}.mp4")
        command = [
            "ffmpeg", "-i", output_video_path, "-i", output_audio_path,
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-y", final_output_path
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print(result.stdout)
        print(result.stderr)

        # Cleanup intermediate files
        if os.path.exists(output_video_path):
            os.remove(output_video_path)
        if os.path.exists(output_audio_path):
            os.remove(output_audio_path)
        os.remove("concat_list.txt")

        print(f"Final video created: {final_output_path}")

if __name__ == "__main__":
    bg_folder = r"E:\Dataset\All Video BG\Watermarked\Horizontal"
    fg_folder = r"E:\Dataset\All Audio Quotes\Video Clips (Full Letters)\2s Added"
    title_folder = r"E:\Dataset\All 200+ Stoic Quotes\Video Clips\2s Added" # Horizontal
    stoistica_folder = r"E:\Dataset\All STOISTICA Audio\Video Clips\2s Added" # Horizontal
    output_folder = "output"

    # Example usage
    resolution = "Horizontal"  # Options: "Vertical", "Horizontal", "Square"
    duration = 10 * 59  # Options: duration in seconds (e.g., 59, 119, 599, 30 * 60, 60 * 60)
    iterations = 1  # Number of iterations to generate

    create_final_video_sequence(bg_folder, fg_folder, title_folder, stoistica_folder, output_folder, resolution, duration, iterations)
