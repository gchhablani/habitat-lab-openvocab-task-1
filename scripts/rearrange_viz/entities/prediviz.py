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

    def plot_instruction(self, ax, legend_column=False):
        wrapped_text = ""
        if self.scene.instruction:
            wrapped_text = wrap_text(
                self.scene.instruction, self.scene.config.max_chars_per_line
            )
            if legend_column:
                frac = 0.5 * (self.scene.width + 600) /(self.scene.width + 300 + self.scene.config.is_next_to.width + 300 + 300)
            else:
                frac = 0.5

            ax.text(
                frac,
                self.scene.config.instruction_relative_height,
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
        show_instruction=True,
        ):
        fig, ax = plt.subplots()
        fig.patch.set_facecolor(BACKGROUND_COLOR)

        toposort = []
        same_args_data = []
        diff_args_data = []
        legends = False
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
        column = False
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
                                self.scene.config.is_next_to, is_next_tos, receptacle_icon_mapping
                            )
                        )
                        current_height_lower, current_height_upper, offset = prop_to_height_range[level_idx]
                        self.legend_bounds.append((
                            current_height_lower, current_height_upper, offset
                        ))
                        column = True
            if same_args_data:
                self.legends.append(
                    SameArgsLegend(
                        self.scene.config.is_next_to, same_args_data, receptacle_icon_mapping
                    )
                )
                self.legend_bounds.append((
                    height_lower, height_upper, 0
                ))
                column = True
            if diff_args_data:
                self.legends.append(
                    DiffArgsLegend(
                        self.scene.config.is_next_to, diff_args_data, receptacle_icon_mapping
                    )
                )
                self.legend_bounds.append((
                    height_lower, height_upper, 0
                ))
                column = True

            range_to_num = {}
            range_to_current_height = {}
            range_to_consumed_space = {}
            for legend, bound in zip(self.legends, self.legend_bounds):
                if bound not in range_to_num:
                    range_to_num[bound] = 0
                    range_to_consumed_space[bound] = 0
                range_to_num[bound] += 1
                range_to_current_height[bound] = 0
                range_to_consumed_space[bound] += legend.height  + self.scene.config.is_next_to.bottom_pad + self.scene.config.is_next_to.top_pad
            
            for legend, bound in zip(self.legends, self.legend_bounds):
                (current_height_lower, current_height_upper, offset) = bound

                available_space = (current_height_upper - current_height_lower)
                consumed_space = range_to_consumed_space[bound]
                num_spaces = range_to_num[bound] + 1

                spacing = (available_space - consumed_space) / num_spaces
                legend_space = legend.height + self.scene.config.is_next_to.bottom_pad + self.scene.config.is_next_to.top_pad
                legend_origin = - offset - range_to_current_height[bound] - spacing - legend_space
                legend.plot((self.scene.width, legend_origin), ax)
                range_to_current_height[bound] += legend_space + spacing
            if hasattr(self, "legends"):
                width = self.legends[-1].width
                ax.set_xlim(0, self.scene.width + 300 + width + 300)
        else:
            ax.set_xlim(0, self.scene.width)
        ax.set_ylim(height_lower, height_upper)
    
        # Add instruction on top
        wrapped_text = ""
        if show_instruction:
            wrapped_text = self.plot_instruction(
                ax, legend_column=column
            )
        num_instruction_lines = wrapped_text.count("\n") + 1

        ax.axis('off')

        return fig, ax, num_instruction_lines
        
