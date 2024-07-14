import matplotlib.pyplot as plt
from .constants import BACKGROUND_COLOR
from .legends.is_next_to_legend import IsNextToLegend
from .legends.same_args_legend import SameArgsLegend
from .legends.diff_args_legend import DiffArgsLegend
from .utils import wrap_text

class PrediViz:
    def __init__(self, config, scene):
        self.config = config
        self.scene = scene

    def plot_instruction(self, ax, scene_width, mx_width, mx_lower, mx_upper):
        wrapped_text = ""
        if self.scene.instruction:
            wrapped_text = wrap_text(
                self.scene.instruction, self.scene.config.max_chars_per_line
            )
            frac = 0.5 * (scene_width / mx_width)

            ax.text(
                frac,
                self.scene.config.instruction_relative_height * abs(mx_lower)/(mx_upper - mx_lower),
                wrapped_text,
                horizontalalignment="center",
                verticalalignment="bottom",
                transform=ax.transAxes,
                fontsize=self.scene.config.instruction_text_size,
                zorder=float('inf'),
            )
        return wrapped_text

    def get_is_next_tos(self, propositions, toposort):
        # Extract room names mentioned in propositions
        is_next_tos = []
        if toposort:
            for current_level in toposort:
                current_propositions = [
                    propositions[idx] for idx in current_level
                ]
                current_is_next_tos = []
                for prop in current_propositions:
                    if prop["function_name"] == "is_next_to":
                        current_is_next_tos += [
                            [
                                prop["args"]["entity_handles_a_names_and_types"],
                                prop["args"]["entity_handles_b_names_and_types"],
                                prop["args"]["number"],
                            ]
                        ]
                is_next_tos.append(current_is_next_tos)
        else:
            current_is_next_tos = []
            for prop in propositions:
                if prop["function_name"] == "is_next_to":
                    current_is_next_tos += [
                        [
                            prop["args"]["entity_handles_a_names_and_types"],
                            prop["args"]["entity_handles_b_names_and_types"],
                            prop["args"]["number"],
                        ]
                    ]
            is_next_tos.append(current_is_next_tos)
        return is_next_tos

    def plot(self,
        propositions,
        constraints,
        receptacle_icon_mapping,
        cropped_receptacle_icon_mapping,
        show_instruction=True,
        ):
        fig, ax = plt.subplots()
        fig.patch.set_facecolor(BACKGROUND_COLOR)

        toposort = []
        same_args_data = []
        diff_args_data = []
        for constraint in constraints:
            if constraint["type"] == "TemporalConstraint":
                toposort = constraint["toposort"]
            elif constraint["type"] == "SameArgConstraint":
                same_args_data.append(constraint["same_args_data"])
            elif constraint["type"] == "DifferentArgConstraint":
                diff_args_data.append(constraint["diff_args_data"])

        fig, ax, height_lower, height_upper, prop_to_height_range = self.scene.plot(
            propositions,
            toposort,
            ax
        )
        
        all_is_next_tos = self.get_is_next_tos(
            propositions, toposort
        )
        # Plot the legend
        self.legends = []
        self.legend_bounds = []
        if (
            all_is_next_tos or same_args_data or diff_args_data
        ):
            if all_is_next_tos:
                for level_idx, is_next_tos in enumerate(all_is_next_tos):
                    if is_next_tos:
                        self.legends.append(
                            IsNextToLegend(
                                self.scene.config.is_next_to, is_next_tos, cropped_receptacle_icon_mapping
                            )
                        )
                        current_height_lower, current_height_upper, offset = prop_to_height_range[level_idx]
                        self.legend_bounds.append((
                            current_height_lower, current_height_upper, offset
                        ))
            if same_args_data:
                self.legends.append(
                    SameArgsLegend(
                        self.scene.config.is_next_to, same_args_data, cropped_receptacle_icon_mapping
                    )
                )
                self.legend_bounds.append((
                    height_lower, height_upper, 0
                ))
            if diff_args_data:
                self.legends.append(
                    DiffArgsLegend(
                        self.scene.config.is_next_to, diff_args_data, cropped_receptacle_icon_mapping
                    )
                )
                self.legend_bounds.append((
                    height_lower, height_upper, 0
                ))
        range_to_num = {}
        range_to_current_height = {}
        range_to_consumed_space = {}

        # Precompute column assignments
        for legend, bound in zip(self.legends, self.legend_bounds):
            if bound not in range_to_num:
                range_to_num[bound] = 0
                range_to_consumed_space[bound] = 0
            range_to_num[bound] += 1
            range_to_current_height[bound] = 0
            range_to_consumed_space[bound] += legend.height + self.scene.config.is_next_to.bottom_pad + self.scene.config.is_next_to.top_pad

        # Compute necessary columns for each bound
        bounds_to_columns = {}
        for bound in range_to_consumed_space.keys():
            (current_height_lower, current_height_upper, offset) = bound
            available_space = (current_height_upper - current_height_lower)
            consumed_space = range_to_consumed_space[bound]
            
            # Calculate how many columns are needed
            if consumed_space > available_space:
                num_columns = (consumed_space // available_space) + 1
            else:
                num_columns = 1
            bounds_to_columns[bound] = num_columns

        # Distribute legends among the columns
        column_legend_lists = {bound: [[] for _ in range(bounds_to_columns[bound])] for bound in bounds_to_columns.keys()}
        column_heights = {bound: [0] * bounds_to_columns[bound] for bound in bounds_to_columns.keys()}

        for legend, bound in zip(self.legends, self.legend_bounds):
            num_columns = bounds_to_columns[bound]
            min_height_column = min(range(num_columns), key=lambda col: column_heights[bound][col])
            column_legend_lists[bound][min_height_column].append(legend)
            column_heights[bound][min_height_column] += legend.height + self.scene.config.is_next_to.bottom_pad + self.scene.config.is_next_to.top_pad

        # Plot legends
        mx_num_columns = 0
        mx_width = self.scene.width
        max_column_upper = height_upper
        min_column_lower = height_lower

        for bound in range_to_num.keys():
            num_columns = bounds_to_columns[bound]
            mx_num_columns = max(num_columns, mx_num_columns)
            column_width = self.scene.config.is_next_to.width
            (current_height_lower, current_height_upper, offset) = bound
            available_space = (current_height_upper - current_height_lower)

            for col in range(num_columns):
                current_height = column_heights[bound][col]
                num_spaces = len(column_legend_lists[bound][col]) + 1
                column_spacing = max(0, (available_space - current_height) / num_spaces)
                if current_height > available_space:
                    # Center align legends vertically
                    total_legend_height = column_heights[bound][col]
                    vertical_offset = (available_space - total_legend_height) / 2
                else:
                    vertical_offset = 0

                current_height = vertical_offset
                for legend in column_legend_lists[bound][col]:
                    legend_space = legend.height + self.scene.config.is_next_to.bottom_pad + self.scene.config.is_next_to.top_pad
                    legend_origin = - offset - current_height - legend_space - column_spacing
                    max_column_upper = max(max_column_upper, legend_origin + legend.height + legend.top_pad + legend.bottom_pad)
                    min_column_lower = min(min_column_lower, legend_origin)
                    legend_left = self.scene.width + col * (column_width + legend.horizontal_margin)
                    legend.plot((legend_left, legend_origin), ax)
                    mx_width = max(mx_width, legend_left + legend.width + legend.horizontal_margin)
                    current_height += legend_space + column_spacing

        if hasattr(self, "legends"):
            ax.set_xlim(0, mx_width)
            ax.set_ylim(min_column_lower, max_column_upper)
        else:
            mx_width = self.scene.width
            ax.set_xlim(0, self.scene.width)
            ax.set_ylim(height_lower, height_upper)
            
        # Add instruction on top
        if show_instruction:
            wrapped_text = self.plot_instruction(
                ax, self.scene.width, mx_width, min_column_lower, max_column_upper
            )
        num_instruction_lines = wrapped_text.count("\n")+1
        ax.axis('off')

        return fig, ax, num_instruction_lines
        
