import matplotlib.pyplot as plt

from .placeholder import Placeholder
from .utils import wrap_text


class Room:
    """
    Represents a room in a 2D space and provides methods for plotting it.
    """

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
        """
        Initializes a Room instance.

        Parameters:
            config (object): A configuration object containing parameters for room rendering.
            room_id (str): Identifier for the room.
            receptacles (list): List of receptacles in the room.
            objects (list, optional): List of objects in the room. Defaults to None.
            use_full_height (bool, optional): Indicates if the room should use full_height. Defaults to False.
        """
        self.config = config.room
        self.room_id = room_id
        self.receptacles = receptacles
        self.objects = objects
        self.in_proposition = in_proposition
        self.plot_placeholder = False
        self.object_to_recep = object_to_recep

        if self.objects:
            self.use_full_height = True
        else:
            self.use_full_height = use_full_height

        self.init_size()

    def init_size(self):
        """
        Initializes the size of the room based on its receptacles and objects.
        """
        min_width = self.config.min_width
        if self.objects:
            object_widths = 0
            for object in self.objects:
                object_widths += object.width

            min_width = max(
                min_width, object_widths * self.config.min_width_per_object
            )
        total_receptacle_width = max(
            min_width, sum(receptacle.width for receptacle in self.receptacles)
        )
        self.room_width = (
            total_receptacle_width
            + self.config.left_pad
            + self.config.right_pad
        )
        self.width = self.room_width + 2 * self.config.horizontal_margin

        self.room_height = (
            (
                self.config.full_height
                if self.use_full_height
                else self.config.half_height
            )
            + self.config.bottom_pad
            + self.config.top_pad
        )
        self.height = self.room_height + 2 * self.config.vertical_margin

    def cleanup(self):
        """Cleanup objects and receptacles."""
        if self.objects:
            for obj in self.objects:
                del obj
            self.objects.clear()
        if self.receptacles:
            for recep in self.receptacles:
                del recep
            self.receptacles.clear()

    def find_object_by_id(self, object_id):
        """
        Find an object by its ID.

        Args:
            object_id (str): The ID of the object to find.

        Returns:
            Object or None: The object if found, otherwise None.
        """
        if self.objects:
            for obj in self.objects:
                if obj.object_id == object_id:
                    return obj
        return None

    def find_receptacle_by_id(self, receptacle_id):
        """
        Find a receptacle by its ID.

        Args:
            receptacle_id (str): The ID of the receptacle to find.

        Returns:
            Receptacle or None: The receptacle if found, otherwise None.
        """
        for receptacle in self.receptacles:
            if receptacle.receptacle_id == receptacle_id:
                return receptacle
        return None

    def plot(self, position=(0, 0), ax=None, target_width=None):
        """
        Plots the room on a matplotlib Axes.

        Parameters:
            position (tuple, optional): Position of the room's bottom-left corner. Defaults to (0, 0).
            ax (matplotlib.axes.Axes, optional): Axes to plot the room on.
                                                 If None, a new figure and Axes will be created.
                                                 Defaults to None.

        Returns:
            matplotlib.figure.Figure, matplotlib.axes.Axes or matplotlib.axes.Axes: If ax is None,
            returns the created figure and axes. Otherwise, returns the modified axes.
        """
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        new_position = [
            position[0] + self.config.horizontal_margin,
            position[1] + self.config.vertical_margin,
        ]

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

        self.room_width = self.room_width + 2 * extra_horizontal_pad

        # Calculate initial offset considering left margin and horizontal padding

        new_receptacle_width = sum(recep.width for recep in self.receptacles)
        num_receptacles = len(self.receptacles)
        spacing = (
            (
                self.room_width
                - self.config.receptacle_horizontal_margin_fraction
                * 2
                * self.room_width
            )
            - new_receptacle_width
        ) / (num_receptacles + 1)
        offset = (
            new_position[0]
            + spacing
            + self.config.receptacle_horizontal_margin_fraction
            * self.room_width
        )
        for receptacle in self.receptacles:
            ax = receptacle.plot(
                ax, position=(offset, new_position[1] + self.config.bottom_pad)
            )
            offset += receptacle.width + spacing

        self.width = self.room_width + 2 * self.config.horizontal_margin

        # Calculate text annotation position
        text_x = new_position[0] + self.room_width / 2
        text_y = (
            new_position[1] + self.config.bottom_pad / 4
        )  # Offset for lower v_pad region

        wrapped_text = wrap_text(self.room_id, self.config.max_chars_per_line)

        text_y = new_position[1] + self.config.bottom_pad / 4 * 1 / (
            wrapped_text.count("\n") + 1
        )
        ax.annotate(
            wrapped_text,
            xy=(text_x, text_y),
            xytext=(text_x, text_y),
            ha="center",
            va="bottom",
            fontsize=self.config.text_size,
        )

        self.room_height = (
            self.config.full_height
            + self.config.bottom_pad
            + self.config.top_pad
        )
        if self.objects:
            # Handle non mapped objects
            # Calculate initial offset for objects considering left margin, horizontal padding, and spacing objects evenly
            total_object_width = 0
            num_objects = 0
            for obj in self.objects:
                if (
                    self.object_to_recep is None
                    or obj.object_id not in self.object_to_recep.keys()
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
                new_position[0]
                + self.config.object_horizontal_margin_fraction
                * self.room_width
                + spacing
            )

            for obj in self.objects:
                if (
                    self.object_to_recep is None
                    or obj.object_id not in self.object_to_recep.keys()
                ):
                    ax = obj.plot(
                        ax,
                        position=(
                            offset,
                            new_position[1]
                            + self.config.bottom_pad
                            + self.config.full_height
                            * self.config.objects_height,
                        ),
                    )
                    offset += obj.width + spacing
                elif (
                    self.object_to_recep is not None
                    and obj.object_id in self.object_to_recep.keys()
                ):
                    receptacle_id = self.object_to_recep[obj.object_id]
                    current_receptacle = self.find_receptacle_by_id(
                        receptacle_id
                    )
                    obj_position = current_receptacle.new_top_item_position
                    ax = obj.plot(ax, obj_position)
                    current_receptacle.new_top_item_position = (
                        obj_position[0],
                        obj.text_position[1] + obj.config.height,
                    )

        else:
            if not self.use_full_height:
                self.room_height = (
                    self.config.half_height
                    + self.config.bottom_pad
                    + self.config.top_pad
                )
            self.height = self.room_height + 2 * self.config.vertical_margin

        self.center_position = (
            new_position[0] + self.room_width / 2,
            new_position[1]
            + self.config.bottom_pad
            + (
                self.config.placeholder_height_if_full
                * self.config.full_height
                if self.use_full_height
                else self.config.placeholder_height_if_half
                * self.config.half_height
            ),
        )

        if not self.in_proposition:
            rect = ax.add_patch(
                plt.Rectangle(
                    (new_position[0], new_position[1]),
                    self.room_width,
                    self.room_height,
                    color="#5A6F8E",
                    alpha=self.config.box_alpha,
                )
            )
        else:
            border_width = self.config.border_width
            rect = ax.add_patch(
                plt.Rectangle(
                    (
                        new_position[0] + border_width,
                        new_position[1] + border_width,
                    ),
                    self.room_width - 2 * border_width,
                    self.room_height - 2 * border_width,
                    edgecolor="white",
                    linewidth=border_width,
                    facecolor="#5A6F8E",
                    alpha=self.config.box_alpha,
                )
            )
        # Set the z-order of the rectangle
        rect.set_zorder(-1)

        if self.plot_placeholder:
            self.center_placeholder = Placeholder(self.config)
            center_placeholder_origin = (
                self.center_position[0] - self.config.placeholder.width / 2,
                self.center_position[1] - self.config.placeholder.height / 2,
            )
            ax = self.center_placeholder.plot(ax, center_placeholder_origin)

        ax.set_xlim(position[0], position[0] + self.width)
        ax.set_ylim(position[1], position[1] + self.height)
        ax.axis("off")

        if created_fig:
            return fig, ax
        else:
            return ax
