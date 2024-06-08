import matplotlib.pyplot as plt

from .object import Object
from .receptacle import Receptacle

class IsNextToLegend:
    
    def __init__(self, config, is_next_tos, receptacle_icon_mapping):
        self.config = config
        self.is_next_tos = is_next_tos
        self.width = self.config.width
        self.receptacle_icon_mapping = receptacle_icon_mapping
    
    def plot(self, position=(0, 0), ax=None):
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        rect = ax.add_patch(
            plt.Rectangle(
                (
                    position[0] + self.config.horizontal_margin, # margin
                    position[1],
                ),
                self.config.width,
                self.config.height,
                edgecolor="white",
                linewidth=0,
                facecolor="#2D3541",
            )
        )
        # Set the z-order of the rectangle
        rect.set_zorder(-1)
        left_midpoint = position[0] + self.config.horizontal_margin + self.config.width/4
        right_midpoint = position[0] + + self.config.horizontal_margin + 3 * self.config.width/4
        left_current_height = position[1] + 3 * self.config.height/4 # top padding
        right_current_height = position[1] + 3 * self.config.height/4 # top padding
        for is_next_to in self.is_next_tos:
            left_entities = []
            right_entities = []
            for entity_a in is_next_to[0]:
                if entity_a[1] == 'object':
                    left_entity = Object(self.config, entity_a[0])
                    left_origin = (
                        left_midpoint - self.config.object.width/2,
                        left_current_height - self.config.object.height/2,
                    )
                else:
                    icon_path = self.receptacle_icon_mapping.get(
                        entity_a[0], "receptacles/chair@2x.png"
                    )
                    left_entity = Receptacle(self.config, entity_a[0], icon_path)
                    left_origin = (
                        left_midpoint - left_entity.width/2,
                        left_current_height - left_entity.height/2,
                    )
                    
                left_entity.plot(
                    ax,
                    left_origin,
                )
                left_current_height -= 500 
                left_entities.append(left_entity)

            for entity_b in is_next_to[1]:
                if entity_b[1] == 'object':
                    right_entity = Object(self.config, entity_b[0])
                    right_origin = (
                        right_midpoint - self.config.object.width/2,
                        right_current_height - self.config.object.height/2
                    )
                else:
                    icon_path = self.receptacle_icon_mapping.get(
                        entity_b[0], "receptacles/chair@2x.png"
                    )
                    right_entity = Receptacle(self.config, entity_b[0], icon_path)
                    right_origin = (
                        right_midpoint - right_entity.width/2,
                        right_current_height - right_entity.height/2,
                    )
                right_entity.plot(
                    ax,
                    right_origin,
                )
                right_current_height -= 500            
                right_entities.append(right_entity)
            if is_next_to[2] < len(is_next_to[0]): # OR proposition
                line_style = 'dotted'
            else:
                line_style = 'solid'

            # Plot lines from left entities to right entities
            for left_entity in left_entities:
                for right_entity in right_entities:
                    left_center = left_entity.center_position if isinstance(left_entity, Object) else left_entity.center_placeholder_position
                    right_center = right_entity.center_position if isinstance(right_entity, Object) else right_entity.center_placeholder_position
                    ax.plot(
                        [left_center[0], right_center[0]],
                        [left_center[1], right_center[1]],
                        linestyle=line_style,
                        color='white'
                    )
        if created_fig:
            return fig, ax
        else:
            return ax