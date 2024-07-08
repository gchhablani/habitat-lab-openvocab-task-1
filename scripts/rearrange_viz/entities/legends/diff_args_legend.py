from matplotlib.patches import FancyBboxPatch
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from ..object import Object
from ..constants import LEGEND_BACKGROUND_COLOR
from ..receptacle import Receptacle
from ..tiny_room import TinyRoom

class DiffArgsLegend:
    def __init__(self, config, diff_args, receptacle_icon_mapping):
        self.title = "diff as"
        self.config = config
        # diff_args is a list of lists
        # each inner list is a list of tuples
        # the first item in each tuple is supposed to be the "same" element
        # the second item in each tuple is the thing to be on the other side
        # each item has its type described in the tuple
        self.diff_args = diff_args
        self.receptacle_icon_mapping = receptacle_icon_mapping
        self.set_graph_and_bipartite_sets()
        self.set_height()

    @property
    def width(self):
        return self.config.width

    def set_graph_and_bipartite_sets(self):
        self.G = nx.Graph()
        for diff_args_data in self.diff_args:
            left_elements = set()
            right_elements = set()
            for tup in diff_args_data:
                left_elements = left_elements.union(set(tup[0]))
                right_elements = right_elements.union(set(tup[1]))

            left_elements = list(left_elements)
            right_elements = list(right_elements)
            for tup_idx, tup in enumerate(diff_args_data):   
                left_element = left_elements[tup_idx]
                right_element = right_elements[tup_idx]
                while left_element == right_element:
                    right_element = right_elements[np.random.choice(len(right_elements))]
                if not self.G.has_node(left_element):
                    self.G.add_node(left_element[0], entity=left_element, bipartite=0)
                if not self.G.has_node(right_element):
                    self.G.add_node(right_element[0], entity=right_element, bipartite=1)
                self.G.add_edge(left_element[0], right_element[0])
        left_set = set()
        right_set = set()
        # Get the two sets of nodes
        for idx, (label, data) in enumerate(self.G.nodes(data=True)):
            if data["bipartite"] == 1:
                left_set = left_set.union({label})
            else:
                right_set = right_set.union({label})
        self.left_set = left_set
        self.right_set = right_set

    def set_height(self):
        self.height = max(
            (len(self.left_set) + 1) * 2 + len(self.left_set),
            (len(self.right_set) + 1) * 2 + len(self.right_set)
        ) * self.config.object.height
    
    def plot_entity_column(
        self, ax, entity_set, midpoint, current_height, spacing
    ):
        entities = {}
        for idx, node in enumerate(entity_set):
            entity_id, entity_type = self.G.nodes[node]['entity']
            if entity_type == "object":
                entity = Object(self.config, entity_id)
                origin = (
                    midpoint - self.config.object.width / 2,
                    current_height - self.config.object.height / 2,
                )
            elif entity_type == "receptacle":
                icon_path = self.receptacle_icon_mapping.get(
                    entity_id, "receptacles/chair@2x.png"
                )
                entity = Receptacle(
                    self.config, entity_id, icon_path
                )
                origin = (
                    midpoint - entity.width / 2,
                    current_height - entity.height / 2,
                )
            else:
                entity = TinyRoom(
                    self.config, entity_id
                )
                origin = (
                    midpoint - entity.width / 2,
                    current_height - entity.height / 2,
                )
            entities[f"{entity_id}"] = entity
            entity.plot(
                ax,
                origin,
            )
            current_height -= spacing
        return entities

    def plot_lines(self, ax, left_entities, right_entities):
        for edge in self.G.edges():
            node1, node2 = edge
            line_style='solid'
            if node1 in left_entities:
                first_entity = left_entities[node1]
            elif node1 in right_entities:
                first_entity = right_entities[node1]
            else:
                raise RuntimeError(f"node1: {node1} not in left or right entities")
            if node2 in left_entities:
                second_entity = left_entities[node2]
            elif node2 in right_entities:
                second_entity = right_entities[node2]
            else:
                raise RuntimeError(f"node2: {node2} not in left or right entities")
            first_center = (
                first_entity.center_position
                if isinstance(first_entity, Object)
                else first_entity.center_placeholder_position
                if isinstance(first_entity, Receptacle)
                else first_entity.center_position
            )
            second_center = (
                second_entity.center_position
                if isinstance(second_entity, Object)
                else second_entity.center_placeholder_position
                if isinstance(second_entity, Receptacle)
                else second_entity.center_position
            )
            ax.plot(
                [first_center[0], second_center[0]],
                [first_center[1], second_center[1]],
                linestyle=line_style,
                linewidth=self.config.linewidth,
                color="white",
            )

            # Mark the end points of the lines with larger solid dots
            ax.scatter(first_center[0], first_center[1], color='white', s=self.config.endpoint_size, zorder=2)
            ax.scatter(second_center[0], second_center[1], color='white', s=self.config.endpoint_size, zorder=2)

    def plot(self, position=(0, 0), ax=None):
        # Plotting logic
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        # Plot the box
        rect = ax.add_patch(
            plt.Rectangle(
                (
                    position[0] + self.config.horizontal_margin,  # margin
                    position[1],
                ),
                self.config.width,
                self.height + self.config.top_pad + self.config.bottom_pad,
                edgecolor="white",
                linewidth=0,
                facecolor=LEGEND_BACKGROUND_COLOR,
            )
        )
        # Set the z-order of the rectangle
        rect.set_zorder(-1)
        left_spacing = self.height / (len(self.left_set))
        right_spacing = self.height / (len(self.right_set))

        # Plot the left nodes
        left_midpoint = (
            position[0] + self.config.horizontal_margin + self.config.width / 4
        )
        left_current_height = (
            position[1] + self.height + self.config.bottom_pad  - left_spacing/2
        )  # top padding
        left_entities = self.plot_entity_column(
            ax, self.left_set, left_midpoint, left_current_height, left_spacing
        )

        # Plot the right nodes
        right_midpoint = (
            position[0] + self.config.horizontal_margin + 3 * self.config.width / 4
        )
        right_current_height = (
            position[1] + self.height + self.config.bottom_pad - right_spacing/2
        )  # top padding
        right_entities = self.plot_entity_column(
            ax, self.right_set, right_midpoint, right_current_height, right_spacing
        )
        
        self.plot_lines(ax, left_entities, right_entities)

        # title 
        ax.text(
            position[0] + self.config.horizontal_margin + self.config.width / 2,
            position[1] + self.height + self.config.bottom_pad,
            self.title,
            horizontalalignment="center",
            verticalalignment="top",
            fontsize=self.config.text_size,
            zorder=float('inf'),
        )

        if created_fig:
            return fig, ax
        else:
            return ax
