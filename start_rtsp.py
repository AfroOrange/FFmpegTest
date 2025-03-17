import subprocess

def start_rtsp_stream(input_video, rtsp_url="rtsp://localhost:8554/camera1"):
    command = [
        "ffmpeg", "-re", "-stream_loop", "-1", "-i", input_video,
        "-vcodec", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
        "-r", "30", "-g", "50", "-keyint_min", "50",
        "-f", "rtsp", rtsp_url
    ]
    subprocess.Popen(command)

if __name__ == "__main__":
    start_rtsp_stream("videos/example_looped.mp4")
    print(f"RTSP Stream started at rtsp://localhost:8554/camera1")