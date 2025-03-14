import ffmpeg

in_file = ffmpeg.input('videos/example.mp4')
overlay_file = ffmpeg.input('images/transparent-image.png')
(
    in_file
    .overlay(overlay_file.filter('scale', width='-1', height='240').hflip())
    .output('videos\output\output.mp4')
    .run()
)