import argparse
from image_to_video_ffmpeg import VideoPlayer

def main():
    parser = argparse.ArgumentParser(description="Loop video player with image overlay")
    parser.add_argument("--vpath", type=str, help="Path to the video file")
    args = parser.parse_args()

    player = VideoPlayer(args.vpath)

if __name__ == "__main__":
    main()