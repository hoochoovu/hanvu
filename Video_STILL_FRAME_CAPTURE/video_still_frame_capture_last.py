import os
import cv2

def process_video(video_path, output_folder, frame_interval=36, max_photos=4):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print(f"Error opening video file: {video_path}")
        return

    # Determine the total number of frames in the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the starting point for capturing the last 4 frames
    frames_to_capture = []
    for i in range(max_photos):
        frame_position = total_frames - (i + 1) * frame_interval
        if frame_position >= 0:
            frames_to_capture.append(frame_position)
    
    frames_to_capture = sorted(frames_to_capture)

    photo_count = 0
    for frame_position in frames_to_capture:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
        success, frame = cap.read()
        if success:
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            frame_filename = os.path.join(output_folder, f"{video_name}_frame_{frame_position}_[Last].jpg")
            cv2.imwrite(frame_filename, frame)
            photo_count += 1
        if photo_count >= max_photos:
            break

    # Release the VideoCapture object
    cap.release()

def process_folder(input_folder, output_folder, frame_interval=36, max_photos=4):
    for root, dirs, files in os.walk(input_folder):
        # Determine the relative path to maintain folder structure
        relative_path = os.path.relpath(root, input_folder)
        output_subfolder = os.path.join(output_folder, relative_path)
        os.makedirs(output_subfolder, exist_ok=True)

        for file in files:
            if file.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                video_path = os.path.join(root, file)
                process_video(video_path, output_subfolder, frame_interval, max_photos)

if __name__ == "__main__":
    input_folder = r"E:\Dataset\All Video BG\Non-Watermarked\Horizontal\1 Minute"
    output_folder = r"E:\Dataset\All Video BG\Non-Watermarked\Horizontal\1 Minute\VIDEO_STILLS"

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    process_folder(input_folder, output_folder)