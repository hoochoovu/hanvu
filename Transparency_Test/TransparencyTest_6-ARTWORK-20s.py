import os
import subprocess

def get_video_info(video_path):
    """
    Gets video width, height, and duration using ffprobe.
    """
    try:
        video_info = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip().split('\n')

        if len(video_info) < 3:
            print(f"Warning: Incomplete video info for {video_path}")
            return None, None, None

        video_width = int(video_info[0]) if video_info[0] else None
        video_height = int(video_info[1]) if video_info[1] else None
        video_duration = float(video_info[2]) if video_info[2] else None

        if video_width is None or video_height is None or video_duration is None:
            print(f"Warning: Invalid video info for {video_path}")
            return None, None, None

        return video_width, video_height, video_duration

    except subprocess.CalledProcessError as e:
        print(f"Error getting video info for {video_path}: {e}")
        return None, None, None
    except ValueError as e:
        print(f"Error parsing video info for {video_path}: {e}")
        return None, None, None

def overlay_fg_on_bg(fg_path, bg_path, output_video_path, zoom=1.0, codec="h264", crf=23, bitrate="4M", speed="fast", fg_brightness=None, bg_brightness=None, fg_gamma=None, bg_gamma=None):
    """
    Overlays the foreground video onto the background video. The output video ends when the background video ends.
    """
    fg_width, fg_height, fg_duration = get_video_info(fg_path)
    bg_width, bg_height, bg_duration = get_video_info(bg_path)

    if fg_width is None or fg_height is None or bg_width is None or bg_height is None:
        print(f"Error: Unable to get video info for {fg_path} or {bg_path}")
        return

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
        fg_filters = fg_filters.rstrip(':')

    # Optional brightness and gamma filters for background
    bg_filters = ""
    if bg_brightness is not None or bg_gamma is not None:
        bg_filters += "eq="
        if bg_brightness is not None:
            bg_filters += f"brightness={bg_brightness}:"
        if bg_gamma is not None:
            bg_filters += f"gamma={bg_gamma}:"
        bg_filters = bg_filters.rstrip(':')

    # Construct filter complex for FFmpeg
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
        "-i", bg_path,  # Background video
        "-i", fg_path,  # Foreground video
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

def process_videos(fg_folder, bg_folder, output_folder, zoom=1.0, codec="h264", crf=23, bitrate="4M", speed="fast", fg_brightness=None, bg_brightness=None, fg_gamma=None, bg_gamma=None):
    """
    Processes foreground videos and overlays them on background videos, replicating the background folder structure.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Check if foreground video exists
    fg_path = os.path.join(fg_folder, "[All Smoke] Vertical - Double Opacity.mp4")
    if not os.path.isfile(fg_path):
        print(f"Error: Foreground video not found at {fg_path}")
        return

    # Iterate over the background videos and copy their folder structure to output
    for root, dirs, files in os.walk(bg_folder):
        for bg_file in files:
            if bg_file.endswith(".mp4"):
                # Replicate the folder structure
                rel_path = os.path.relpath(root, bg_folder)
                output_dir = os.path.join(output_folder, rel_path)
                os.makedirs(output_dir, exist_ok=True)

                bg_path = os.path.join(root, bg_file)
                output_video_filename = f"[smoke]{bg_file}"
                output_video_path = os.path.join(output_dir, output_video_filename)

                print(f"Processing FG with BG: {bg_file} -> {output_video_filename}")

                try:
                    # Overlay foreground video on background
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
                    print(f"Error processing {bg_file}: {e}")
                except Exception as e:
                    print(f"Unexpected error: {e}")

if __name__ == "__main__":
    fg_folder = "fg"
    bg_folder = r"E:\Dataset\All Video BG\Watermarked\Vertical\Smoke\All Artwork"
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
