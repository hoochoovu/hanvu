import os
import subprocess

def merge_videos(bg_path, fg_path, output_video_path, zoom=1.0, x_offset=0, y_offset=0):
    """
    Merges background and foreground videos using color keying, applying zoom and offsets.

    Args:
        bg_path: Path to the background video.
        fg_path: Path to the foreground video.
        output_video_path: Path to save the merged video output.
        zoom: Zoom factor for foreground video (default: 1.0).
        x_offset: Horizontal offset for foreground video (default: 0).
        y_offset: Vertical offset for foreground video (default: 0).
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
    scaled_fg_width = int(fg_width * zoom)
    scaled_fg_height = int(fg_height * zoom)
    x_center_offset = (bg_width - scaled_fg_width) // 2 + x_offset
    y_center_offset = (bg_height - scaled_fg_height) // 2 + y_offset

    # Build ffmpeg command for video merging
    command = [
        "ffmpeg", "-i", bg_path, "-i", fg_path,
        "-filter_complex",
        f"[1:v]colorkey=0x000000:0.1:0.1,scale={scaled_fg_width}:{scaled_fg_height}[fg];"
        f"[0:v][fg]overlay=x={x_center_offset}:y={y_center_offset}:shortest=1[video]",
        "-map", "[video]", "-c:v", "libx264", "-preset", "veryfast", "-y", output_video_path
    ]
    subprocess.run(command)

def merge_audio(bg_path, fg_path, output_audio_path):
    """
    Merges audio streams from the background and foreground videos.

    Args:
        bg_path: Path to the background video.
        fg_path: Path to the foreground video.
        output_audio_path: Path to save the merged audio output.
    """
    # Build ffmpeg command for audio merging
    command = [
        "ffmpeg", "-i", bg_path, "-i", fg_path,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=shortest[a]",
        "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-y", output_audio_path
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

            for fg_file in os.listdir(fg_folder):
                if fg_file.endswith(".mp4"):
                    fg_path = os.path.join(fg_folder, fg_file)
                    output_video_path = os.path.join(output_folder, f"{os.path.splitext(fg_file)[0]}_video.mp4")
                    output_audio_path = os.path.join(output_folder, f"{os.path.splitext(fg_file)[0]}_audio.m4a")
                    final_output_path = os.path.join(output_folder, f"{os.path.splitext(fg_file)[0]}_output.mp4")

                    # Merge videos
                    merge_videos(bg_path, fg_path, output_video_path, zoom, x_offset, y_offset)

                    # Merge audio
                    merge_audio(bg_path, fg_path, output_audio_path)

                    # Combine video and audio into the final output
                    command = [
                        "ffmpeg", "-i", output_video_path, "-i", output_audio_path,
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-y", final_output_path
                    ]
                    subprocess.run(command)

                    # Remove intermediate files
                    os.remove(output_video_path)
                    os.remove(output_audio_path)

if __name__ == "__main__":
    bg_folder = "bg"
    fg_folder = "fg"
    output_folder = "output"

    # Set zoom and offset values
    zoom = 1  # Zoom factor (e.g., 1.2 for 20% zoom)
    x_offset = 0  # Additional horizontal offset in pixels
    y_offset = 0  # Additional vertical offset in pixels

    # Process videos using separate video and audio merging functions
    process_videos(bg_folder, fg_folder, output_folder, zoom, x_offset, y_offset)
