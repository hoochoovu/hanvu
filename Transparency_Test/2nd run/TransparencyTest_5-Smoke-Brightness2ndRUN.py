import os
import subprocess
import math

def get_video_info(video_path):
    """
    Gets video width, height, and duration using ffprobe.

    Args:
        video_path: Path to the video file.

    Returns:
        video_width: Width of the video.
        video_height: Height of the video.
        video_duration: Duration of the video.
    """
    video_info = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path,
        ],
        capture_output=True,
        text=True,
    ).stdout.strip().split('\n')

    video_width = int(video_info[0])
    video_height = int(video_info[1])
    video_duration = float(video_info[2])

    return video_width, video_height, video_duration

def loop_bg_video(bg_path, fg_duration):
    """
    Loops the background video until it matches or exceeds the duration of the foreground video.

    Args:
        bg_path: Path to the background video file.
        fg_duration: Duration of the foreground video.

    Returns:
        looped_bg: Path to the looped background video.
    """
    bg_width, bg_height, bg_duration = get_video_info(bg_path)
    loop_count = math.ceil(fg_duration / bg_duration)

    looped_bg = "looped_bg.mp4"

    # Use ffmpeg's concat demuxer to loop the background video
    with open("bg_loop_input.txt", "w") as f:
        for _ in range(loop_count):
            f.write(f"file '{os.path.abspath(bg_path)}'\n")

    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            "bg_loop_input.txt",
            "-c",
            "copy",
            "-y",
            looped_bg,
        ],
        check=True
    )

    # Trim the looped background to match the exact duration of the foreground video
    trimmed_bg = "trimmed_bg.mp4"
    subprocess.run(
        [
            "ffmpeg",
            "-i",
            looped_bg,
            "-t",
            str(fg_duration),
            "-c",
            "copy",
            "-y",
            trimmed_bg,
        ],
        check=True
    )

    # Clean up intermediate looped background
    os.remove(looped_bg)
    os.remove("bg_loop_input.txt")

    return trimmed_bg

def overlay_fg_on_bg(fg_path, bg_path, output_video_path, zoom=1.0, codec="h264", crf=23, bitrate="4M", speed="fast", fg_brightness=None, bg_brightness=None, fg_gamma=None, bg_gamma=None):
    """
    Overlays the foreground video onto a single background video, with optional brightness or gamma adjustments.
    
    Args:
        fg_path: Path to the foreground video.
        bg_path: Path to the background video.
        output_video_path: Path to save the final merged video.
        zoom: Zoom factor for the foreground video.
        codec: Video codec for encoding ('h264' or 'av1').
        crf: Constant Rate Factor for quality control (lower is better).
        bitrate: Bitrate for the video encoding (e.g., '4M').
        speed: Encoding speed preset (e.g., 'fast', 'medium', 'slow').
        fg_brightness: Adjust brightness of the foreground video.
        bg_brightness: Adjust brightness of the background video.
        fg_gamma: Adjust gamma of the foreground video.
        bg_gamma: Adjust gamma of the background video.
    """
    # Get foreground video dimensions and duration
    fg_width, fg_height, fg_duration = get_video_info(fg_path)

    # Loop the background video to match foreground duration
    looped_bg = loop_bg_video(bg_path, fg_duration)

    # Scale the foreground video and add transparency
    scaled_fg_width = int(fg_width * zoom)
    scaled_fg_height = int(fg_height * zoom)

    # Optional brightness and gamma filters for foreground
    fg_filters = f"scale={scaled_fg_width}:{scaled_fg_height},format=rgba,colorchannelmixer=aa=0.5"
    if fg_brightness is not None or fg_gamma is not None:
        fg_filters += f",eq="
        if fg_brightness is not None:
            fg_filters += f"brightness={fg_brightness}:"
        if fg_gamma is not None:
            fg_filters += f"gamma={fg_gamma}:"
        fg_filters = fg_filters.rstrip(':')  # Remove trailing colon

    # Optional brightness and gamma filters for background
    bg_filters = ""
    if bg_brightness is not None or bg_gamma is not None:
        bg_filters += "eq="
        if bg_brightness is not None:
            bg_filters += f"brightness={bg_brightness}:"
        if bg_gamma is not None:
            bg_filters += f"gamma={bg_gamma}:"
        bg_filters = bg_filters.rstrip(':')  # Remove trailing colon

    # Construct the filter complex for FFmpeg
    filter_complex = f"[1:v]{fg_filters}[fg];"
    if bg_filters:
        filter_complex += f"[0:v]{bg_filters}[bg];[bg][fg]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:shortest=1[video]"
    else:
        filter_complex += "[0:v][fg]overlay=(main_w-overlay_w)/2:(main_h-overlay_h)/2:shortest=1[video]"

    # Select codec and encoding settings
    if codec == "h264":
        encoder = "h264_nvenc"
        encoding_opts = ["-preset", speed, "-b:v", bitrate]
    elif codec == "av1":
        encoder = "av1_nvenc"
        encoding_opts = ["-crf", str(crf), "-b:v", bitrate]
    else:
        raise ValueError("Unsupported codec. Choose 'h264' or 'av1'.")

    # Run FFmpeg to overlay the foreground video on the background
    command = [
        "ffmpeg",
        "-i", looped_bg,
        "-i", fg_path,
        "-filter_complex", filter_complex,
        "-map", "[video]",
        "-map", "1:a?",
        "-c:v", encoder,
    ] + encoding_opts + [
        "-c:a", "aac",
        "-b:a", "192k",
        "-y", output_video_path,
    ]

    subprocess.run(command, check=True)

    # Clean up intermediate looped background
    os.remove(looped_bg)

def process_videos(fg_folder, bg_folder, output_folder, zoom=1.0, codec="h264", crf=23, bitrate="4M", speed="fast", fg_brightness=None, bg_brightness=None, fg_gamma=None, bg_gamma=None):
    """
    Processes foreground videos and overlays them on each background video, saving the final videos to the output folder.

    Args:
        fg_folder: Path to the folder containing foreground videos.
        bg_folder: Path to the folder containing background videos.
        output_folder: Path to the folder where output videos will be saved.
        zoom: Zoom factor for the foreground video.
        codec: Video codec for encoding ('h264' or 'av1').
        crf: Constant Rate Factor for AV1 encoding.
        bitrate: Bitrate for video encoding.
        speed: Speed preset for H264 encoding.
        fg_brightness: Adjust brightness of the foreground videos.
        bg_brightness: Adjust brightness of the background videos.
        fg_gamma: Adjust gamma of the foreground videos.
        bg_gamma: Adjust gamma of the background videos.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # List all background video files
    bg_files = sorted([f for f in os.listdir(bg_folder) if f.endswith('.mp4')])

    # Iterate over all foreground videos
    for root, dirs, files in os.walk(fg_folder):
        for fg_file in files:
            if fg_file.endswith(".mp4"):
                fg_path = os.path.join(root, fg_file)
                rel_path = os.path.relpath(root, fg_folder)
                output_dir = os.path.join(output_folder, rel_path)
                os.makedirs(output_dir, exist_ok=True)

                # Iterate over each background video
                for bg_file in bg_files:
                    bg_path = os.path.join(bg_folder, bg_file)
                    bg_name, bg_ext = os.path.splitext(bg_file)
                    output_video_filename = f"[smoke]{bg_name}{bg_ext}"
                    output_video_path = os.path.join(output_dir, output_video_filename)

                    print(f"Processing FG: {fg_file} with BG: {bg_file} -> {output_video_filename}")

                    # Overlay foreground video on background
                    try:
                        overlay_fg_on_bg(
                            fg_path,
                            bg_path,
                            output_video_path,
                            zoom,
                            codec,
                            crf,
                            bitrate,
                            speed,
                            fg_brightness,
                            bg_brightness,
                            fg_gamma,
                            bg_gamma
                        )
                        print(f"Successfully created {output_video_filename}")
                    except subprocess.CalledProcessError as e:
                        print(f"Error processing {fg_file} with {bg_file}: {e}")
                    except Exception as e:
                        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    fg_folder = "fg"
    bg_folder = r"E:\Dataset\All Samurai Photos\1 min v1\2nd"
    output_folder = "output"

    process_videos(
        fg_folder,
        bg_folder,
        output_folder,
        zoom=1.0, 
        codec="av1",
        crf=23,
        bitrate="4M",
        speed="fast",
        fg_brightness=0,
        bg_brightness=0.05,
        fg_gamma=1.0,
        bg_gamma=1.0
    )
