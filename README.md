# de-pixelate"

This project is an enhancement of the original video depixelation project.
Fully automated

## Modifications

### New Python Scripts
- `Create-Frames.py` : Script to extract video frames
- `Remove-Blur.py` : Main depixelation script
- `Remove-Files.py` : Utility to clean temporary files

### Directory Structure
- `video-input/` : Contains source videos
- `video-output/` : Contains processed videos
- `frames_detected/` : Frames with window detection
- `mosaics/` : Images with pixel grid
- `accumulated/` : Accumulated images
- `windows/` : Extracted windows

## Usage

1. Place your video in the `video-input/` directory
2. Run `Create-Frames.py` to extract frames
3. Run `Remove-Blur.py` for depixelation processing
4. Results will be available in `video-output/`

## License

The files are dedicated to the public domain using the Creative Commons CC0 1.0 Universal Public Domain Dedication:

You can find the full text of the CC0 license online at: <https://creativecommons.org/publicdomain/zero/1.0/>

All other files in this repository are under a different, unspecified license. Copyright and related rights are retained by the original authors unless otherwise stated.