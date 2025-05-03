# SPDX-License-Identifier: CC0-1.0
#
# To the extent possible under law, the author(s) have dedicated all
# copyright and related and neighboring rights to this software to the
# public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication
# along with this software. If not, see <https://creativecommons.org/publicdomain/zero/1.0/>.

import os
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
        transform = transforms.ToTensor()
        yield filename, transform(image).mul(0xFF).to(torch.uint8)
      except Exception as e:
        print(f"Error processing {filename}: {e}")

gframe = None
for name, frame in load_png_frames('frames'):
  # find window position
  red_channel = frame[0, :, :]
  green_channel = frame[1, :, :]
  blue_channel = frame[2, :, :]
  red_pixels = (red_channel == 0xFF) & (green_channel == 0) & (blue_channel == 0)
  y, x = torch.where(red_pixels)
  window_pos = (
    y[0].item(),
    x[0].item()
  )
  print(f"{name} First red pixel found at (x={window_pos[-2]}, y={window_pos[-1]})")
  frame = frame[:, window_pos[-2]:, window_pos[-1]:][:, :window_size[-2], :window_size[-1]]
  transform = transforms.ToPILImage()
  image = transform(frame)
  image.save(os.path.join('windows', name))

  # find mosaic position (this takes lots of memory.. not optimized.. just casting to bytes sometimes.. very slow..)
  hframe = frame.float().mean(-1,  keepdim=True)
  vframe = frame.float().mean(-2,  keepdim=True)
  mframe = (hframe.expand_as(frame) + vframe.expand_as(frame)).div(2)
  hframe2 = (mframe[:,  :-1, :-1] - mframe[:, 1:, :-1]).abs().mean(0, keepdim=True)
  vframe2 = (mframe[:,  :-1, :-1] - mframe[:, :-1, 1:]).abs().mean(0, keepdim=True)
  hframe2 = hframe2 > 4
  vframe2 = vframe2 > 4
  # get x,y position
  for y in range(25, vframe2.size(-2) - 25):
    if hframe2[0, y, 50]:
      break
  for x in range(25, vframe2.size(-1) - 25):
    if vframe2[0, 50, x]:
      break
  mosaic_y = int(y + 1)
  mosaic_x = int(x + 1)
  while mosaic_y - mosaic_size[-2] > 0:
    mosaic_y -= mosaic_size[-2]
  while mosaic_x - mosaic_size[-1] > 0:
    mosaic_x -= mosaic_size[-1]
  print(f"{name} Mosaic offset found at (x={mosaic_x}, y={mosaic_y})")
  mframe2 = hframe2 | vframe2
  mframe2 = F.pad(mframe2, (0,1,1,0))
  mframe = mframe.to(torch.uint8)
  mframe2[:,:25] = 0
  mframe2[:,-25:] = 0
  mframe2[:,:, :25] = 0
  mframe2[:,:, -25:] = 0
  #print(mframe2.size(), mframe.size(), frame.size())
  mframe = torch.where(mframe2.expand_as(mframe), torch.tensor((0,0,0xFF,0xFF), dtype=torch.uint8).view(4, 1, 1).expand_as(mframe), frame)
  mask = torch.zeros_like(frame, dtype=float)
  y = mosaic_y + mosaic_size[-2] / 2
  while y < hframe2.size(-2):
    x = mosaic_x + mosaic_size[-1] / 2
    while x < vframe2.size(-1):
      x_int = int(x)
      y_int = int(y)
      mask[:, y_int, x_int] = 1
      mframe[0, y_int, x_int] = 0
      mframe[1, y_int, x_int] = 0xFF
      mframe[0, y_int, x_int] = 0
      mframe[1, y_int, x_int] = 0xFF

      x += mosaic_size[-1]
    y += mosaic_size[-2]
  #mframe[1, mosaic_y::mosaic_size, mosaic_x::mosaic_size] = 1
  image = transform(mframe)
  image.save(os.path.join('mosaics', name))

  if gframe is None:
    gframe = torch.zeros_like(frame, dtype=float)
  gframe += frame * mask

  #image = gframe.div(gframe[3:4]).mul(0xFF)
  image = torch.zeros_like(gframe)
  image[:] = gframe

  # grow pixels
  run = True
  while run:
    c = image[3:4] == 0
    run = torch.any(c)
    image += c.float() * F.avg_pool2d(image, 3, 1, 1, False, False, 1)

  image = image.div(image[3:4]).mul(0xFF)
  image = image.to(torch.uint8)
  image = transform(image)
  image.save(os.path.join('accumulated', name))
