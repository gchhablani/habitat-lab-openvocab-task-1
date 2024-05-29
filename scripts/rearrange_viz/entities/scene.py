import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrow
from .utils import wrap_text

class Scene:
    """
    Represents a scene consisting of multiple rooms and provides methods for plotting objects, receptacles, and relations between them.
    """

    def __init__(self, config, rooms, instruction=""):
        """
        Initializes a Scene instance.

        Parameters:
            config (object): A configuration object containing parameters for scene rendering.
            rooms (list): List of Room objects representing the rooms in the scene.
            instruction (str, optional): Instruction string used for sorting rooms based on relevance. Defaults to "".
        """
        self.config = config.scene
        self.instruction = instruction
        self.rooms = self.sort_rooms(rooms, instruction)

    def cleanup(self):
        if self.rooms:
            for room in self.rooms:
                room.cleanup()
                del room

    def sort_rooms(self, rooms, instruction):
        """
        Sorts rooms based on their relevance to an instruction.

        Parameters:
            rooms (list): List of Room objects representing the rooms to be sorted.
            instruction (str): Instruction string used for sorting rooms.

        Returns:
            list: List of Room objects sorted by relevance.
        """
        if not instruction:
            return rooms

        # Split instruction string into words and exclude "room"
        keywords = [word.lower().strip(".") for word in instruction.split()]

        # Create a dictionary to hold the rooms and their relevance score
        relevance_scores = {}

        for room in rooms:
            score = sum(
                " ".join(room.room_id.split("_")[:-1]) in keyword
                for keyword in keywords
            )

            # Consider receptacles in the score calculation
            for receptacle in room.receptacles:
                score += sum(
                    " ".join(receptacle.receptacle_id.split("_")[:-1])
                    in keyword
                    for keyword in keywords
                )

            # Consider objects in the score calculation
            if room.objects:
                for obj in room.objects:
                    score += sum(
                        " ".join(obj.object_id.split("_")[:-1]) in keyword
                        for keyword in keywords
                    )

            relevance_scores[room] = score

        # Sort the rooms based on relevance score
        sorted_rooms = sorted(
            relevance_scores.keys(),
            key=lambda room: relevance_scores[room],
            reverse=True,
        )

        return sorted_rooms

    def plot_object_to_receptacle_lines(
        self, object_names, receptacle_names, number, function_name, ax
    ):
        """
        Plots lines between objects and receptacles based on their relations.

        Parameters:
            object_names (list): List of object names.
            receptacle_names (list): List of receptacle names.
            function_name (str): Name of the relation function.
            ax (matplotlib.axes.Axes): Axes to plot the lines on.
        """
        for object_name in object_names:
            for room in self.rooms:
                object_obj = room.find_object_by_id(object_name)
                if object_obj:
                    for receptacle_name in receptacle_names:
                        receptacle_objs = []
                        for r_room in self.rooms:
                            receptacle_obj = r_room.find_receptacle_by_id(
                                receptacle_name
                            )
                            if receptacle_obj:
                                receptacle_objs.append(receptacle_obj)

                        for receptacle_obj in receptacle_objs:
                            if function_name == "is_inside":
                                if len(object_names) > number:
                                    line_style = (0, (5, 10))  # Dotted line for multiple objects
                                else:
                                    line_style = (
                                        "-"  # Solid line for single object
                                    )
                                self.add_arrow(
                                    ax,
                                    object_obj.center_position,
                                    receptacle_obj.center_placeholder_position,
                                    line_style,
                                )
                            elif function_name == "is_on_top":
                                if len(object_names) > number:
                                    line_style = (0, (5, 10))  # Dotted line for multiple objects
                                else:
                                    line_style = (
                                        "-"  # Solid line for single object
                                    )
                                self.add_arrow(
                                    ax,
                                    object_obj.center_position,
                                    receptacle_obj.top_placeholder_position,
                                    line_style,
                                )

    def plot_object_to_room_lines(self, object_names, room_names, number, ax):
        """
        Plots lines between objects and rooms based on their relations.

        Parameters:
            object_names (list): List of object names.
            room_names (list): List of room names.
            ax (matplotlib.axes.Axes): Axes to plot the lines on.
        """
        source_objects = []
        target_rooms = []
        for object_name in object_names:
            for room in self.rooms:
                object_obj = room.find_object_by_id(object_name)
                if object_obj:
                    source_objects.append(object_obj)
        for room_name in room_names:
            for r_room in self.rooms:
                if r_room.room_id == room_name:
                    target_rooms.append(r_room)
        for object_obj in source_objects:
            for room_obj in target_rooms:
                if len(object_names) > number:
                    line_style = (0, (5, 10))  # Dotted line for multiple objects
                else:
                    line_style = "-"  # Solid line for single object

                self.add_arrow(
                    ax,
                    object_obj.center_position,
                    room_obj.center_position,
                    line_style,
                )

    def add_arrow(self, ax, obj_loc, room_loc, line_style):
        """
        Adds an arrow to the given line.

        Parameters:
            ax (matplotlib.axes.Axes): Axes to add the arrow to.
            obj_loc (tuple): Location of the object.
            room_loc (tuple): Location of the room.
            line_style (str): Style of the line ('-' for solid, '--' for dashed).
        """
        
        arrow = FancyArrow(
            obj_loc[0],
            obj_loc[1],
            room_loc[0] - obj_loc[0],
            room_loc[1] - obj_loc[1],
            linestyle=line_style,
            head_length=self.config.arrow.head_length,
            head_width=self.config.arrow.head_width,
            # width=self.config.arrow.linewidth,
            linewidth=self.config.arrow.linewidth,
            length_includes_head=True,
            edgecolor=(1, 1, 1, 1),
            facecolor=(1, 1, 1, 0), # 0 alpha
            overhang=self.config.arrow.overhang,
        )
        ax.add_patch(arrow)

    def redistribute_target_width_to_rooms(self, rooms_to_plot, target_width):
        # Calculate total width of all rooms
        total_width = sum(room.width for room in rooms_to_plot)

        # Calculate redistribution factor based on target width and total width
        redistribution_factor = target_width / total_width

        # Redistribute width to each room based on their width ratios
        redistributed_widths = [
            room.width * redistribution_factor for room in rooms_to_plot
        ]

        return redistributed_widths

    def plot_rooms_linear(
        self,
        mentioned_rooms,
        ax,
        target_width=None,
        height_offset=0,
        all_mentioned_rooms=None,
    ):
        """
        Plots rooms linearly with names underneath.

        Parameters:
            mentioned_rooms (list): List of mentioned room names.
            ax (matplotlib.axes.Axes): Axes to plot the rooms on.

        Returns:
            matplotlib.axes.Axes: Modified axes.
        """

        if target_width is None:
            # Calculate starting position of the first row to center it relative to the second row
            first_row_position = 0
            for room in self.rooms:
                if room.room_id in mentioned_rooms:
                    ax = room.plot(position=(first_row_position, 0), ax=ax)
                    first_row_position += room.width

            # Calculate total scene width based on the widths of all rooms
            self.width = first_row_position
            # Calculate scene height
            first_row_height = max(
                room.height
                for room in self.rooms
                if room.room_id in mentioned_rooms
            )

            total_rooms = len(self.rooms)
            current_rooms_to_plot = []
            current_row_width = 0
            current_row_height = 0 + height_offset
            i = 0
            while i < total_rooms:
                room = self.rooms[i]
                if room.room_id not in mentioned_rooms:
                    if room.width + current_row_width <= self.width:
                        current_row_width += room.width
                        current_rooms_to_plot.append(room)
                    else:
                        max_room_height_for_row = max(
                            room.height for room in current_rooms_to_plot
                        )
                        rooms_have_objects = np.any(
                            [
                                room.objects is not None and room.objects != []
                                for room in current_rooms_to_plot
                            ]
                        )
                        current_row_height -= max_room_height_for_row
                        current_row_width = 0
                        for room in current_rooms_to_plot:
                            if rooms_have_objects:
                                room.use_full_height = True
                            else:
                                room.use_full_height = False
                            ax = room.plot(
                                position=(
                                    current_row_width,
                                    current_row_height,
                                ),
                                ax=ax,
                            )
                            current_row_width += room.width
                        current_row_width = 0
                        current_rooms_to_plot = []
                        continue
                i += 1

            current_row_height -= max(
                room.height for room in current_rooms_to_plot
            )
            current_row_width = 0
            for room in current_rooms_to_plot:
                ax = room.plot(
                    position=(current_row_width, current_row_height), ax=ax
                )
                current_row_width += room.width

            height_upper = first_row_height
            height_lower = current_row_height

            return ax, height_lower, height_upper

        else:
            self.width = target_width
            all_rooms = []
            if all_mentioned_rooms is None:
                all_mentioned_rooms = mentioned_rooms
            for room in self.rooms:
                if room.room_id in all_mentioned_rooms:
                    all_rooms.append(room)
            for room in self.rooms:
                if room.room_id not in all_mentioned_rooms:
                    all_rooms.append(room)
            # NOTE: This is needed to get back to original width after every call of this method
            for room in self.rooms:
                room.init_size()

            current_rooms_to_plot = []
            current_row_width = 0
            current_row_height = 0 + height_offset
            i = 0
            while i < len(all_rooms):
                room = all_rooms[i]
                if room.width + current_row_width <= self.width:
                    current_row_width += room.width
                    current_rooms_to_plot.append(room)
                else:
                    rooms_have_objects = np.any(
                        [
                            room.objects is not None and room.objects != []
                            for room in current_rooms_to_plot
                        ]
                    )
                    for room in current_rooms_to_plot:
                        if rooms_have_objects:
                            room.use_full_height = True
                            room.init_size()
                        else:
                            room.use_full_height = False
                            room.init_size()
                    current_row_height -= max(
                        room.height for room in current_rooms_to_plot
                    )
                    current_row_width = 0
                    room_target_widths = (
                        self.redistribute_target_width_to_rooms(
                            current_rooms_to_plot, target_width
                        )
                    )
                    for room, room_target_width in zip(
                        current_rooms_to_plot, room_target_widths
                    ):
                        ax = room.plot(
                            position=(current_row_width, current_row_height),
                            ax=ax,
                            target_width=room_target_width,
                        )
                        current_row_width += room.width
                    self.width = max(current_row_width, self.width)
                    current_row_width = 0
                    current_rooms_to_plot = []
                    continue
                i += 1

            rooms_have_objects = np.any(
                [
                    room.objects is not None and room.objects != []
                    for room in current_rooms_to_plot
                ]
            )
            for room in current_rooms_to_plot:
                if rooms_have_objects:
                    room.use_full_height = True
                    room.init_size()
                else:
                    room.use_full_height = False
                    room.init_size()
            current_row_height -= max(
                room.height for room in current_rooms_to_plot
            )
            current_row_width = 0
            room_target_widths = self.redistribute_target_width_to_rooms(
                current_rooms_to_plot, target_width
            )
            for room, room_target_width in zip(
                current_rooms_to_plot, room_target_widths
            ):
                ax = room.plot(
                    position=(current_row_width, current_row_height),
                    ax=ax,
                    target_width=room_target_width,
                )
                current_row_width += room.width
            self.width = max(current_row_width, self.width)

            height_upper = 0
            height_lower = current_row_height
            # self.height = self.height_upper - self.height_lower

            return ax, height_lower, height_upper

    def plot_for_propositions(
        self,
        propositions,
        show_instruction=True,
        height_offset=0,
        initial_ax=None,
        all_mentioned_rooms=None,
    ):
        # Extract room names mentioned in propositions
        mentioned_objs = []
        on_floor_objs = []
        mentioned_receps = []
        mentioned_rooms = []
        for prop in propositions:
            if prop["function_name"] in ["is_on_top", "is_inside"]:
                mentioned_objs += prop["args"]["object_names"]
                if prop["function_name"] == "is_on_top":
                    mentioned_receps += [
                        ("is_on_top", recep_name)
                        for recep_name in prop["args"]["receptacle_names"]
                    ]
                if prop["function_name"] == "is_inside":
                    mentioned_receps += [
                        ("is_inside", recep_name)
                        for recep_name in prop["args"]["receptacle_names"]
                    ]
            elif prop["function_name"] == "is_in_room":
                mentioned_objs += prop["args"]["object_names"]
                mentioned_rooms += prop["args"]["room_names"]
            elif prop["function_name"] == "is_on_floor":
                on_floor_objs += prop["args"]["object_names"]
            else:
                raise NotImplementedError(
                    f"Not implemented for function with name: {prop['function_name']}."
                )

        for room in self.rooms:
            if room.room_id in mentioned_rooms:
                room.plot_placeholder = True
            else:
                room.plot_placeholder = False

        for room in self.rooms:
            for receptacle in room.receptacles:
                receptacle.plot_top_placeholder = False
                receptacle.plot_center_placeholder = False
            for obj in room.objects:
                obj.is_on_floor = False

        for room in self.rooms:
            for obj in on_floor_objs:
                found_object = room.find_object_by_id(obj)
                if found_object:
                    found_object.is_on_floor = True
                    if room.room_id not in mentioned_rooms:
                        mentioned_rooms += [room.room_id]

            for obj in mentioned_objs:
                found_object = room.find_object_by_id(obj)
                if found_object:
                    if room.room_id not in mentioned_rooms:
                        mentioned_rooms += [room.room_id]
            for prop_function, recep in mentioned_receps:
                found_receptacle = room.find_receptacle_by_id(recep)
                if found_receptacle:
                    if room.room_id not in mentioned_rooms:
                        mentioned_rooms += [room.room_id]
                    if prop_function == "is_on_top":
                        found_receptacle.plot_top_placeholder = True
                    elif prop_function == "is_inside":
                        found_receptacle.plot_center_placeholder = True
                    else:
                        raise NotImplementedError(
                            f"Not implemented for prop fuction {prop_function}."
                        )

        for room in self.rooms:
            if room.room_id in mentioned_rooms:
                room.in_proposition = True
            else:
                room.in_proposition = False

        # Create a figure and axis for plotting the scene
        if initial_ax is None:
            fig, ax = plt.subplots()
            background_color = "#3E4C60"
            # Set the background color of the figure
            fig.patch.set_facecolor(background_color)
        else:
            ax = initial_ax

        ax, height_lower, height_upper = self.plot_rooms_linear(
            mentioned_rooms,
            ax,
            self.config.target_width,
            height_offset,
            all_mentioned_rooms,
        )

        # Plot lines between objects and receptacles based on propositions
        if propositions:
            for proposition in propositions:
                function_name = proposition["function_name"]
                args = proposition["args"]
                object_names = args["object_names"]
                number = args["number"]
                if function_name in ["is_inside", "is_on_top"]:
                    receptacle_names = args["receptacle_names"]
                    self.plot_object_to_receptacle_lines(
                        object_names, receptacle_names, number, function_name, ax
                    )
                elif function_name == "is_in_room":
                    room_names = args["room_names"]
                    self.plot_object_to_room_lines(
                        object_names, room_names, number, ax
                    )
                # else:
                #     raise NotImplementedError(f"Not implemented line plotting for {function_name}.")



        # Add instruction on top
        wrapped_text = ""
        if self.instruction and show_instruction:
            wrapped_text = wrap_text(self.instruction, self.config.max_chars_per_line)

            ax.text(
                0.5,
                self.config.instruction_relative_height,
                wrapped_text,
                horizontalalignment="center",
                verticalalignment="bottom",
                transform=ax.transAxes,
                fontsize=self.config.instruction_text_size,
            )

        # Set axis limits
        ax.set_xlim(0, self.width)
        ax.set_ylim(height_lower, height_upper)
        if initial_ax is None:
            return fig, ax, height_lower, height_upper, wrapped_text
        else:
            return ax, height_lower, height_upper, wrapped_text

    def plot(self, propositions=None, constraints=None, force_hide_instructions=None):
        """
        Plots the scene.

        Parameters:
            propositions (list, optional): List of propositions containing relations between objects, receptacles, and rooms. Defaults to None.

        Returns:
            matplotlib.figure.Figure, matplotlib.axes.Axes: Figure and axes of the plotted scene.
        """
        assert (
            constraints is not None
        ), "All propositions should have atleast `TerminalSatisfactionConstraint`. Found no constraints instead."
        assert (
            propositions is not None
        ), "Plotting without propositions is not supported."
        toposort = []
        for constraint in constraints:
            if constraint["type"] == "TemporalConstraint":
                toposort = constraint["toposort"]
        if toposort:
            
            # NOTE: All the next bits are only used to get a list of all the mentioned rooms to keep them in front!
            # We don't really care about using mentioned objects and receptacles after
            mentioned_objs = []
            mentioned_receps = []
            mentioned_rooms = []
            for prop in propositions:
                if prop["function_name"] in ["is_on_top", "is_inside"]:
                    mentioned_objs += prop["args"]["object_names"]
                    if prop["function_name"] == "is_on_top":
                        mentioned_receps += [
                            ("is_on_top", recep_name)
                            for recep_name in prop["args"]["receptacle_names"]
                        ]
                    if prop["function_name"] == "is_inside":
                        mentioned_receps += [
                            ("is_inside", recep_name)
                            for recep_name in prop["args"]["receptacle_names"]
                        ]
                elif prop["function_name"] == "is_in_room":
                    mentioned_objs += prop["args"]["object_names"]
                    mentioned_rooms += prop["args"]["room_names"]
                elif prop["function_name"] == "is_on_floor":
                    mentioned_objs += prop["args"]["object_names"]
                else:
                    raise NotImplementedError(
                        f"Not implemented for function with name: {prop['function_name']}."
                    )

            for room in self.rooms:
                for obj in mentioned_objs:
                    found_object = room.find_object_by_id(obj)
                    if found_object:
                        if room.room_id not in mentioned_rooms:
                            mentioned_rooms += [room.room_id]
                for prop_function, recep in mentioned_receps:
                    found_receptacle = room.find_receptacle_by_id(recep)
                    if found_receptacle:
                        if room.room_id not in mentioned_rooms:
                            mentioned_rooms += [room.room_id]

            all_mentioned_rooms = sorted(mentioned_rooms)

            max_upper = 0
            min_lower = 0
            fig, ax = plt.subplots()
            background_color = "#3E4C60"
            # Set the background color of the figure
            fig.patch.set_facecolor(background_color)
            num_instruction_lines = 0
            for level_idx, current_level in enumerate(toposort):
                if level_idx == 0 and not force_hide_instructions:
                    show_instruction = True
                else:
                    show_instruction = False
                current_propositions = [
                    propositions[idx] for idx in current_level
                ]
                ax, height_lower, height_upper, wrapped_text = self.plot_for_propositions(
                    current_propositions,
                    show_instruction=show_instruction,
                    height_offset=min_lower,
                    initial_ax=ax,
                    all_mentioned_rooms=all_mentioned_rooms,
                )
                # Plot horizontal line
                ax.axhline(
                    y=height_lower - 20,
                    color="white",
                    linewidth=4,
                    linestyle="-",
                )
                num_instruction_lines = max(num_instruction_lines, wrapped_text.count("\n")+1)
                max_upper = max(height_upper, max_upper)
                min_lower = min(height_lower - 40, min_lower)
            self.height = max_upper - min_lower
            return fig, ax, num_instruction_lines
        else:
            num_instruction_lines = 0
            fig, ax, height_lower, height_upper, wrapped_text = self.plot_for_propositions(
                propositions, show_instruction=not force_hide_instructions,
            )
            self.height = height_upper - height_lower
            num_instruction_lines = max(num_instruction_lines, wrapped_text.count("\n")+1)
            return fig, ax, num_instruction_lines


# TODO:
# Think about using the initial object-receptacle mapping if needed
# Get missing assets - shower,
