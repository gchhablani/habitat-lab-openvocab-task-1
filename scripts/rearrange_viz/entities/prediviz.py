import matplotlib.pyplot as plt
from .constants import BACKGROUND_COLOR
from .legends.is_next_to_legend import IsNextToLegend
from .legends.same_args_legend import SameArgsLegend
from .utils import wrap_text

class PrediViz:
    def __init__(self, config, scene):
        self.config = config
        self.scene = scene

    def plot_instruction(self, ax, legend_column=False):
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
        for constraint in constraints:
            if constraint["type"] == "TemporalConstraint":
                toposort = constraint["toposort"]
            elif constraint["type"] == "SameArgConstraint":
                same_args_data.append(constraint["same_args_data"])

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
        if all_is_next_tos or same_args_data:
            if all_is_next_tos:
                self.legends = []
                for level_idx, is_next_tos in enumerate(all_is_next_tos):
                    if is_next_tos:
                        self.legends.append(
                            IsNextToLegend(
                                self.scene.config.is_next_to, is_next_tos, receptacle_icon_mapping
                            )
                        )
                        print(level_idx)
                        current_height_lower, current_height_upper, offset = prop_to_height_range[level_idx]
                        self.legends[-1].plot(
                            (
                                self.scene.width,
                                - (current_height_upper - current_height_lower) / 2
                                - offset
                                - self.legends[-1].height / 2
                                - self.scene.config.is_next_to.bottom_pad,
                            ),
                            ax,
                        )
                        column = True
            if same_args_data:
                self.same_args_legend = SameArgsLegend(
                    self.scene.config.is_next_to, same_args_data, receptacle_icon_mapping
                )
                self.same_args_legend.plot(
                    (
                        self.scene.width,
                        (height_lower + height_upper) / 2
                        + self.scene.config.is_next_to.height / 2,
                    ),
                    ax,
                )
                column = True
            if hasattr(self, "legends") or hasattr(self, "same_args_legend"):
                width = self.legends[-1].width if hasattr(self, "legends") else self.same_args_legend.width  
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
        
