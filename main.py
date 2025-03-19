import ffmpeg
import subprocess
import threading
import time
import numpy as np
import cv2
import random
import sys

# Define video dimensions and framerate.
WIDTH, HEIGHT = 640, 360
FPS = 25

def start_source_stream():
    """
    Streams the source video (example.mp4) in a continuous loop to RTSP stream1.
    """
    rtsp_url = 'rtsp://localhost:8554/stream1'
    process = (
        ffmpeg
        .input('videos/example.mp4', re=None, stream_loop='-1')
        .output(rtsp_url,
                format='rtsp',
                rtsp_transport='tcp',
                vcodec='libx264',
                preset='veryfast',
                fflags='nobuffer')
        .run_async(pipe_stdout=True, pipe_stderr=True)
    )
    while True:
        if process.poll() is not None:
            print("[Source Stream] FFmpeg process exited")
            break
        line = process.stderr.readline()
        if line:
            print("[Source Stream LOG]", line.decode('utf-8', errors='replace'), end='')

def generate_dynamic_overlay_frame():
    """
    Generates a single RGBA frame (numpy array) of size WIDTH x HEIGHT
    with a transparent background and random red bounding boxes.
    """
    # Start with a fully transparent frame.
    frame = np.zeros((HEIGHT, WIDTH, 4), dtype=np.uint8)
    
    # Generate a random number (1 to 3) of bounding boxes.
    num_boxes = random.randint(1, 3)
    for _ in range(num_boxes):
        # Random top-left corner; ensure a minimum margin.
        x1 = random.randint(0, WIDTH - 50)
        y1 = random.randint(0, HEIGHT - 50)
        # Random width/height between 30 and 100 pixels.
        box_w = random.randint(30, 100)
        box_h = random.randint(30, 100)
        x2 = min(WIDTH - 1, x1 + box_w)
        y2 = min(HEIGHT - 1, y1 + box_h)
        # Draw a red rectangle with a thickness of 2.
        # OpenCV uses BGRA order; red is (0, 0, 255, 255).
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255, 255), thickness=2)
    return frame

def start_composite_stream():
    """
    Launches an ffmpeg composite process that takes:
      - Input 0: the source RTSP stream (stream1).
      - Input 1: raw RGBA frames (dynamic overlay) from a pipe.
    The overlay filter composites input1 on top of input0.
    The output is sent to RTSP stream2.
    """
    # This ffmpeg command expects two inputs:
    #   * The first input is the RTSP source.
    #   * The second input is rawvideo (RGBA) coming via stdin.
    ffmpeg_cmd = [
        'ffmpeg',
        '-i', 'rtsp://localhost:8554/stream1',
        '-f', 'rawvideo',
        '-pix_fmt', 'rgba',
        '-s', f'{WIDTH}x{HEIGHT}',
        '-r', str(FPS),
        '-i', 'pipe:0',
        '-filter_complex', '[0:v][1:v]overlay=format=auto',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-f', 'rtsp',
        'rtsp://localhost:8554/stream2'
    ]
    print("Starting composite process:")
    print(' '.join(ffmpeg_cmd))
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    try:
        while True:
            # Generate a dynamic overlay frame with random bounding boxes.
            frame = generate_dynamic_overlay_frame()
            # Write the raw RGBA bytes to ffmpeg's stdin.
            process.stdin.write(frame.tobytes())
            process.stdin.flush()
            time.sleep(1.0 / FPS)
    except Exception as e:
        print("Exception in composite stream:", e)
    finally:
        process.stdin.close()
        process.wait()

if __name__ == '__main__':
    # Start the source stream thread.
    source_thread = threading.Thread(target=start_source_stream, daemon=True)
    # Start the composite (final output) stream thread.
    composite_thread = threading.Thread(target=start_composite_stream, daemon=True)

    source_thread.start()
    # Allow a few seconds for the source stream to initialize.
    time.sleep(5)
    composite_thread.start()

    try:
        source_thread.join()
        composite_thread.join()
    except KeyboardInterrupt:
        print("Shutting down...")
        sys.exit(0)
