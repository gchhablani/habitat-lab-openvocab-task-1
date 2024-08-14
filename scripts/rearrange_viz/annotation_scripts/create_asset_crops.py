import os
import numpy as np
from PIL import Image

def crop_height(image):
    alpha = np.array(image)[:, :, 3]
    non_zero_rows = np.any(alpha != 0, axis=1)
    
    top, bottom = np.where(non_zero_rows)[0][[0, -1]]
    
    width = image.width
    cropped_image = image.crop((0, top, width, bottom + 1))
    return cropped_image

def process_directory(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_dir, filename)
            image = Image.open(image_path).convert("RGBA")
            
            cropped_image = crop_height(image)
            
            output_path = os.path.join(output_dir, filename)
            cropped_image.save(output_path)

input_directory = 'receptacles'
output_directory = 'cropped_receptacles'

process_directory(input_directory, output_directory)
