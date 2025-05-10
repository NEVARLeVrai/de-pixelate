import subprocess
import os

def extract_frames(video_path, output_folder, ffmpeg_path):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    print(f"Processing video: {video_path}")

    # FFmpeg command to extract frames based on scene changes and the first frame
    command = [
        ffmpeg_path,  # Path to ffmpeg
        "-i", video_path,  # Input video
        "-filter_complex", "select=bitor(gt(scene\\,0.001)\\,eq(n\\,0))",  # Filter to select frames
        "-vsync", "drop",  # To avoid frame synchronization issues
        os.path.join(output_folder, "%04d.png")  # Output file naming pattern
    ]

    print(f"FFmpeg command: {' '.join(command)}")

    # Execute the command
    try:
        subprocess.run(command, check=True)
        print(f"Frames successfully extracted from {video_path} into {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Error while extracting frames from {video_path}: {e}")

def extract_frames_from_all_videos(videos_folder, output_folder, ffmpeg_path):
    # List all files in the 'videos' folder
    print(f"Checking files in folder {videos_folder}...")
    for filename in os.listdir(videos_folder):
        if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm')):  # Add more extensions if needed
            video_path = os.path.join(videos_folder, filename)
            print(f"Video found: {video_path}")
            extract_frames(video_path, output_folder, ffmpeg_path)
        else:
            print(f"File skipped (not a video): {filename}")

# Example usage:
videos_folder = "video-input"  # Folder containing the videos
output_folder = "frames"  # Folder where extracted frames will be saved
ffmpeg_path = r"C:\Users\Danie\Mon Drive\Bot Python Discord\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"  # Path to ffmpeg

# Check if the 'videos' folder exists and contains files
if not os.path.exists(videos_folder):
    print(f"The folder {videos_folder} does not exist.")
else:
    # Extract frames from all video files in the 'videos' folder
    extract_frames_from_all_videos(videos_folder, output_folder, ffmpeg_path)
