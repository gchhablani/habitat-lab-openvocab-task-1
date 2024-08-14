import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


class Placeholder:
    def __init__(self, config):
        self.config = config.placeholder
        self.center_position = None

    @property
    def width(self):
        return self.config.width

    @property
    def height(self):
        return self.config.height

    def plot(self, ax=None, origin=(0, 0)):
        if ax is None:
            fig, ax = plt.subplots()
            created_fig = True
        else:
            created_fig = False

        object_rect = FancyBboxPatch(
            (origin[0], origin[1]),
            self.width,
            self.height,
            edgecolor="white",
            facecolor="black",
            linewidth=0,
            linestyle="-",
            boxstyle=f"Round, pad=0, rounding_size={self.config.rounding_size}",
            alpha=1.0,
        )

        ax.add_patch(object_rect)

        self.center_position = (
            origin[0] + self.width / 2,
            origin[1] + self.height / 2,
        )  # Update center position

        if created_fig:
            return fig, ax
        else:
            return ax
