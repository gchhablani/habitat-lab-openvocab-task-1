import matplotlib.pyplot as plt

from .placeholder import Placeholder
from .utils import wrap_text
from .constants import ROOM_COLOR

class Room:
    def __init__(
        self,
        config,
        room_id,
        receptacles,
        objects=None,
        use_full_height=False,
        in_proposition=False,
        object_to_recep=None,
    ):
        self.global_config = config
        self.config = config.room
        self.room_id = room_id

        # Contained entities
        self.receptacles = receptacles
        self.objects = objects

        # If the room is mentioned in propositions
        self.in_proposition = in_proposition

        self.plot_placeholder = False

        # Initial object to receptacle mapping
        self.object_to_recep = object_to_recep

        self.num_receptacle_state_lines = 0
        # initialize the bottom pad with config bottom pad, but might change depending on the number of receptacle states
        self.bottom_pad = self.config.bottom_pad

        if self.objects:
            self.use_full_height = True
        else:
            self.use_full_height = use_full_height

        self.init_size()

    def init_widths(self):
        # Calculate width based on the objects and receptacles
        min_width = self.config.min_width
        if self.objects:
            object_widths = 0
            for object in self.objects:
                if self.object_to_recep is None:
                    object_widths += object.width
                else:
                    if object.object_id in self.object_to_recep.keys():
                        continue
                    else:
                        object_widths += object.width

            min_width = max(
                min_width, object_widths * self.config.min_width_per_object
            )

        # Calculate total room width including margins
        minimum_room_width = max(
            min_width, sum(receptacle.width for receptacle in self.receptacles)
        )
        self.room_width = (
            minimum_room_width + self.config.left_pad + self.config.right_pad
        )
        self.width = self.room_width + 2 * self.config.horizontal_margin


    def init_heights(self):
        # Init with min receptacle height
        # Need to increase the bottom pad by the number of lines we are planning to plot for receptacle states
        self.bottom_pad += self.config.per_receptacle_state_padding * self.num_receptacle_state_lines

        self.room_height = (
            self.config.min_height
        )
        for receptacle in self.receptacles:
            receptacle.temp_mx_height = receptacle.height

        if self.objects:
            self.room_height *= 2
            for obj in self.objects:
                if (
                    self.object_to_recep is not None
                    and obj.object_id in self.object_to_recep.keys()
                ):  
                    # print(obj.object_id)
                    receptacle_id = self.object_to_recep[obj.object_id]
                    if receptacle_id.startswith("floor_"):
                        continue
                    else:
                        current_receptacle = self.find_receptacle_by_id(
                            receptacle_id
                        )
                        current_receptacle.temp_mx_height += abs(obj.config.text_margin) + 2 * obj.config.height + obj.config.extra_space_between_objects
                        # We take max of all top item positions for now
                        self.room_height = max(self.room_height, current_receptacle.temp_mx_height)
        self.room_height = self.room_height + self.bottom_pad + self.config.top_pad
        self.height = self.room_height + 2 * self.config.vertical_margin
        
    def init_size(self):
        self.init_widths()
        self.init_heights()

    def cleanup(self):
        if self.objects:
            for obj in self.objects:
                del obj
            self.objects.clear()
        if self.receptacles:
            for recep in self.receptacles:
                del recep
            self.receptacles.clear()

    def find_object_by_id(self, object_id):
        if self.objects:
            for obj in self.objects:
                if obj.object_id == object_id:
                    return obj
        return None

    def find_receptacle_by_id(self, receptacle_id):
        for receptacle in self.receptacles:
            if receptacle.receptacle_id == receptacle_id:
                return receptacle
        return None
    
    def plot_objects(self, ax, actual_origin):
        if self.objects:
            # Handle non mapped objects
            # Calculate initial offset for objects considering left margin, horizontal padding, and spacing objects evenly
            total_object_width = 0
            num_objects = 0
            for obj in self.objects:
                if (
                    self.object_to_recep is None
                    or obj.object_id not in self.object_to_recep.keys()
                    or self.object_to_recep[obj.object_id].startswith("floor_")
                ):
                    total_object_width += obj.width
                    num_objects += 1

            spacing = (
                (
                    self.room_width
                    - self.config.object_horizontal_margin_fraction
                    * 2
                    * self.room_width
                )
                - total_object_width
            ) / (num_objects + 1)
            offset = (
                actual_origin[0]
                + self.config.object_horizontal_margin_fraction
                * self.room_width
                + spacing
            )

            for obj in self.objects:
                if (
                    self.object_to_recep is None
                    or obj.object_id not in self.object_to_recep.keys()
                    or self.object_to_recep[obj.object_id].startswith("floor_")
                ):
                    ax = obj.plot(
                        ax,
                        origin=(
                            offset,
                            actual_origin[1]
                            + self.room_height
                            * self.config.objects_height,
                        ),
                    )
                    offset += obj.width + spacing
                elif (
                    self.object_to_recep is not None
                    and obj.object_id in self.object_to_recep.keys()
                    and not self.object_to_recep[obj.object_id].startswith("floor_")
                ):
                    receptacle_id = self.object_to_recep[obj.object_id]
                    # print(obj.object_id, self.room_id, receptacle_id, self.object_to_recep)
                    current_receptacle = self.find_receptacle_by_id(
                        receptacle_id
                    )
                    obj_position = current_receptacle.next_top_item_position
                    ax = obj.plot(ax, obj_position)
                    current_receptacle.next_top_item_position = (
                        obj_position[0],
                        current_receptacle.next_top_item_position[1]
                        + abs(obj.config.text_margin)
                        + 2 * obj.config.height + obj.config.extra_space_between_objects,
                    )

    def plot_receptacles(self, ax, actual_origin):
        # Calculate initial offset considering left margin and horizontal padding
        receptacle_width = sum(recep.width for recep in self.receptacles)
        num_receptacles = len(self.receptacles)
        spacing = (
            (
                self.room_width
                - self.config.receptacle_horizontal_margin_fraction
                * 2
                * self.room_width
            )
            - receptacle_width
        ) / (num_receptacles + 1)
        offset = (
            actual_origin[0]
            + spacing
            + self.config.receptacle_horizontal_margin_fraction
            * self.room_width
        )
        for receptacle in self.receptacles:
            ax = receptacle.plot(
                ax, origin=(offset, actual_origin[1] + self.bottom_pad)
            )
            offset += receptacle.width + spacing

    def plot_text_label(self, ax, actual_origin):
        # Calculate text annotation position
        text_x = actual_origin[0] + self.room_width / 2
        text_y = (
            actual_origin[1] + self.bottom_pad / 4
        )  # Offset for lower v_pad region

        wrapped_text = wrap_text(self.room_id, self.config.max_chars_per_line)

        text_y = actual_origin[1] + self.bottom_pad / 4 * 1 / (
            wrapped_text.count("\n") + 1
        )
        ax.annotate(
            wrapped_text,
            xy=(text_x, text_y),
            xytext=(text_x, text_y),
            ha="center",
            va="bottom",
            fontsize=self.config.text_size,
            zorder=float('inf'),
        )

    def plot_placeholders(self, ax, actual_origin):
        self.center_position = (
            actual_origin[0] + self.width / 2,
            actual_origin[1]
            + (
                self.config.placeholder_height
                * self.room_height
            ),
        )
        if self.plot_placeholder:
            self.center_placeholder = Placeholder(self.config)
            center_placeholder_origin = (
                self.center_position[0] - self.config.placeholder.width / 2,
                self.center_position[1] - self.config.placeholder.height / 2,
            )
            ax = self.center_placeholder.plot(ax, center_placeholder_origin)

    def plot(self, origin=(0, 0), ax=None, target_width=None):
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        actual_origin = [
            origin[0] + self.config.horizontal_margin,
            origin[1] + self.config.vertical_margin,
        ]

        # Re-initialize widths
        self.init_widths()

        # Add extra horizontal padding if needed to match target width
        if target_width is None:
            extra_horizontal_pad = 0
        else:
            extra_horizontal_pad = max(
                0,
                (
                    target_width
                    - self.room_width
                    - 2 * self.config.horizontal_margin
                )
                / 2,
            )
        # Recalculate room widths and total width
        self.room_width = self.room_width + 2 * extra_horizontal_pad
        self.width = self.room_width + 2 * self.config.horizontal_margin

        self.plot_receptacles(ax, actual_origin)
        self.plot_text_label(ax, actual_origin)
        self.plot_objects(ax, actual_origin)

        # Plot the rectangle for the room
        if self.config.disable_in_proposition_room_border or not self.in_proposition:
            rect = ax.add_patch(
                plt.Rectangle(
                    (actual_origin[0], actual_origin[1]),
                    self.room_width,
                    self.room_height,
                    color=ROOM_COLOR,
                    alpha=self.config.box_alpha,
                )
            )
        else:
            border_width = self.config.border_width
            rect = ax.add_patch(
                plt.Rectangle(
                    (
                        actual_origin[0] + border_width,
                        actual_origin[1] + border_width,
                    ),
                    self.room_width - 2 * border_width,
                    self.room_height - 2 * border_width,
                    edgecolor="white",
                    linewidth=border_width,
                    facecolor=ROOM_COLOR,
                    alpha=self.config.box_alpha,
                )
            )
        # Set the z-order of the rectangle
        rect.set_zorder(-1)

        self.plot_placeholders(ax, actual_origin)

        if created_fig:
            ax.set_xlim(origin[0], origin[0] + self.width)
            ax.set_ylim(origin[1], origin[1] + self.height)
            ax.axis("off")
            return fig, ax
        else:
            return ax
