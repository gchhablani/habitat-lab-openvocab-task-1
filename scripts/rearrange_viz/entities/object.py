import os

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch
import numpy as np
from PIL import Image

from .constants import category_color_map, object_category_map, object_states_colors
from .instance_color_map import InstanceColorMap
from .utils import wrap_text, resize_icon_height

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
        self.state_rect_ratio = 0.4
        self.set_switch_icon()

    def set_switch_icon(self):
        img_path = os.path.join("receptacles", "switch.png")
        img_path = os.path.join("receptacles", "switch.png")
        img = Image.open(img_path).convert("RGBA")
        
        # Resize image to match the state rectangle height
        resized_img = resize_icon_height(img, self.state_rect_ratio * self.config.height)
        img_array = np.array(resized_img)
        self.switch_icon = img_array

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

    def plot_state_rectangles(self, ax, origin):
        state_rect_width = self.state_rect_ratio * self.config.width  # Smaller width
        state_rect_height = self.state_rect_ratio * self.config.height  # Smaller height
        state_rect_spacing = 0.1 * self.config.height  # Spacing between rectangles

        num_states = len([state for state in object_states_colors if state in self.states])
        total_height = num_states * state_rect_height + (num_states - 1) * state_rect_spacing
        start_y_position = self.center_position[1] - total_height / 2

        y_position = start_y_position
        for state, colors in object_states_colors.items():
            if state in self.states:
                state_value = str(self.states[state]).lower()
                color = colors[state_value]
                state_rect = FancyBboxPatch(
                    (origin[0] + self.config.width + state_rect_width / 2, y_position),
                    state_rect_width,
                    state_rect_height,
                    edgecolor="black",
                    facecolor=color,
                    linewidth=0,
                    linestyle="-",
                    boxstyle=f"Round, pad=0, rounding_size={self.config.rounding_size}",
                    alpha=1.0,
                    zorder=float('inf'),
                )
                ax.add_patch(state_rect)
                # Check if the state has changed
                if state not in self.previous_states or self.previous_states[state] != self.states[state]:
                    # Plot the switch icon using ax.imshow
                    ax.imshow(self.switch_icon, aspect='auto',
                              extent=(origin[0] + self.config.width + state_rect_width * 1.5,
                                      origin[0] + self.config.width + state_rect_width * 1.5 + self.switch_icon.shape[1],
                                      y_position,
                                      y_position + state_rect_height),
                              zorder=float('inf'))
                y_position += state_rect_height + state_rect_spacing
        self.previous_states = self.states.copy()

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
        self.plot_state_rectangles(ax, origin)

        if created_fig:
            return fig, ax
        else:
            return ax
