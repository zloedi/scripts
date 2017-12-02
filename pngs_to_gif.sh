convert -resize 600x -delay 5 -loop 0 frames/*.png -dither none -deconstruct -matte -depth 8 quality00.gif && convert quality00.gif -layers Optimize result00.gif
convert -resize 600x -delay 5 -loop 0 frames/*.png -deconstruct -matte -depth 8 quality01.gif && convert quality01.gif -layers Optimize result01.gif
convert -resize 600x -delay 5 -loop 0 frames/*.png -matte -depth 8 quality02.gif && convert quality02.gif -layers Optimize result02.gif
convert -resize 600x -delay 5 -loop 0 frames/*.png -depth 8 quality03.gif && convert quality03.gif -layers Optimize result03.gif
convert -resize 600x -delay 5 -loop 0 frames/*.png quality04.gif && convert quality04.gif -layers Optimize result04.gif
