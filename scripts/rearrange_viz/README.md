# Scene Visualization Tool

## Overview

This tool provides functionality to visualize scenes described in JSON format along with propositions describing relationships between objects, receptacles, and rooms. It utilizes Python with the following libraries:

- Matplotlib: For plotting scenes and visualizations.
- PIL (Python Imaging Library): For image processing.
- OmegaConf: For managing configurations.
- argparse: For parsing command-line arguments.

## Usage

### Setup

1. Install the required Python packages using pip:

```sh
pip install matplotlib pillow omegaconf
```

2. Clone the repository:

```sh
git clone <repository_url>
```

3. Download the `Inter` font through [Google Fonts](https://fonts.google.com/specimen/Inter?query=inter) and place it in `fonts`.

### Running the tool

You can run the tool using the following command:
```sh
python main.py --scene-json-path <path_to_scene_json> --propositions-path <path_to_propositions_json> [options]
```

Replace `<path_to_scene_json>` with the path to the JSON file containing scene data, and `<path_to_propositions_json>` with the path to the JSON file containing propositions.

### Command-line Options

- `--object-id`: Specify the ID of a specific object to plot.
- `--receptacle-id`: Specify the ID of a specific receptacle to plot.
- `--room-id`: Specify the ID of a specific room to plot.
- `--save-path`: Specify the path to save the generated figure.

### Examples

1. Plotting a specific object:

```sh
python main.py --scene-json-path scene.json --propositions-path propositions.json --object-id <object_id>
```

2. Plotting a specific receptacle:

```sh
python main.py --scene-json-path scene.json --propositions-path propositions.json --receptacle-id <receptacle_id>
```

3. Plotting a specific room:

```sh
python main.py --scene-json-path scene.json --propositions-path propositions.json --room-id <room_id>
```

4. Saving the generated figure:

```sh
python main.py --scene-json-path scene.json --propositions-path propositions.json --save-path output.png
```