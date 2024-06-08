import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .constants import receptacle_color_map, receptacle_properties
from .placeholder import Placeholder
from .utils import add_tint_to_rgb


class Receptacle:
    """
    Represents a receptacle object in a 2D space and provides methods for plotting it.
    """

    def __init__(self, config, receptacle_id, icon_path):
        """
        Initializes a Receptacle instance.

        Parameters:
            config (object): A configuration object containing parameters for receptacle rendering.
            receptacle_id (str): Identifier for the receptacle.
            icon_path (str): Path to the icon image file representing the receptacle.
        """
        self.config = config.receptacle
        self.receptacle_id = receptacle_id
        self.icon_path = icon_path
        self.center_placeholder_position = None  # Initialize center position
        self.top_placeholder_position = None  # Initialize top position
        self.plot_top_placeholder = False
        self.plot_center_placeholder = False
        self.new_top_item_position = None
        self.init_size()

    @property
    def horizontal_margin(self):
        """
        Horizontal margin of the receptacle.

        Returns:
            float: Horizontal margin of the receptacle.
        """
        return self.config.horizontal_margin

    def resize_icon(self, icon):
        """
        Resizes the receptacle icon image.

        Parameters:
            icon (PIL.Image.Image): Icon image of the receptacle.

        Returns:
            PIL.Image.Image: Resized icon image.
        """
        width, height = icon.size
        scaling_factor = self.config.target_height / height

        # Resize the image
        new_width = int(width * scaling_factor)
        new_height = int(height * scaling_factor)
        resized_icon = icon.resize((new_width, new_height))
        return resized_icon

    def init_size(self):
        """
        Initializes the size of the receptacle based on its icon image.
        """
        icon = Image.open(self.icon_path)
        icon = self.resize_icon(icon)
        icon_width, icon_height = icon.size
        self.width = icon_width + 2 * self.horizontal_margin
        self.height = icon_height

    def calculate_placeholder_heights(self, image):
        """
        Calculate the top and middle height of the object in the image.

        Args:
        - image: PIL Image object (RGBA)

        Returns:
        - center_height: Middle height of the object in the image
        - top_height: Height of the non-empty part of the image from the top
        """
        alpha = np.array(image)[:, :, 3]
        bottom = alpha.shape[0] + 1
        top = 0
        for idx, row in enumerate(alpha):
            middle_idx = row.shape[0] // 2
            row_sum = np.sum(row[middle_idx])
            if row_sum != 0:
                top = idx + 1
                break
        top_height = bottom - top
        center_height = top_height / 2
        return center_height, top_height

    def plot(self, ax=None, position=(0, 0)):
        """
        Plots the receptacle on a matplotlib Axes.

        Parameters:
            ax (matplotlib.axes.Axes, optional): Axes to plot the receptacle on.
                                                 If None, a new figure and Axes will be created.
                                                 Defaults to None.
            position (tuple, optional): Position of the receptacle's bottom-left corner.
                                        Defaults to (0, 0).

        Returns:
            matplotlib.figure.Figure, matplotlib.axes.Axes or matplotlib.axes.Axes: If ax is None,
            returns the created figure and axes. Otherwise, returns the modified axes.
        """
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        icon = Image.open(self.icon_path)
        icon = self.resize_icon(icon)
        color = receptacle_color_map[
            "_".join(self.receptacle_id.split("_")[:-1])
        ]
        color = tuple(int(255 * i) for i in color)
        icon = add_tint_to_rgb(icon, tint_color=color)
        receptacle_width, receptacle_height = icon.size
        ax.imshow(
            icon,
            extent=(
                (position[0] + self.horizontal_margin),
                (position[0] + receptacle_width + self.horizontal_margin),
                position[1],
                (position[1] + receptacle_height),
            ),
        )

        center_height, top_height = self.calculate_placeholder_heights(icon)
        self.center_placeholder_position = (
            position[0] + self.width / 2,
            position[1] + center_height,
        )
        self.center_placeholder_origin = (
            self.center_placeholder_position[0]
            - self.config.placeholder.width / 2,
            self.center_placeholder_position[1]
            - self.config.placeholder.height / 2,
        )
        self.top_placeholder_position = (
            position[0] + self.width / 2,
            position[1] + top_height + self.config.placeholder_margin,
        )
        self.top_placeholder_origin = (
            self.top_placeholder_position[0]
            - self.config.placeholder.width / 2,
            self.top_placeholder_position[1]
            - self.config.placeholder.height / 2,
        )
        self.new_top_item_position = self.top_placeholder_origin

        properties = receptacle_properties[
            "_".join(self.receptacle_id.split("_")[:-1])
        ]
        # TODO: See how to handle `is_same`
        if self.plot_top_placeholder and properties["is_same"]:
            self.plot_center_placeholder = True
            self.plot_top_placeholder = False
        if self.plot_top_placeholder and properties["is_on_top"]:
            self.top_placeholder = Placeholder(self.config)
            ax = self.top_placeholder.plot(ax, self.top_placeholder_origin)
            self.new_top_item_position = (
                self.top_placeholder_origin[0],
                self.top_placeholder_origin[1]
                + self.config.placeholder.height,
            )
        if self.plot_center_placeholder and properties["is_inside"]:
            self.center_placeholder = Placeholder(self.config)
            ax = self.center_placeholder.plot(
                ax, self.center_placeholder_origin
            )

        ax.axis("off")

        if created_fig:
            return fig, ax
        else:
            return ax
