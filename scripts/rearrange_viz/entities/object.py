import os

import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch, FancyBboxPatch
import numpy as np
from PIL import Image

from .constants import category_color_map, object_category_map, ROOM_COLOR
from .instance_color_map import InstanceColorMap
from .utils import wrap_text, resize_icon_height, add_tint_to_rgb

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

        # Object states
        self.states = {}
        self.previous_states = {}
        self.set_icons()

    @property
    def width(self):
        return self.config.width

    @property
    def height(self):
        return self.config.height

    def plot_on_floor_line(self, ax):
        assert self.center_position is not None, f"Center position is empty for object: {self.object_id}"
        assert self.text_position is not None, f"Text position is empty for object: {self.object_id}"
        # Calculate the height after the text position based on number of lines in the text 
        line_start = (
            self.center_position[0]
            - self.config.on_floor_line_length_ratio * self.config.width,
            self.text_position[1] - self.config.extra_space_between_objects / 2,
        )
        line_end = (
            self.center_position[0]
            + self.config.on_floor_line_length_ratio * self.config.width,
            self.text_position[1] - self.config.extra_space_between_objects / 2,
        )
        line = ConnectionPatch(
            xyA=line_start,
            xyB=line_end,
            coordsA="data",
            coordsB="data",
            axesA=ax,
            axesB=ax,
            color="white",
            linewidth=self.config.on_floor_linewidth,
        )
        ax.add_artist(line)

    def set_icons(self):
        # img = Image.open("object_states/object_dirty.png").convert("RGBA")
        # resized_img = resize_icon_height(img, self.config.height)
        # img_array = np.array(resized_img)
        # self.dirty_icon = img_array
        
        img = Image.open("object_states/object_clean.png").convert("RGBA")
        resized_img = resize_icon_height(img, self.config.height)
        img_array = np.array(resized_img)
        self.clean_icon = img_array
        
        img = Image.open("object_states/object_clean_plus_on.png").convert("RGBA")
        resized_img = resize_icon_height(img, self.config.height)
        img_array = np.array(resized_img)
        self.clean_plus_on_icon = img_array

        img = Image.open("object_states/object_on.png").convert("RGBA")
        resized_img = resize_icon_height(img, self.config.height)
        img_array = np.array(resized_img)
        self.powered_on_icon = img_array

        img = Image.open("object_states/refresh.png").convert("RGBA")
        resized_img = resize_icon_height(img, self.config.height)
        img_array = np.array(resized_img)
        self.refresh_icon = img_array

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

    def hex_to_rgb(self, hex_color):
        # Remove the hash symbol if present
        hex_color = hex_color.lstrip('#')

        # Convert the hex color to RGB components
        rgb = list(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return rgb

    def plot_state_attributes(self, ax, origin):
        if self.previous_states != self.states:
            # show refresh icon inside the object rect
            ax.imshow(
                self.refresh_icon,
                extent=[
                    origin[0] + 0.2 * self.config.width,
                    origin[0] + 0.8 * self.config.width,
                    origin[1] + 0.2 * self.config.height,
                    origin[1] + 0.8 * self.config.height,
                ],
                zorder=float('inf'),
            )
            self.previous_states = self.states.copy()

        if 'is_clean' in self.states and self.states['is_clean'] and 'is_powered_on' in self.states and self.states['is_powered_on']:
            ax.imshow(
                self.clean_plus_on_icon,
                extent=[
                    origin[0] - 1 * self.config.width,
                    origin[0] + 2 * self.config.width,
                    origin[1] - 1 * self.config.height,
                    origin[1] + 2 * self.config.height,
                ],
            )
        elif 'is_clean' in self.states and self.states['is_clean']:
            ax.imshow(
                self.clean_icon,
                extent=[
                    origin[0] - 1 * self.config.width,
                    origin[0] + 2 * self.config.width,
                    origin[1] - 1 * self.config.width,
                    origin[1] + 2 * self.config.height,
                ],
            )
        elif 'is_powered_on' in self.states and self.states['is_powered_on']:
            ax.imshow(
                self.powered_on_icon,
                extent=[
                    origin[0] - 1 * self.config.width,
                    origin[0] + 2 * self.config.width,
                    origin[1] - 1 * self.config.height,
                    origin[1] + 2 * self.config.height,
                ],
            )

    def plot(self, ax=None, origin=(0, 0)):
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        color = get_object_color(self.object_id)

        if 'is_filled' in self.states and not self.states['is_filled']:
            # Create the object rectangle with only border
            self.object_rect = FancyBboxPatch(
                (origin[0], origin[1]),
                self.config.width,
                self.config.height,
                edgecolor=color,
                facecolor=ROOM_COLOR,
                linewidth=self.config.empty_state_linewidth,
                linestyle="-",
                boxstyle=f"Round, pad=0, rounding_size={self.config.rounding_size}",
                alpha=1.0,
            )
        else:
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

        self.center_position = (
            origin[0] + self.config.width / 2,
            origin[1] + self.config.height / 2,
        )

        self.plot_text_label(ax)

        if self.is_on_floor:
            # Draw a white line below the text label
            self.plot_on_floor_line(ax)

        color = get_object_color(self.object_id)
        self.clean_icon[self.clean_icon[:, :, 3] != 0, :3] = self.hex_to_rgb(color)
        self.clean_plus_on_icon[self.clean_plus_on_icon[:, :, 3] != 0, :3] = self.hex_to_rgb(color)
        self.powered_on_icon[self.powered_on_icon[:, :, 3] != 0, :3] = self.hex_to_rgb(color)
        self.refresh_icon[self.refresh_icon[:, :, 3] != 0, :3] = self.hex_to_rgb("#FFFFFF")
        self.plot_state_attributes(ax, origin)

        if created_fig:
            return fig, ax
        else:
            return ax
