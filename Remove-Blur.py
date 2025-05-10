# SPDX-License-Identifier: CC0-1.0
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see <https://creativecommons.org/publicdomain/zero/1.0/>

import os
import subprocess
import torch
from PIL import Image
import torch.nn.functional as F
from torchvision import transforms

mosaic_size = (730/29, 1763/70)
window_size = (930, 1842)

print('mosaic_size is', mosaic_size)

def load_png_frames(frames_folder):
    for filename in os.listdir(frames_folder):
        if filename.lower().endswith(".png"):
            filepath = os.path.join(frames_folder, filename)
            try:
                image = Image.open(filepath)
                image = image.convert("RGBA")
                transform = transforms.ToTensor()
                img = transform(image).mul(0xFF).to(torch.uint8)
                yield filename, img
            except Exception as e:
                print(f"Error processing {filename}: {e}")

transform = transforms.ToPILImage()

# V2 .. automatically find windows position
for name, frame in load_png_frames('frames'):
    oframe = frame
    frame = (frame[:3].float().mean(0, keepdim=True) < 45).float()
    ff = F.unfold(frame[None, ...], 3, 1, 1, 1)
    s1 = torch.tensor((0,0,0,1,1,1,0,0,0), dtype=float).view(1,1,3,3)
    sf1 = F.unfold(s1, 3,1,0,1)
    s2 = torch.tensor((0,1,0,0,1,0,0,1,0), dtype=float).view(1,1,3,3)
    sf2 = F.unfold(s2, 3,1,0,1)
    a = (ff - sf1).abs().sum(-2, keepdim=True)
    b = (ff - sf2).abs().sum(-2, keepdim=True)
    fa = F.fold(a, frame.size()[-2:], 1,1,0,1)
    fb = F.fold(b, frame.size()[-2:],1,1,0,1)
    fa = fa <= 1/256
    fb = fb <= 1/256
    m = fa | fb

    imageA = frame.float().mul(0xFF).to(torch.uint8)
    imageB = fa.float().mul(0xFF)[0].to(torch.uint8)
    imageC = fb.float().mul(0xFF)[0].to(torch.uint8)
    image = torch.cat((imageA, imageB, imageC, torch.full_like(imageA, 0xFF)), 0)
    frame = oframe

    hframe = image.float().mean(-1, keepdim=True)
    vframe = image.float().mean(-2, keepdim=True)
    hframe = (hframe[1:2] >= 16).float().mul(torch.tensor((0,0xFF,0,0xFF), dtype=float).view(4,1,1))
    vframe = (vframe[2:3] >= 16).float().mul(torch.tensor((0,0,0xFF,0xFF), dtype=float).view(4,1,1))
    mframe = torch.max(hframe.expand_as(frame), vframe.expand_as(frame))

    mframe = oframe + mframe
    mframe = mframe / mframe[3:4] * 0xFF

    image = mframe.to(torch.uint8)

    foundX = False
    foundY = False
    for y in range(350,1900):
        if hframe[1,y,0] != 0:
            foundX = True
            break
    for x in range(0,1230):
        if vframe[2,0,x] !=0:
            foundY = True
            break
    if foundX and foundY:
        print(f"{name} position found at (x={x}, y={y})")
    else:
        print(f"{name} position not found")
        continue
    image[0,y,x] = 0xFF
    image[1,y,x] = 0
    image[2,y,x] = 0
    image[3,y,x] = 0xFF

    image = transform(image)
    image.save(os.path.join('frames_detected', name))

gframe = None
for name, frame in load_png_frames('frames_detected'):
    red_channel = frame[0,:,:]
    green_channel = frame[1,:,:]
    blue_channel = frame[2,:,:]
    red_pixels = (red_channel==0xFF) & (green_channel==0) & (blue_channel==0)
    y,x = torch.where(red_pixels)
    window_pos = (y[0].item(), x[0].item())
    print(f"{name} First red pixel found at (x={window_pos[-2]}, y={window_pos[-1]})")
    frame = frame[:, window_pos[-2]:, window_pos[-1]:][:, :window_size[-2], :window_size[-1]]
    image = transform(frame)
    image.save(os.path.join('windows', name))

    hframe = frame.float().mean(-1, keepdim=True)
    vframe = frame.float().mean(-2, keepdim=True)
    mframe = (hframe.expand_as(frame)+vframe.expand_as(frame)).div(2)
    hframe2 = (mframe[:, :-1,:-1] - mframe[:,1:,:-1]).abs().mean(0, keepdim=True)
    vframe2 = (mframe[:, :-1,:-1] - mframe[:,:-1,1:]).abs().mean(0, keepdim=True)
    hframe2 = hframe2>4
    vframe2 = vframe2>4
    for y in range(25, vframe2.size(-2)-25):
        if hframe2[0,y,50]:
            break
    for x in range(25, vframe2.size(-1)-25):
        if vframe2[0,50,x]:
            break
    mosaic_y = int(y+1)
    mosaic_x = int(x+1)
    while mosaic_y - mosaic_size[-2] >0:
        mosaic_y -= mosaic_size[-2]
    while mosaic_x - mosaic_size[-1] >0:
        mosaic_x -= mosaic_size[-1]
    print(f"{name} Mosaic offset found at (x={mosaic_x}, y={mosaic_y})")
    mframe2 = hframe2 | vframe2
    mframe2 = F.pad(mframe2, (0,1,1,0))
    mframe = mframe.to(torch.uint8)
    mframe2[:,:25] =0
    mframe2[:,-25:]=0
    mframe2[:,:,:25]=0
    mframe2[:,:,-25:]=0
    mframe = torch.where(mframe2.expand_as(mframe), torch.tensor((0,0,0xFF,0xFF), dtype=torch.uint8).view(4,1,1).expand_as(mframe), frame)
    mask = torch.zeros_like(frame, dtype=float)
    y = mosaic_y + mosaic_size[-2]/2
    while y < hframe2.size(-2):
        x = mosaic_x + mosaic_size[-1]/2
        while x < vframe2.size(-1):
            x_int = int(x)
            y_int = int(y)
            mask[:, y_int, x_int] =1
            mframe[0, y_int, x_int] =0
            mframe[1, y_int, x_int] =0xFF
            x += mosaic_size[-1]
        y += mosaic_size[-2]
    image = transform(mframe)
    image.save(os.path.join('mosaics', name))

    if gframe is None:
        gframe = torch.zeros_like(frame, dtype=float)
    gframe += frame * mask

    image = torch.zeros_like(gframe)
    image[:] = gframe

    run = True
    while run:
        c = image[3:4]==0
        run = torch.any(c)
        image += c.float()*F.avg_pool2d(image,3,1,1,False,False,1)

    image = image.div(image[3:4]).mul(0xFF)
    image = image.to(torch.uint8)
    image = transform(image)
    image.save(os.path.join('accumulated', name))

# ---------- Automatic FFmpeg call ----------
def create_video_from_frames_with_gaps(frames_folder, output_folder, output_video_name, ffmpeg_path, framerate=30):
    # Check if the frames folder exists
    if not os.path.exists(frames_folder):
        print(f"The folder {frames_folder} does not exist.")
        return

    # Create the output folder if necessary
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Output folder created: {output_folder}")

    # List and sort the images
    frames = [f for f in os.listdir(frames_folder) if f.lower().endswith('.png')]
    frames.sort()

    if not frames:
        print("No images found in the folder.")
        return

    # Rename the files to 0001.png, 0002.png...
    for i, file in enumerate(frames):
        old_path = os.path.join(frames_folder, file)
        new_name = f"{i + 1:04d}.png"
        new_path = os.path.join(frames_folder, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed {file} to {new_name}")

    # Generate the full output path
    output_video_path = os.path.join(output_folder, output_video_name)

    # Generate the FFmpeg command (without concat, using %04d.png)
    input_pattern = os.path.join(frames_folder, "%04d.png")
    command = [
        ffmpeg_path,
        "-framerate", str(framerate),   # set input framerate
        "-i", input_pattern,           # input file pattern
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-r", str(framerate),          # output framerate
        output_video_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"Video successfully created at {output_video_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error while creating the video: {e}")

# Example usage
frames_folder = "accumulated"
output_folder = "video-output"
output_video_name = "output_video.mp4"
ffmpeg_path = r"C:\Users\Danie\Mon Drive\Bot Python Discord\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"

create_video_from_frames_with_gaps(frames_folder, output_folder, output_video_name, ffmpeg_path)
