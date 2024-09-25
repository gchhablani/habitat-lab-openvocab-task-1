import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from .constants import receptacle_color_map, receptacle_properties
from .placeholder import Placeholder
from .utils import add_tint_to_rgb, resize_icon_height

# DEFAULT_STATES = {
#     "is_clean": False,
#     "is_filled": False,
#     "is_powered_on": False,
# }

def calculate_placeholder_heights(image):
    # This method uses the alpha values to calculate center and top height of the icon
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


class Receptacle:
    def __init__(self, config, receptacle_id, icon_path):
        self.config = config.receptacle
        self.object_config = config.object
        self.receptacle_id = receptacle_id
        self.icon_path = icon_path

        self.center_placeholder_position = None  # Initialize center position
        self.top_placeholder_position = None  # Initialize top position

        self.plot_top_placeholder = False
        self.plot_center_placeholder = False

        self.next_top_item_position = None

        self.plot_states = {
            "is_clean": False,
            "is_filled": False,
            "is_powered_on": False,
        }
        # This initialization does not matter as we parse the states from the files
        # and set both to the same value initially
        self.previous_states = {}
        self.states = {}

        self.init_size()

    @property
    def horizontal_margin(self):
        return self.config.horizontal_margin

    def init_size(self):
        icon = self.get_icon(add_tint=False)
        icon_width, icon_height = icon.size
        self.width = icon_width + 2 * self.horizontal_margin
        self.height = icon_height

    def get_icon(self, add_tint=True):
        icon = Image.open(self.icon_path)
        icon = resize_icon_height(icon, self.config.target_height)
        if add_tint:
            color = receptacle_color_map[
                "_".join(self.receptacle_id.split("_")[:-1])
            ]
            color = tuple(int(255 * i) for i in color)
            icon = add_tint_to_rgb(icon, tint_color=color)
        return icon

    def set_placeholder_positions(self, icon, origin):
        center_height, top_height = calculate_placeholder_heights(icon)
        self.center_placeholder_position = (
            origin[0] + self.width / 2,
            origin[1] + center_height,
        )
        self.center_placeholder_origin = (
            self.center_placeholder_position[0]
            - self.config.placeholder.width / 2,
            self.center_placeholder_position[1]
            - self.config.placeholder.height / 2,
        )
        self.top_placeholder_position = (
            origin[0] + self.width / 2,
            origin[1] + top_height + self.config.placeholder_margin,
        )
        self.top_placeholder_origin = (
            self.top_placeholder_position[0]
            - self.config.placeholder.width / 2,
            self.top_placeholder_position[1]
            - self.config.placeholder.height / 2,
        )
        
        # The bottom is needed to calculate the stacked objects in case
        # there are many initialized on the same receptacle
        self.next_top_item_position = (
            self.top_placeholder_origin[0],
            self.top_placeholder_origin[1] + abs(
                self.object_config.text_margin
            ) + self.object_config.bottom_text_extra_margin
        )

    def plot_state_attributes(self, ax, origin):
        # # Plot only if the state is different from the default state or the previous state
        # if self.states == self.previous_states:
        #     return
        # NOTE: The current logic is to set whether to display a particular state or not outside of this class
        # This is because we need control at the row level whether to display the state or not
        # We also need to pre-decide the number of rows, and update the bottom pad accordingly.

        # Plot the attributes as a text
        plot_height = origin[1] - self.config.state_text_relative_height
        if self.plot_states["is_clean"] and "is_clean" in self.states:
            if self.states["is_clean"]:
                ax.text(
                    self.center_placeholder_position[0],
                    plot_height,
                    "clean",
                    ha="center",
                    va="center",
                    fontsize=13,
                    color="white",
                )
            else:
                # default is dirty
                ax.text(
                    self.center_placeholder_position[0],
                    plot_height,
                    "dirty",
                    ha="center",
                    va="center",
                    fontsize=13,
                    color="black",
                )
            plot_height -= self.config.state_text_relative_height

        if self.plot_states["is_filled"] and "is_filled" in self.states:
            if self.states["is_filled"]:
                ax.text(
                    self.center_placeholder_position[0],
                    plot_height,
                    "filled",
                    ha="center",
                    va="center",
                    fontsize=13,
                    color="white",
                )
            else:
                # default is empty
                ax.text(
                    self.center_placeholder_position[0],
                    plot_height,
                    "empty",
                    ha="center",
                    va="center",
                    fontsize=13,
                    color="black",
                )
            plot_height -= self.config.state_text_relative_height

        if self.plot_states["is_powered_on"] and "is_powered_on" in self.states:
            if self.states["is_powered_on"]:
                ax.text(
                    self.center_placeholder_position[0],
                    plot_height,
                    "on",
                    ha="center",
                    va="center",
                    fontsize=13,
                    color="white",
                )
            else:
                # default is off
                ax.text(
                    self.center_placeholder_position[0],
                    plot_height,
                    "off",
                    ha="center",
                    va="center",
                    fontsize=13,
                    color="black",
                )


    def plot_placeholders(self, ax):
        assert hasattr(self, "next_top_item_position"), (
            f"next item position is not set for receptacle: {self.receptacle_id}"
        )
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
            self.next_top_item_position = (
                self.next_top_item_position[0],
                self.next_top_item_position[1]
                + self.config.placeholder.height,
            )
        if self.plot_center_placeholder and properties["is_inside"]:
            self.center_placeholder = Placeholder(self.config)
            ax = self.center_placeholder.plot(
                ax, self.center_placeholder_origin
            )
        
    def plot(self, ax=None, origin=(0, 0)):
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        icon = self.get_icon()
        receptacle_width, receptacle_height = icon.size
        ax.imshow(
            icon,
            extent=(
                (origin[0] + self.horizontal_margin),
                (origin[0] + receptacle_width + self.horizontal_margin),
                origin[1],
                (origin[1] + receptacle_height),
            ),
        )
        self.set_placeholder_positions(icon, origin)
        self.plot_placeholders(ax)
        self.plot_state_attributes(ax, origin)

        if created_fig:
            ax.axis("off")
            return fig, ax
        else:
            return ax
