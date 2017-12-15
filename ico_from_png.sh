if [ "$1" != "" ]; then
    convert "$1" -resize 256x256 "$1-256.png"
    convert "$1" -resize 128x128 "$1-128.png"
    convert "$1" -resize 96x96 "$1-96.png"
    convert "$1" -resize 64x64 "$1-64.png"
    convert "$1" -resize 48x48 "$1-48.png"
    convert "$1" -resize 32x32 "$1-32.png"
    convert "$1" -resize 16x16 "$1-16.png"
    convert "$1-256.png" "$1-128.png" "$1-96.png" "$1-64.png" "$1-48.png" "$1-32.png" "$1-16.png" "$1.ico"
else
    echo "Supply path to .png image"
fi
