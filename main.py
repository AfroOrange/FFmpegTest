import subprocess
import threading
import time
import os
import shutil

# File paths
SOURCE_IMAGE = "images/angry.png"  # The image you edit
FFMPEG_IMAGE = "images/overlay_ffmpeg.png"  # FFmpeg reads this
RTSP_INPUT = "rtsp://localhost:8554/camera1"  # RTSP input stream
OUTPUT_STREAM = "rtsp://localhost:8554/overlay_stream"  # RTSP output

def start_ffmpeg():
    """Starts FFmpeg and uses overlay_ffmpeg.png."""
    # Ensure FFmpeg overlay file exists before starting
    if not os.path.exists(FFMPEG_IMAGE):
        print("Creating initial overlay_ffmpeg.png...")
        shutil.copy(SOURCE_IMAGE, FFMPEG_IMAGE)  # Ensure FFmpeg has an image to read

    # FFmpeg command to overlay image
    command = [
        "ffmpeg", "-i", RTSP_INPUT, "-loop", "1", "-i", FFMPEG_IMAGE,
        "-filter_complex", "[0:v][1:v] overlay=10:10",
        "-vcodec", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
        "-f", "rtsp", OUTPUT_STREAM
    ]

    print("Starting FFmpeg with overlay...")
    process = subprocess.Popen(command)
    process.wait()  # Keep process running

def watch_overlay():
    """Detects changes in angry.png and updates overlay_ffmpeg.png safely."""
    
    if not os.path.exists(SOURCE_IMAGE):
        print(f"Error: {SOURCE_IMAGE} does not exist. Please create it.")
        return

    last_modified = os.path.getmtime(SOURCE_IMAGE)

    while True:
        time.sleep(1)  # Check every second

        try:
            current_modified = os.path.getmtime(SOURCE_IMAGE)
        except FileNotFoundError:
            continue  # Ignore if the file is temporarily missing

        if current_modified != last_modified:
            print("Overlay updated! Refreshing...")

            try:
                shutil.copy(SOURCE_IMAGE, FFMPEG_IMAGE)
                last_modified = current_modified  # Update last modified time
            except PermissionError:
                print("Warning: Unable to update overlay (file in use). Retrying...")

# Run both functions in separate threads
if __name__ == "__main__":
    ffmpeg_thread = threading.Thread(target=start_ffmpeg, daemon=True)
    overlay_thread = threading.Thread(target=watch_overlay, daemon=True)

    ffmpeg_thread.start()
    overlay_thread.start()

    # Keep main script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping everything...")