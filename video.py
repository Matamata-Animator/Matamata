import ffmpeg
(
    ffmpeg
    .input('generate/%d.jpg', framerate=25)
    .output('movie.mp4')
    .run()
)
