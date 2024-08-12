import re

from PIL import Image, ImageChops


def add_tint_to_rgb(image, tint_color):
    """
    Adds a tint color to the RGB channels of an image while preserving the alpha channel.

    Parameters:
        image (PIL.Image.Image): The original image.
        tint_color (tuple): The RGB color tuple (r, g, b) to be applied as a tint.

    Returns:
        PIL.Image.Image: The tinted image with preserved alpha channel.
    """
    # Extract the alpha channel from the original image
    r, g, b, alpha = image.split()

    # Create a solid color image of the same size as the original image
    tint = Image.new("RGB", image.size, tint_color)

    # Composite the RGB channels with the tint color
    tinted_rgb = ImageChops.screen(tint.convert("RGB"), image.convert("RGB"))

    # Return the composite image with original alpha channel
    return Image.merge(
        "RGBA",
        (
            tinted_rgb.split()[0],
            tinted_rgb.split()[1],
            tinted_rgb.split()[2],
            alpha,
        ),
    )


def wrap_text(text, max_chars_per_line, split_on_period=False):
    if split_on_period:
        text = text.split('.')[0]
    # Remove digits which are preceded by `_`.
    text = re.sub(r"_(\d+)", "", text)
    # Remove underscores and slashes
    text = text.replace("/", "_")
    text = text.replace(" ", "_")
    names = text.split("_")

    current_line = ""
    wrapped_text = []
    for name in names:
        name = name.strip()
        if len(current_line + name) <= max_chars_per_line:
            current_line += name + " "
        else:
            wrapped_text.append(current_line.strip())
            current_line = name + " "
    wrapped_text.append(current_line.strip())
    wrapped_text = "\n".join(wrapped_text).strip()
    return wrapped_text

def sort_rooms(rooms, instruction):
    # Sorts the rooms based on "relevance"
    # Uses keyword matching with the instruction and room + receptacle + object names
    if not instruction:
        return rooms

    # Split instruction string into words and exclude "room"
    keywords = [word.lower().strip(".") for word in instruction.split()]

    # Create a dictionary to hold the rooms and their relevance score
    relevance_scores = {}

    for room in rooms:
        score = sum(
            " ".join(room.room_id.split("_")[:-1]) in keyword
            for keyword in keywords
        )

        # Consider receptacles in the score calculation
        for receptacle in room.receptacles:
            score += sum(
                " ".join(receptacle.receptacle_id.split("_")[:-1])
                in keyword
                for keyword in keywords
            )

        # Consider objects in the score calculation
        if room.objects:
            for obj in room.objects:
                score += sum(
                    " ".join(obj.object_id.split("_")[:-1]) in keyword
                    for keyword in keywords
                )

        relevance_scores[room] = score

    # Sort the rooms based on relevance score
    sorted_rooms = sorted(
        relevance_scores.keys(),
        key=lambda room: relevance_scores[room],
        reverse=True,
    )

    return sorted_rooms

def redistribute_target_width_to_rooms(rooms_to_plot, target_width):
    # Calculate total width of all rooms
    total_width = sum(room.width for room in rooms_to_plot)

    # Calculate redistribution factor based on target width and total width
    redistribution_factor = target_width / total_width

    # Redistribute width to each room based on their width ratios
    redistributed_widths = [
        room.width * redistribution_factor for room in rooms_to_plot
    ]

    return redistributed_widths

def resize_icon_height(icon, target_height):
    width, height = icon.size
    scaling_factor = target_height / height

    # Resize the image
    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)
    resized_icon = icon.resize((new_width, new_height))
    return resized_icon
