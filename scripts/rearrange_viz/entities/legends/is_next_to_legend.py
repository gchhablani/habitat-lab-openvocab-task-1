import matplotlib.pyplot as plt
import networkx as nx
from ..object import Object
from ..receptacle import Receptacle
from ..constants import LEGEND_BACKGROUND_COLOR

# Function to get bipartite sets from a graph with disconnected components
def get_bipartite_sets(G):
    left_set, right_set = set(), set()
    for component in nx.connected_components(G):
        subgraph = G.subgraph(component)
        if nx.is_bipartite(subgraph):
            left, right = nx.bipartite.sets(subgraph)
            left_set.update(left)
            right_set.update(right)
    return left_set, right_set

class IsNextToLegend:
    def __init__(self, config, is_next_tos, receptacle_icon_mapping):
        self.title = "next to"
        self.config = config
        self.is_next_tos = is_next_tos
        self.receptacle_icon_mapping = receptacle_icon_mapping
        self.set_graph_and_bipartite_sets()
        self.set_height()

    @property
    def width(self):
        return self.config.width

    @property
    def horizontal_margin(self):
        return self.config.horizontal_margin

    @property
    def top_pad(self):
        return self.config.top_pad

    @property
    def bottom_pad(self):
        return self.config.bottom_pad
    
    def set_graph_and_bipartite_sets(self):
        # Create a bipartite graph and separate the entities into two different sets
        self.graphs = []
        self.left_sets = []
        self.right_sets = []
        self.edge_styles = []
        for is_next_to in self.is_next_tos:
            G = nx.Graph()
            edge_style = {}
            for entity_a in is_next_to[0]:
                node_label_a = f"{entity_a[0]}"
                if not G.has_node(node_label_a):
                    G.add_node(node_label_a, entity=entity_a)

            for entity_b in is_next_to[1]:
                node_label_b = f"{entity_b[0]}"
                if not G.has_node(node_label_b):
                    G.add_node(node_label_b, entity=entity_b)
                
                # Determine the line style
                line_style = 'dotted' if is_next_to[2] < len(is_next_to[0]) or is_next_to[2] < len(is_next_to[1]) else 'solid'

                # Add edges between all pairs of nodes in entity_a and entity_b
                for entity_a in is_next_to[0]:
                    node_label_a = f"{entity_a[0]}"
                    G.add_edge(node_label_a, node_label_b)
                    edge_style[(node_label_a, node_label_b)] = line_style

            # Check if the graph is bipartite
            assert nx.is_bipartite(G), "The graph is not bipartite"
            left_set, right_set = get_bipartite_sets(G)
            self.graphs.append(G)
            self.edge_styles.append(edge_style)
            self.left_sets.append(left_set)
            self.right_sets.append(right_set)

    def set_height(self):
        self.left_set_length = sum(len(left_set) for left_set in self.left_sets)
        self.right_set_length = sum(len(right_set) for right_set in self.right_sets)
        self.height = max(
            (self.left_set_length + 1) * 2 + self.left_set_length,
            (self.right_set_length + 1) * 2 + self.right_set_length
        ) * self.config.object.height

    def plot_entity_column(
        self, ax, G, entity_set, midpoint, current_height, spacing
    ):
        entities = {}
        for idx, node in enumerate(entity_set):
            entity_id, entity_type = G.nodes[node]['entity']
            if entity_type == "object":
                entity = Object(self.config, entity_id)
                origin = (
                    midpoint - self.config.object.width / 2,
                    current_height - self.config.object.height / 2,
                )
            else:
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
            entities[f"{entity_id}"] = entity
            entity.plot(
                ax,
                origin,
            )
            current_height -= spacing
        return entities, current_height

    def plot_lines(self, G, edge_style, ax, left_entities, right_entities):
        # Plot lines from left entities to right entities
        for edge in G.edges():
            node1, node2 = edge
            if (node1, node2) in edge_style:
                line_style = edge_style[(node1, node2)]
            else:
                line_style = edge_style[(node2, node1)]
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

        left_spacing = self.height / self.left_set_length
        right_spacing = self.height / self.right_set_length

        # Plot the left nodes
        left_midpoint = (
            position[0] + self.config.horizontal_margin + self.config.width / 4
        )
        left_current_height = (
            position[1] + self.height + self.config.bottom_pad - left_spacing/2
        )
        left_entities = []
        for G, left_set in zip(self.graphs, self.left_sets):
            new_left_entities, left_current_height = self.plot_entity_column(
                ax, G, left_set, left_midpoint, left_current_height, left_spacing
            )
            left_entities.append(new_left_entities)

        # Plot the right nodes
        right_midpoint = (
            position[0] + self.config.horizontal_margin + 3 * self.config.width / 4
        )
        right_current_height = (
            position[1] + self.height + self.config.bottom_pad - right_spacing/2
        )
        right_entities = []
        for G, right_set in zip(self.graphs, self.right_sets):
            new_right_entities, right_current_height = self.plot_entity_column(
                ax, G, right_set, right_midpoint, right_current_height, right_spacing
            )
            right_entities.append(new_right_entities)

        for G, edge_style, current_left_entities, current_right_entities in zip(
            self.graphs, self.edge_styles, left_entities, right_entities
        ):  
            self.plot_lines(G, edge_style, ax, current_left_entities, current_right_entities)

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
