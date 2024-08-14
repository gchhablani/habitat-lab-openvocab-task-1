

class InstanceColorMap:
    _instance_colors = {}

    @classmethod
    def set_color(cls, instance_id, color):
        """Sets the color for a given instance ID."""
        cls._instance_colors[instance_id] = color

    @classmethod
    def get_color(cls, instance_id):
        """Gets the color for a given instance ID."""
        return cls._instance_colors.get(instance_id, None)

    @classmethod
    def remove_color(cls, instance_id):
        """Removes the color for a given instance ID."""
        if instance_id in cls._instance_colors:
            del cls._instance_colors[instance_id]

    @classmethod
    def get_all_colors(cls):
        """Gets all instance colors."""
        return cls._instance_colors.copy()

    @classmethod
    def has_color(cls, instance_id):
        """Checks if a color exists for a given instance ID."""
        return instance_id in cls._instance_colors
    
    @classmethod
    def reset_map(cls):
        cls._instance_colors = {}
    
