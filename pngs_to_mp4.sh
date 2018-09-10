ffmpeg -framerate 60 -i frame%05d.png -c:v libx264 -crf 23 -pix_fmt yuv420p output.mp4
