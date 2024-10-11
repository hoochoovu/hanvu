import os
import subprocess

def get_video_info(fg_path):
    """
    Gets video width, height, and duration using ffprobe.

    Args:
        fg_path: Path to the video file.

    Returns:
        fg_width: Width of the video.
        fg_height: Height of the video.
        fg_duration: Duration of the video.
    """
    # Get video dimensions and duration
    fg_info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                              "-show_entries", "stream=width,height,duration", 
                              "-of", "default=noprint_wrappers=1:nokey=1", fg_path],
                             capture_output=True, text=True).stdout.strip().split('\n')
    
    fg_width = int(fg_info[0])
    fg_height = int(fg_info[1])
    fg_duration = float(fg_info[2])

    return fg_width, fg_height, fg_duration

def merge_videos(fg_path, output_video_path, zoom=1.0):
    """
    Overlays the foreground video onto a 1920x1080 black background, applying cropping, zoom, and centering.

    Args:
        fg_path: Path to the foreground video.
        output_video_path: Path to save the merged video output.
        zoom: Zoom factor for foreground video (default: 1.0).
    """
    # Get foreground video dimensions and duration
    fg_width, fg_height, fg_duration = get_video_info(fg_path)

    # Target resolution (1920x1080)
    target_width, target_height = 1920, 1080

    # Scale the foreground video
    scaled_fg_width = int(fg_width * zoom)
    scaled_fg_height = int(fg_height * zoom)

    # Calculate cropping to maintain aspect ratio and center the video
    if scaled_fg_width > target_width:
        crop_width = target_width
        crop_height = int(target_width * scaled_fg_height / scaled_fg_width)
    else:
        crop_height = target_height
        crop_width = int(target_height * scaled_fg_width / scaled_fg_height)

    # Center the crop on the target resolution
    crop_x = (scaled_fg_width - crop_width) // 2
    crop_y = (scaled_fg_height - crop_height) // 2

    # Center the video on the target background
    x_offset = (target_width - crop_width) // 2
    y_offset = (target_height - crop_height) // 2

    # Build ffmpeg command for video merging
    command = [
        "ffmpeg", "-f", "lavfi", "-i", f"color=black:s={target_width}x{target_height}:d={fg_duration}", 
        "-i", fg_path,
        "-filter_complex",
        f"[1:v]scale={scaled_fg_width}:{scaled_fg_height},crop={crop_width}:{crop_height}:{crop_x}:{crop_y}[fg];"
        f"[0:v][fg]overlay=x={x_offset}:y={y_offset}:shortest=1[video]",
        "-map", "[video]", "-c:v", "libx264", "-preset", "veryfast", "-y", output_video_path
    ]
    subprocess.run(command)

def merge_audio(fg_path, output_audio_path):
    """
    Copies the audio stream from the foreground video.

    Args:
        fg_path: Path to the foreground video.
        output_audio_path: Path to save the extracted audio output.
    """
    # Build ffmpeg command for audio extraction
    command = [
        "ffmpeg", "-i", fg_path,
        "-vn", "-c:a", "aac", "-b:a", "192k", "-y", output_audio_path
    ]
    subprocess.run(command)

def process_videos(fg_folder, output_folder, zoom=1.0):
    """
    Processes videos by overlaying the foreground video onto a 1920x1080 black background and merging the audio.

    Args:
        fg_folder: Path to the folder containing foreground videos.
        output_folder: Path to the folder where output videos will be saved.
        zoom: Zoom factor for foreground video (default: 1.0).
    """
    for root, dirs, files in os.walk(fg_folder):
        for fg_file in files:
            if fg_file.endswith(".mp4"):
                fg_path = os.path.join(root, fg_file)
                rel_path = os.path.relpath(root, fg_folder)
                output_dir = os.path.join(output_folder, rel_path)
                os.makedirs(output_dir, exist_ok=True)
                
                output_video_path = os.path.join(output_dir, f"{os.path.splitext(fg_file)[0]}_video.mp4")
                output_audio_path = os.path.join(output_dir, f"{os.path.splitext(fg_file)[0]}_audio.m4a")
                final_output_path = os.path.join(output_dir, f"{os.path.splitext(fg_file)[0]}_output.mp4")

                # Merge videos
                merge_videos(fg_path, output_video_path, zoom)

                # Merge audio
                merge_audio(fg_path, output_audio_path)

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
    fg_folder = "fg"
    output_folder = "output"

    # Set zoom value
    zoom = 1.0  # Zoom factor (e.g., 1.2 for 20% zoom)

    # Process videos
    process_videos(fg_folder, output_folder, zoom)
