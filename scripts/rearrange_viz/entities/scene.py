import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrow, PathPatch
from matplotlib.path import Path

from .legends.is_next_to_legend import IsNextToLegend
from .legends.same_args_legend import SameArgsLegend
from .utils import wrap_text, sort_rooms, redistribute_target_width_to_rooms
from .constants import color_palette, BACKGROUND_COLOR


class Scene:
    def __init__(self, config, rooms, instruction=""):
        self.config = config.scene
        self.instruction = instruction
        self.rooms = sort_rooms(rooms, instruction)

    def cleanup(self):
        if self.rooms:
            for room in self.rooms:
                room.cleanup()
                del room

    def plot_object_to_receptacle_lines(
        self,
        object_names,
        receptacle_names,
        number,
        function_name,
        ax,
        color=None,
        modify_object_color=False,
    ):
        for object_name in object_names:
            for room in self.rooms:
                object_obj = room.find_object_by_id(object_name)
                if object_obj:
                    if modify_object_color:
                        object_obj.change_rectangle_color(color)
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
                                arrow_dest_position = receptacle_obj.center_placeholder_position
                            else:
                                arrow_dest_position = receptacle_obj.top_placeholder_position
                            
                            if len(object_names) > number:
                                line_style = (
                                    0,
                                    (5, 10),
                                )  # Dotted line for multiple objects
                            else:
                                line_style = (
                                    "-"  # Solid line for single object
                                )
                            self.add_arrow(
                                ax,
                                object_obj.center_position,
                                arrow_dest_position,
                                line_style,
                                curved=True,
                                color=color,
                            )

    def plot_object_to_room_lines(
        self, object_names, room_names, number, ax, color=None, modify_object_color=False,
    ):
        source_objects = []
        target_rooms = []
        for object_name in object_names:
            for room in self.rooms:
                object_obj = room.find_object_by_id(object_name)
                if object_obj:
                    if modify_object_color:
                        object_obj.change_rectangle_color(color)
                    source_objects.append(object_obj)
        for room_name in room_names:
            for r_room in self.rooms:
                if r_room.room_id == room_name:
                    target_rooms.append(r_room)
        for object_obj in source_objects:
            for room_obj in target_rooms:
                if len(object_names) > number:
                    line_style = (
                        0,
                        (5, 10),
                    )  # Dotted line for multiple objects
                else:
                    line_style = "-"  # Solid line for single object

                self.add_arrow(
                    ax,
                    object_obj.center_position,
                    room_obj.center_position,
                    line_style,
                    curved=True,
                    color=color,
                )

    def add_arrow(
        self,
        ax,
        obj_loc,
        room_loc,
        line_style,
        curved=True,
        color=(1, 1, 1, 1),
    ):
        x0, y0 = obj_loc
        x1, y1 = room_loc
        dx, dy = x1 - x0, y1 - y0

        if curved:
            # Calculate control points for the Bézier curve
            ctrl_x = (x0 + x1) / 2 + dy / 2
            ctrl_y = (y0 + y1) / 2 + abs(dx) / 2  # Curve upwards

            # Define path for the curved arrow
            path_data = [
                (Path.MOVETO, (x0, y0)),
                (Path.CURVE3, (ctrl_x, ctrl_y)),
                (Path.CURVE3, (x1, y1)),
            ]
            codes, verts = zip(*path_data)
            path = Path(verts, codes)
            patch = PathPatch(
                path,
                linestyle=line_style,
                linewidth=self.config.arrow.linewidth,
                facecolor="none",
                edgecolor=color,
            )
            ax.add_patch(patch)

            # Calculate the derivative (tangent) at the end point of the Bézier curve
            t = 1  # At the end point
            dx_dt = 2 * (1 - t) * (ctrl_x - x0) + 2 * t * (x1 - ctrl_x)
            dy_dt = 2 * (1 - t) * (ctrl_y - y0) + 2 * t * (y1 - ctrl_y)
            arrow_dir = np.array([dx_dt, dy_dt])
            arrow_dir /= np.linalg.norm(
                arrow_dir
            )  # Normalize the direction vector

            # Calculate the position for the arrowhead
            head_pos = (
                np.array([x1, y1]) - arrow_dir * self.config.arrow.head_length
            )

            # Add arrowhead
            arrow_head = FancyArrow(
                head_pos[0],
                head_pos[1],
                arrow_dir[0] * self.config.arrow.head_length,
                arrow_dir[1] * self.config.arrow.head_length,
                head_length=self.config.arrow.head_length,
                head_width=self.config.arrow.head_width,
                linewidth=self.config.arrow.linewidth,
                edgecolor=color,
                facecolor=color,
                length_includes_head=True,
                overhang=self.config.arrow.overhang,
            )
            ax.add_patch(arrow_head)

        else:
            arrow = FancyArrow(
                x0,
                y0,
                dx,
                dy,
                linestyle=line_style,
                head_length=self.config.arrow.head_length,
                head_width=self.config.arrow.head_width,
                linewidth=self.config.arrow.linewidth,
                length_includes_head=True,
                edgecolor=color,
                facecolor=color,
                overhang=self.config.arrow.overhang,
            )
            ax.add_patch(arrow)

    def plot_a_row_of_rooms(self, ax, current_rooms_to_plot, target_width, current_row_height):
        current_row_height -= max(
            room.height for room in current_rooms_to_plot
        )
        # Set max room height for all rooms
        max_room_height = max(room.room_height for room in current_rooms_to_plot)
        max_height = max(room.height for room in current_rooms_to_plot)
        for room in current_rooms_to_plot:
            room.height = max_height
            room.room_height = max_room_height
        current_row_width = 0
        room_target_widths = (
            redistribute_target_width_to_rooms(
                current_rooms_to_plot, target_width
            )
        )
        for room, room_target_width in zip(
            current_rooms_to_plot, room_target_widths
        ):
            ax = room.plot(
                origin=(current_row_width, current_row_height),
                ax=ax,
                target_width=room_target_width,
            )
            current_row_width += room.width
        
        self.width = max(current_row_width, self.width)
        return current_row_width, current_row_height

    def plot_room_rows(
        self,
        mentioned_rooms,
        ax,
        target_width,
        height_offset=0,
        all_mentioned_rooms=None,
    ):

        self.width = target_width
        all_rooms = []
        if all_mentioned_rooms is None:
            all_mentioned_rooms = mentioned_rooms
        # Keep mentioned rooms first
        for room in self.rooms:
            if room.room_id in all_mentioned_rooms:
                all_rooms.append(room)
        # Then keep non-mentioned rooms
        for room in self.rooms:
            if room.room_id not in all_mentioned_rooms:
                all_rooms.append(room)

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
                current_row_width, current_row_height = self.plot_a_row_of_rooms(
                    ax, current_rooms_to_plot, target_width, current_row_height
                )
                current_row_width = 0
                current_rooms_to_plot = []
                continue
            i += 1

        current_row_width, current_row_height = self.plot_a_row_of_rooms(
            ax, current_rooms_to_plot, target_width, current_row_height
        )

        height_upper = 0
        height_lower = current_row_height

        return ax, height_lower, height_upper

    def extract_info_before_plot(self, propositions):
        # Extract room names mentioned in propositions
        mentioned_objs = []
        on_floor_objs = []
        mentioned_receps = []
        mentioned_rooms = []
        is_next_tos = []
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
            elif prop["function_name"] == "is_next_to":
                is_next_tos += [
                    [
                        prop["args"]["entity_handles_a_names_and_types"],
                        prop["args"]["entity_handles_b_names_and_types"],
                        prop["args"]["number"],
                    ]
                ]
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
        return mentioned_rooms, is_next_tos

    def plot_proposition_lines(self, ax, propositions):
        color_index = 0
        for proposition in propositions:
            function_name = proposition["function_name"]
            args = proposition["args"]
            if "object_names" in args:
                object_names = args["object_names"]
                number = args["number"]

                # Cycle through the color palette for each proposition
                color = list(color_palette.values())[
                    color_index % len(color_palette)
                ]
                color_index += 1
                if function_name in ["is_inside", "is_on_top"]:
                    receptacle_names = args["receptacle_names"]
                    self.plot_object_to_receptacle_lines(
                        object_names,
                        receptacle_names,
                        number,
                        function_name,
                        ax,
                        color,
                        modify_object_color=True
                    )
                elif function_name == "is_in_room":
                    room_names = args["room_names"]
                    self.plot_object_to_room_lines(
                        object_names,
                        room_names,
                        number,
                        ax,
                        color,
                        modify_object_color=True
                    )

    def plot_instruction(self, ax, legend_column=False):
        if self.instruction:
            wrapped_text = wrap_text(
                self.instruction, self.config.max_chars_per_line
            )
            if legend_column:
                frac = 0.5 * (self.width + 600) /(self.width + 300 + self.config.is_next_to.width + 300 + 300)
            else:
                frac = 0.5

            ax.text(
                frac,
                self.config.instruction_relative_height,
                wrapped_text,
                horizontalalignment="center",
                verticalalignment="bottom",
                transform=ax.transAxes,
                fontsize=self.config.instruction_text_size,
                zorder=float('inf'),
            )

    def plot_one_time_step(
        self,
        ax,
        propositions,
        receptacle_icon_mapping,
        same_args_data,
        show_instruction=True,
        height_offset=0,
        all_mentioned_rooms=None,
    ):
        
        (
            mentioned_rooms,
            is_next_tos
        ) = self.extract_info_before_plot(propositions)

        ax, height_lower, height_upper = self.plot_room_rows(
            mentioned_rooms,
            ax,
            self.config.target_width,
            height_offset,
            all_mentioned_rooms,
        )

        self.plot_proposition_lines(ax, propositions)

        # Plot the legend
        if is_next_tos or same_args_data:
            if is_next_tos:
                self.legend = IsNextToLegend(
                    self.config.is_next_to, is_next_tos, receptacle_icon_mapping
                )
                self.legend.plot(
                    (
                        self.width,
                        (height_lower + height_upper) / 2
                        - self.config.is_next_to.height / 2,
                    ),
                    ax,
                )
            if same_args_data:
                self.same_args_legend = SameArgsLegend(
                    self.config.is_next_to, same_args_data, receptacle_icon_mapping
                )
                self.same_args_legend.plot(
                    (
                        self.width,
                        (height_lower + height_upper) / 2
                        + self.config.is_next_to.height / 2,
                    ),
                    ax,
                )
            if hasattr(self, "legend") or hasattr(self, "same_args_legend"):
                width = self.legend.width if hasattr(self, "legend") else self.same_args_legend.width  
                ax.set_xlim(0, self.width + 300 + width + 300)

        # Set axis limits
        else:
            ax.set_xlim(0, self.width)
        ax.set_ylim(height_lower, height_upper)

        # Add instruction on top
        wrapped_text = ""
        if show_instruction:
            self.plot_instruction(
                ax, legend_column=is_next_tos or same_args_data
            )

        return ax, height_lower, height_upper, wrapped_text

    def get_all_mentioned_rooms(self, propositions):
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
            elif prop["function_name"] == "is_next_to":
                continue
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
        return all_mentioned_rooms

    def plot(
        self,
        receptacle_icon_mapping,
        propositions,
        constraints,
    ):
        fig, ax = plt.subplots()
        fig.patch.set_facecolor(BACKGROUND_COLOR)

        toposort = []
        all_same_args = []
        for constraint in constraints:
            if constraint["type"] == "TemporalConstraint":
                toposort = constraint["toposort"]
            elif constraint["type"] == "SameArgConstraint":
                all_same_args.append(constraint["same_args_data"])

        if toposort:
            all_mentioned_rooms = self.get_all_mentioned_rooms(propositions)
            max_upper = 0
            min_lower = 0
            num_instruction_lines = 0
            for level_idx, current_level in enumerate(toposort):
                show_instruction = level_idx == 0
                current_propositions = [
                    propositions[idx] for idx in current_level
                ]
                ax, height_lower, height_upper, wrapped_text = (
                    self.plot_one_time_step(
                        ax,
                        current_propositions,
                        receptacle_icon_mapping=receptacle_icon_mapping,
                        same_args_data=all_same_args,
                        show_instruction=show_instruction,
                        height_offset=min_lower,
                        all_mentioned_rooms=all_mentioned_rooms,
                    )
                )
                # Plot horizontal line
                ax.hlines(
                    xmin=0, 
                    xmax=self.width,
                    y=height_lower - 20,
                    color="white",
                    linewidth=4,
                    linestyle="-",
                )
                num_instruction_lines = max(
                    num_instruction_lines, wrapped_text.count("\n") + 1
                )
                max_upper = max(height_upper, max_upper)
                min_lower = min(height_lower - 40, min_lower)
            self.height = max_upper - min_lower
            return fig, ax, num_instruction_lines
        else:
            num_instruction_lines = 0
            ax, height_lower, height_upper, wrapped_text = (
                self.plot_one_time_step(
                    ax,
                    propositions,
                    receptacle_icon_mapping=receptacle_icon_mapping,
                    same_args_data=all_same_args,
                    show_instruction=True,
                )
            )
            self.height = height_upper - height_lower
            num_instruction_lines = max(
                num_instruction_lines, wrapped_text.count("\n") + 1
            )
            return fig, ax, num_instruction_lines
