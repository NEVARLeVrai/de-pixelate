# de-pixelate

This project is an enhancement of the original video depixelation project.

## Versions

### V2 - Original WORK
- Improved window detection
- Automatic folder creation
- Better error handling
- All paths are now relative to the script location
- Added video processing status messages

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
The original project is under CC0 1.0 Universal Public Domain Dedication.
