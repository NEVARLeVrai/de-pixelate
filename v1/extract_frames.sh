#!/bin/bash
# SPDX-License-Identifier: CC0-1.0
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see <https://creativecommons.org/publicdomain/zero/1.0/>.

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null
then
    echo "ffmpeg could not be found. Please install it."
    exit
fi

# Check if a video file is provided as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <video_file.webm>"
  exit 1
fi

video_file="$1"

# Check if the video file exists
if [ ! -f "$video_file" ]; then
  echo "Error: Video file '$video_file' not found."
  exit 1
fi

# Create the frames directory if it doesn't exist
mkdir -p frames

# Extract frames using ffmpeg
ffmpeg -i "$video_file" -filter_complex "select=bitor(gt(scene\,0.01)\,eq(n\,0))" -vsync drop frames/%04d.png
echo "Frames extracted to the 'frames' directory."
