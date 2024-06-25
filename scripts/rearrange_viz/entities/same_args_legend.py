import matplotlib.pyplot as plt
import networkx as nx
from .object import Object
from .receptacle import Receptacle

class SameArgsLegend:
    def __init__(self, config, same_args, receptacle_icon_mapping):
        self.config = config
        # same_args is a list of lists
        # each inner list is a list of tuples
        # the first item in each tuple is supposed to be the "same" element
        # the second item in each tuple is the thing to be on the other side
        # each item has its type described in the tuple
        self.same_args = same_args
        self.receptacle_icon_mapping = receptacle_icon_mapping

    @property
    def width(self):
        return self.config.width

    def plot(self, position=(0, 0), ax=None):
        # Create a bipartite graph and separate the entities into two different sets
        G = nx.Graph()
        edge_styles = {}
        for same_args_data in self.same_args:
            left_elements = set()
            right_elements = set()
            for tup in same_args_data:
                left_elements = left_elements.union(set(tup[0]))
                right_elements = right_elements.union(set(tup[1]))
            left_elements = list(left_elements)
            right_elements = list(right_elements)

            # TODO: Think if we need a better logic here.
            # Currently just picking one of the elements here.
            # left element is the common element(s)
            left_element = left_elements[0]
            if not G.has_node(left_element[0]):
                G.add_node(left_element[0], entity=left_element, bipartite=0)
            for item in right_elements:
                node_label = item[0]
                if not G.has_node(node_label):
                    G.add_node(node_label, entity=item, bipartite=1)
                G.add_edge(left_element[0], node_label)

        # NOTE: This assertion is not always true
        # assert nx.is_bipartite(G), "The graph is not bipartite"

        left_set = set()
        right_set = set()
        # Get the two sets of nodes
        for idx, (label, data) in enumerate(G.nodes(data=True)):
            if data["bipartite"] == 1:
                right_set = right_set.union({label})
            else:
                if label == left_element[0]:
                    left_set = left_set.union({label})

        # Get maximum height based on left and right sets
        
        # TODO: Think of better logic to calculate height here
        mx_height = max((len(left_set) + 1) * 2 + len(left_set), (len(right_set) + 1) * 2 + len(right_set)) * self.config.object.height
        if len(left_set) > len(right_set):
            spacing = mx_height / (len(left_set))
        else:
            spacing = mx_height / (len(right_set))

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
                mx_height + self.config.top_pad + self.config.bottom_pad,
                edgecolor="white",
                linewidth=0,
                facecolor="#2D3541",
            )
        )
        # Set the z-order of the rectangle
        rect.set_zorder(-1)

        left_entities = {}
        # Plot the left nodes
        left_midpoint = (
            position[0] + self.config.horizontal_margin + self.config.width / 4
        )
        left_current_height = (
            position[1] + mx_height - 2 * self.config.object.height + self.config.bottom_pad
        )  # top padding
        
        for idx, node in enumerate(left_set):
            entity_id, entity_type = G.nodes[node]['entity']
            if entity_type == "object":
                left_entity = Object(self.config, entity_id)
                left_origin = (
                    left_midpoint - self.config.object.width / 2,
                    left_current_height - self.config.object.height / 2,
                )
            else:
                icon_path = self.receptacle_icon_mapping.get(
                    entity_id, "receptacles/chair@2x.png"
                )
                left_entity = Receptacle(
                    self.config, entity_id, icon_path
                )
                left_origin = (
                    left_midpoint - left_entity.width / 2,
                    left_current_height - left_entity.height / 2,
                )
            left_entities[f"{entity_id}"] = left_entity
            left_entity.plot(
                ax,
                left_origin,
            )
            left_current_height -= spacing
    
        
        right_entities = {}
        # Plot the right nodes
        right_midpoint = (
            position[0] + self.config.horizontal_margin + 3 * self.config.width / 4
        )
        right_current_height = (
            position[1] + mx_height - 2 * self.config.object.height + self.config.bottom_pad
        )  # top padding
        
        for idx, node in enumerate(right_set):
            entity_id, entity_type = G.nodes[node]['entity']
            if entity_type == "object":
                right_entity = Object(self.config, entity_id)
                right_origin = (
                    right_midpoint - self.config.object.width / 2,
                    right_current_height - self.config.object.height / 2,
                )
            else:
                icon_path = self.receptacle_icon_mapping.get(
                    entity_id, "receptacles/chair@2x.png"
                )
                right_entity = Receptacle(
                    self.config, entity_id, icon_path
                )
                right_origin = (
                    right_midpoint - right_entity.width / 2,
                    right_current_height - right_entity.height / 2,
                )
            right_entities[f"{entity_id}"] = right_entity
            right_entity.plot(
                ax,
                right_origin,
            )
            right_current_height -= spacing

        # Plot lines from left entities to right entities
        for edge in G.edges():
            node1, node2 = edge
            line_style='solid'
            if node1 in left_entities:
                left_entity = left_entities[node1]
            elif node1 in right_entities:
                right_entity = right_entities[node1]
            else:
                raise RuntimeError("node1 not in left or right entities")
            if node2 in left_entities:
                left_entity = left_entities[node2]
            elif node2 in right_entities:
                right_entity = right_entities[node2]
            else:
                raise RuntimeError("node2 not in left or right entities")
            left_center = (
                left_entity.center_position
                if isinstance(left_entity, Object)
                else left_entity.center_placeholder_position
            )
            right_center = (
                right_entity.center_position
                if isinstance(right_entity, Object)
                else right_entity.center_placeholder_position
            )
            ax.plot(
                [left_center[0], right_center[0]],
                [left_center[1], right_center[1]],
                linestyle=line_style,
                linewidth=self.config.linewidth,
                color="white",
            )

            # Mark the end points of the lines with larger solid dots
            ax.scatter(left_center[0], left_center[1], color='white', s=self.config.endpoint_size, zorder=2)
            ax.scatter(right_center[0], right_center[1], color='white', s=self.config.endpoint_size, zorder=2)
            ax.text(
                position[0] + self.config.horizontal_margin + self.config.width / 2,
                position[1] + mx_height + self.config.bottom_pad,
                "same arg",
                horizontalalignment="center",
                verticalalignment="top",
                fontsize=self.config.text_size,
                zorder=float('inf'),
            )
        if created_fig:
            return fig, ax
        else:
            return ax
