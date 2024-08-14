import os
import matplotlib.pyplot as plt
from PIL import Image

# Function to load image files from a folder and return both images and file names
def load_images_from_folder(folder):
    images = []
    file_names = []
    for filename in os.listdir(folder):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            img = Image.open(os.path.join(folder, filename))
            images.append(img)
            file_names.append(filename)
    return images, file_names

# Function to create a collage with titles
def create_collage(image_folder, figsize=(10, 10)):
    images, file_names = load_images_from_folder(image_folder)
    
    num_images = len(images)
    num_rows = 2
    num_cols = (num_images + num_rows - 1) // num_rows  # Round up to the nearest integer
    
    fig, axs = plt.subplots(num_rows, num_cols, figsize=figsize)
    
    for i, ax in enumerate(axs.flat):
        ax.axis('off')
        if i < num_images:
            img = images[i]
            ax.imshow(img)
            ax.set_title(file_names[i].replace('@2x.png', ''), fontsize=20, verticalalignment='bottom', color='white')
    
    plt.subplots_adjust(hspace=0.5)
    fig.patch.set_facecolor('#3E4C60')  # Set dark background
    fig.set_size_inches(32, 8)
    plt.savefig('receptacle_collage.png')

# Example usage
image_folder = "receptacles"
create_collage(image_folder)
