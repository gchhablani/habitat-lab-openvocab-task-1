import os

import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch, FancyBboxPatch
from PIL import Image

from .constants import category_color_map, object_category_map
from .instance_color_map import InstanceColorMap
from .utils import wrap_text

def get_object_color(object_id):
    if InstanceColorMap.has_color(object_id):
        color = InstanceColorMap.get_color(object_id)
    else:
        raise NotImplementedError
    return color


class Object:
    def __init__(self, config, object_id):
        self.object_id = object_id
        self.config = config.object
        self.center_position = None
        self.is_on_floor = False

    @property
    def width(self):
        return self.config.width

    @property
    def height(self):
        return self.config.height

    def change_rectangle_color(self, color):
        self.object_rect.set_facecolor(color)
        InstanceColorMap.set_color(self.object_id, color)
        plt.gcf().canvas.draw()

    def plot_text_label(self, ax):
        self.text_position = (
            self.center_position[0],
            self.center_position[1] + self.config.text_margin,
        )

        wrapped_text = wrap_text(
            self.object_id, self.config.max_chars_per_line
        )
        ax.annotate(
            wrapped_text,
            xy=self.text_position,
            ha="center",
            va="center",
            fontsize=self.config.text_size,
            zorder=float('inf'),
        )

    def plot(self, ax=None, origin=(0, 0)):
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        color = get_object_color(self.object_id)

        # Create the object rectangle
        self.object_rect = FancyBboxPatch(
            (origin[0], origin[1]),
            self.config.width,
            self.config.height,
            edgecolor="white",
            facecolor=color,
            linewidth=0,
            linestyle="-",
            boxstyle=f"Round, pad=0, rounding_size={self.config.rounding_size}",
            alpha=1.0,
        )

        ax.add_patch(self.object_rect)

        # Calculate the coordinates of the white border if is_on_floor is True
        if self.is_on_floor:
            padding = 0.1 * self.config.width  # Adjust this value as needed
            border_rect = FancyBboxPatch(
                (origin[0] - padding, origin[1] - padding),
                self.config.width + 2 * padding,
                self.config.height + 2 * padding,
                edgecolor="white",
                facecolor="none",
                linewidth=self.config.on_floor_linewidth,
                linestyle="-",
                boxstyle=f"Round, pad=0, rounding_size={self.config.rounding_size}",
                alpha=1.0,
            )

            ax.add_patch(border_rect)

        self.center_position = (
            origin[0] + self.config.width / 2,
            origin[1] + self.config.height / 2,
        )

        self.plot_text_label(ax)

        if created_fig:
            return fig, ax
        else:
            return ax