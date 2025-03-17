from flask import Flask, Response, request
import ffmpeg
import os
import time
import threading

# OPEN VLC AND GO TO: Media -> Open Network Stream -> http://localhost:5000/video

app = Flask(__name__)

video_path = "videos/example.mp4"

def generate_video(overlay_path=None):
    while True:  # Keep the stream running indefinitely
        input_stream = ffmpeg.input(video_path, stream_loop=-1)  # Loop video

        if overlay_path and os.path.exists(overlay_path):  # Check if overlay exists
            overlay_stream = ffmpeg.input(overlay_path)
            video_stream = ffmpeg.overlay(input_stream, overlay_stream)
        else:
            video_stream = input_stream

        output_stream = ffmpeg.output(video_stream, 'pipe:', format='mpegts', vcodec='libx264')
        process = ffmpeg.run_async(output_stream, pipe_stdout=True, pipe_stderr=True)

        try:
            while True:
                frame = process.stdout.read(8192)  # Read stream chunks
                if not frame:
                    break  # Restart FFMpeg if EOF reached
                yield frame
        finally:
            process.stdout.close()
            process.wait()
            time.sleep(1)  # Prevent excessive CPU usage

@app.route('/video')
def video_feed():
    overlay_path = request.args.get('overlay')  # Get overlay image path from query param
    print(f"Video feed requested. Overlay: {overlay_path}")
    return Response(generate_video(overlay_path), mimetype='video/mp2t')

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, threaded=True)