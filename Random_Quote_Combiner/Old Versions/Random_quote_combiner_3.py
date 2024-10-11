import os
import subprocess
import random

def append_videos(videos, target_duration, output_path):
    """
    Appends videos randomly until the target duration is met, avoiding duplicates.

    Args:
        videos: A list of video file paths.
        target_duration: The desired duration for the appended video in seconds.
        output_path: Path to save the appended video.
    """
    temp_appended_video = "temp_appended.mp4"
    appended_videos = []
    total_duration = 0

    while total_duration < target_duration:
        available_videos = [v for v in videos if v not in appended_videos]
        if not available_videos:
            break  # No more videos to append

        video_to_append = random.choice(available_videos)
        appended_videos.append(video_to_append)

        # Get video duration
        duration = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                         "-of", "default=noprint_wrappers=1:nokey=1", video_to_append],
                                        capture_output=True, text=True).stdout)

        total_duration += duration

        if total_duration <= target_duration:
            if os.path.exists(temp_appended_video):
                command = [
                    "ffmpeg", "-i", temp_appended_video, "-i", video_to_append,
                    "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
                    "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-y", temp_appended_video
                ]
            else:
                command = [
                    "ffmpeg", "-i", video_to_append, "-c:v", "libx264", "-preset", "veryfast", "-y", temp_appended_video
                ]
            subprocess.run(command)

    # Rename the temporary file to the final output
    os.rename(temp_appended_video, output_path)

def append_audio(videos, output_path):
    """
    Appends audio from a list of videos into a single audio file.

    Args:
        videos: A list of video file paths.
        output_path: Path to save the appended audio.
    """
    temp_appended_audio = "temp_appended_audio.m4a"
    for i, video in enumerate(videos):
        if i == 0:
            command = [
                "ffmpeg", "-i", video, "-map", "0:a", "-c:a", "aac", "-b:a", "192k", "-y", temp_appended_audio
            ]
        else:
            command = [
                "ffmpeg", "-i", temp_appended_audio, "-i", video,
                "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[a]",
                "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-y", temp_appended_audio
            ]
        subprocess.run(command)

    # Rename the temporary file to the final output
    os.rename(temp_appended_audio, output_path)

def apply_color_keying(video_path, output_path):
    """
    Applies color keying to remove black pixels from a video.

    Args:
        video_path: Path to the input video.
        output_path: Path to save the color-keyed video.
    """
    command = [
        "ffmpeg", "-i", video_path,
        "-filter_complex", "[0:v]colorkey=0x000000:0.1:0.1[out]",
        "-map", "[out]", "-c:v", "libx264", "-preset", "veryfast", "-y", output_path
    ]
    subprocess.run(command)

def merge_videos_with_audio(bg_path, fg_path, bg_audio_path, fg_audio_path, output_path):
    """
    Merges background and foreground videos with audio using AV1 encoding.

    Args:
        bg_path: Path to the background video.
        fg_path: Path to the foreground video.
        bg_audio_path: Path to the background audio.
        fg_audio_path: Path to the foreground audio.
        output_path: Path to save the merged video output.
    """
    # Get video dimensions
    bg_info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                              "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", bg_path],
                             capture_output=True, text=True).stdout.strip().split('x')
    fg_info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                              "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", fg_path],
                             capture_output=True, text=True).stdout.strip().split('x')
    bg_width, bg_height = int(bg_info[0]), int(bg_info[1])
    fg_width, fg_height = int(fg_info[0]), int(fg_info[1])

    # Adjust offsets for centering the foreground video
    # (Assuming zoom is 1.0 for simplicity)
    x_center_offset = (bg_width - fg_width) // 2
    y_center_offset = (bg_height - fg_height) // 2

    command = [
        "ffmpeg", "-i", bg_path, "-i", fg_path, "-i", bg_audio_path, "-i", fg_audio_path,
        "-filter_complex",
        f"[1:v]scale={fg_width}:{fg_height}[fg];"
        f"[0:v][fg]overlay=x={x_center_offset}:y={y_center_offset}:shortest=1[video];"
        f"[2:a][3:a]amix=inputs=2:duration=shortest[audio]",
        "-map", "[video]", "-map", "[audio]",
        "-c:v", "libaom-av1", "-crf", "30", "-b:v", "0", "-c:a", "aac", "-b:a", "192k", "-y", output_path
    ]
    subprocess.run(command)

def process_videos(bg_folder, fg_folder, output_folder, zoom=1.0, x_offset=0, y_offset=0):
    """
    Processes videos by merging the video and audio streams from background and foreground videos.

    Args:
        bg_folder: Path to the folder containing background videos.
        fg_folder: Path to the folder containing foreground videos.
        output_folder: Path to the folder where output videos will be saved.
        zoom: Zoom factor for foreground video (default: 1.0).
        x_offset: Horizontal offset for foreground video (default: 0).
        y_offset: Vertical offset for foreground video (default: 0).
    """
    for bg_file in os.listdir(bg_folder):
        if bg_file.endswith(".mp4"):
            bg_path = os.path.join(bg_folder, bg_file)
            bg_audio_path = bg_path.replace(".mp4", "_audio.m4a")

            fg_videos = [f for f in os.listdir(fg_folder) if f.endswith(".mp4")]
            appended_fg_video = os.path.join(output_folder, f"{os.path.splitext(bg_file)[0]}_fg_appended.mp4")
            appended_fg_audio = os.path.join(output_folder, f"{os.path.splitext(bg_file)[0]}_fg_audio.m4a")

            # Append foreground videos
            append_videos(
                [os.path.join(fg_folder, fg_video) for fg_video in fg_videos],
                target_duration=60,  # Example target duration
                output_path=appended_fg_video
            )

            # Append foreground audio
            append_audio(
                [os.path.join(fg_folder, fg_video) for fg_video in fg_videos],
                output_path=appended_fg_audio
            )

            output_video_path = os.path.join(output_folder, f"{os.path.splitext(bg_file)[0]}_output.mp4")

            # Apply color keying to the appended foreground video
            color_keyed_fg_video = os.path.join(output_folder, f"{os.path.splitext(bg_file)[0]}_fg_color_keyed.mp4")
            apply_color_keying(appended_fg_video, color_keyed_fg_video)

            # Merge background and foreground videos with audio
            merge_videos_with_audio(
                bg_path, color_keyed_fg_video, bg_audio_path, appended_fg_audio, output_video_path
            )

            # Remove intermediate files
            os.remove(appended_fg_video)
            os.remove(appended_fg_audio)
            os.remove(color_keyed_fg_video)

if __name__ == "__main__":
    bg_folder = "bg"
    fg_folder = "fg"
    output_folder = "output"

    # Set zoom and offset values
    zoom = 0.50  # Zoom factor (e.g., 1.2 for 20% zoom)
    x_offset = 0  # Additional horizontal offset in pixels
    y_offset = 300  # Additional vertical offset in pixels

    # Process videos
    process_videos(bg_folder, fg_folder, output_folder, zoom, x_offset, y_offset)