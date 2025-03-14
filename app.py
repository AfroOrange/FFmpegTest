import os
import ffmpeg

def trim(in_file, out_file, start, end):
    if os.path.exists(out_file):
        os.remove(out_file)
    
    in_file_probe_result = ffmpeg.probe(in_file)
    in_file_duration = in_file_probe_result.get('format', {}).get('duration', None)
    print(in_file_duration)

    input_stream = ffmpeg.input(in_file)

    video = input_stream.trim(start=start, end=end).setpts('PTS-STARTPTS') #presentation timestamp
    audio = (
        input_stream
        .filter_('atrim', start=start, end=end)
        .filter_('asetpts', 'PTS-STARTPTS')
    )

    video_audio = ffmpeg.concat(video, audio, v=1, a=1)

    output = ffmpeg.output(video_audio, out_file, format='mp4')
    output.run()

trim("videos/example.mp4", "videos/example_trimmed.mp4", 5, 9)