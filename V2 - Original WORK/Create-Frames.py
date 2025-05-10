import subprocess
import os

# Obtenir le chemin du répertoire où se trouve le script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_frames(video_path, output_folder, ffmpeg_path):
    # Create the output folder if it doesn't exist
    output_path = os.path.join(SCRIPT_DIR, output_folder)
    os.makedirs(output_path, exist_ok=True)
    
    print(f"Processing video: {video_path}")

    # FFmpeg command to extract frames based on scene changes and the first frame
    command = [
        ffmpeg_path,  # Path to ffmpeg
        "-i", video_path,  # Input video
        "-filter_complex", "select=bitor(gt(scene\\,0.001)\\,eq(n\\,0))",  # Filter to select frames
        "-vsync", "drop",  # To avoid frame synchronization issues
        os.path.join(output_path, "%04d.png")  # Output file naming pattern
    ]

    print(f"FFmpeg command: {' '.join(command)}")

    # Execute the command
    try:
        subprocess.run(command, check=True)
        print(f"Frames successfully extracted from {video_path} into {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error while extracting frames from {video_path}: {e}")

def extract_frames_from_all_videos(videos_folder, output_folder, ffmpeg_path):
    # List all files in the 'videos' folder
    videos_path = os.path.join(SCRIPT_DIR, videos_folder)

    print(f"Checking files in folder {videos_path}...")
    video_count = 0
    for filename in os.listdir(videos_path):
        if filename.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm')):  # Add more extensions if needed
            video_path = os.path.join(videos_path, filename)
            print(f"Video found: {video_path}")
            extract_frames(video_path, output_folder, ffmpeg_path)
            video_count += 1
        else:
            print(f"File skipped (not a video): {filename}")
    
    if video_count == 0:
        print(f"\nNo videos found in folder {videos_path}")
        print("Please place your videos in the 'video-input' folder")
    else:
        print(f"\nTotal number of videos processed: {video_count}")

# Example usage:
videos_folder = "video-input"  # Folder containing the videos
output_folder = "frames"  # Folder where extracted frames will be saved
ffmpeg_path = r"C:\Users\Danie\Mon Drive\Bot Python Discord\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"  # Path to ffmpeg

# Check if the 'videos' folder exists and contains files
videos_path = os.path.join(SCRIPT_DIR, videos_folder)
if not os.path.exists(videos_path):
    print(f"The folder {videos_path} does not exist.")
else:
    # Extract frames from all video files in the 'videos' folder
    extract_frames_from_all_videos(videos_folder, output_folder, ffmpeg_path)
