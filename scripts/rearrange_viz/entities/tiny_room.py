import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from .utils import wrap_text


class TinyRoom:
    def __init__(self, config, room_id):
        self.config = config.room
        self.room_id = room_id
        self.center_position = None

    @property
    def width(self):
        return self.config.width

    @property
    def height(self):
        return self.config.height

    def plot_text_label(self, ax):
        self.text_position = (
            self.center_position[0],
            self.center_position[1] + self.config.text_margin,
        )
        # Assuming 100 is max chars for any room name
        wrapped_text = wrap_text(
            self.room_id, 100, split_on_period=True
        )
        ax.annotate(
            wrapped_text,
            xy=self.text_position,
            ha="center",
            va="center",
            fontsize=self.config.text_size,
            zorder=float('inf'),
        )

    def plot(self, ax=None, origin=(0, 0)):
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        self.room_rect = FancyBboxPatch(
            origin,
            self.width,
            self.height,
            edgecolor="white",
            facecolor="#3E4C60",
            linewidth=1,
            linestyle="-",
            alpha=1.0,
        )
        ax.add_patch(self.room_rect)
        
        self.center_position = (
            origin[0] + self.width/2,
            origin[1] + self.height/2
        )

        self.plot_text_label(ax)

        if created_fig:
            return fig, ax
        else:
            return ax
