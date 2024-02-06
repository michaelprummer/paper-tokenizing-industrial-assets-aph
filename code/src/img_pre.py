from PIL import Image, ImageEnhance
from glob import glob
from mconfig import config
from image_ctrl import pImageController
import os

c = pImageController(config)

files = glob("./assets/original/mpls/wire_only_mpls/moving/*", recursive=True)

for file in files:
    img = Image.open(file)
    if img.width < img.height:
        print("Height > Width: ",file, img.width, img.height)
    
    if img.width < 1024:
        print("Too small: ", img.width)
        target_width = 1024
        w_percent = (target_width/float(img.size[0]))
        h_size = int((float(img.size[1])*float(w_percent)))
        resized_img = img.resize(
            (target_width, h_size), Image.Resampling.LANCZOS)                                
        resized_img.save(file)

    if img.width > 1024:
        print("Too big: ", img.width)
        target_width = 1024
        w_percent = (target_width/float(img.size[0]))
        h_size = int((float(img.size[1])*float(w_percent)))
        resized_img = img.resize(
            (target_width, h_size), Image.Resampling.LANCZOS)                                
        resized_img.save(file)