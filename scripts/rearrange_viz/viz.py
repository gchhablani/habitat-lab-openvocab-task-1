import argparse
import json
import os
import random
import traceback

import matplotlib
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from entities import Object, Receptacle, Room, Scene, PrediViz
from omegaconf import OmegaConf
from tqdm import tqdm

matplotlib.use("Agg")


def load_configuration():
    """
    Load configuration from config.yaml file.
    """
    config_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "conf/config.yaml"
    )
    return OmegaConf.load(config_path)


def load_episode_data(episode_data_dir, episode_id, prefix="episode_"):
    """
    Load episode data from JSON file.
    """
    with open(
        os.path.join(episode_data_dir, f"{prefix}{episode_id}.json")
    ) as f:
        return json.load(f)


def load_run_data(run_json, episode_id, run_data=None):
    """
    Load run data and retrieve episode data.
    """
    if not run_data:
        with open(run_json) as f:
            run_data = json.load(f)
    for episode in run_data["episodes"]:
        if episode["episode_id"] == str(episode_id):
            return episode
    return None


def plot_object(config, object_id, save_path=None):
    """
    Plot specific object.
    """
    object = Object(config, object_id)
    fig, ax = object.plot()
    if save_path:
        plt.savefig(save_path, dpi=400)
    else:
        plt.show()
    fig.clear()
    plt.close()
    del object


def plot_receptacle(config, receptacle_id, icon_path, save_path=None):
    """
    Plot specific receptacle.
    """
    receptacle = Receptacle(config, receptacle_id, icon_path)
    fig, ax = receptacle.plot()
    if save_path:
        plt.savefig(save_path, dpi=400)
    else:
        plt.show()
    fig.clear()
    plt.close()
    del receptacle


def plot_room(
    config, room_id, episode_data, receptacle_icon_mapping, save_path=None
):
    """
    Plot specific room.
    """
    objects = [
        Object(config, obj_id) for obj_id in episode_data["object_to_room"]
    ]
    room_receptacles = []
    for receptacle_id, r_room_id in episode_data["recep_to_room"].items():
        if r_room_id == room_id:
            icon_path = receptacle_icon_mapping.get(
                receptacle_id, "receptacles/chair@2x.png"
            )
            room_receptacles.append(
                Receptacle(config, receptacle_id, icon_path)
            )
    room_objects = [
        obj
        for obj in objects
        if episode_data["object_to_room"][obj.object_id] == room_id
    ]
    room = Room(config, room_id, room_receptacles, room_objects)
    fig, ax = room.plot()
    if save_path:
        plt.savefig(save_path, dpi=400)
    else:
        plt.show()
    fig.clear()
    plt.close()
    room.cleanup()
    del room


def plot_scene(
    config,
    episode_data,
    propositions,
    constraints,
    receptacle_icon_mapping,
    cropped_receptacle_icon_mapping,
    single_image=True,
    instruction=None,
    save_path=None,
    object_to_recep=None,
    object_to_room=None,
    object_to_states=None,
):
    """
    Plot entire scene.
    """
    objects = []
    for obj_id in episode_data["object_to_room"]:
        new_obj = Object(config, obj_id)
        # Initial states
        if object_to_states is not None and obj_id in object_to_states:
            new_obj.states = object_to_states[obj_id]
            new_obj.previous_states = object_to_states[obj_id].copy()
        objects.append(new_obj)

    rooms = []
    for room_id in episode_data["rooms"]:
        room_receptacles = []
        for receptacle_id, r_room_id in episode_data["recep_to_room"].items():
            if r_room_id == room_id:
                icon_path = receptacle_icon_mapping.get(
                    receptacle_id, "receptacles/chair@2x.png"
                )
                room_receptacles.append(
                    Receptacle(config, receptacle_id, icon_path)
                )
        room_objects = [
            obj
            for obj in objects
            if episode_data["object_to_room"][obj.object_id] == room_id
        ]
        room = Room(
            config,
            room_id,
            room_receptacles,
            room_objects,
            object_to_recep=object_to_recep,
        )
        rooms.append(room)

    scene = Scene(
        config,
        rooms,
        episode_data["instruction"] if instruction is None else instruction,
        object_to_recep,
        object_to_room,
    )
    prediviz = PrediViz(
        config,
        scene
    )
    result_fig_data = prediviz.plot(
        propositions,
        constraints,
        receptacle_icon_mapping,
        cropped_receptacle_icon_mapping,
        single_image=single_image,
    )
    step_id_to_path_mapping = {}
    for step_idx, (fig, ax, final_height, final_width) in enumerate(result_fig_data):
        width_inches = config.width_inches
        fig.set_size_inches(
            width_inches, (final_height / final_width) * width_inches
        )

        # Adjust only the current subplot
        plt.sca(ax)
        plt.subplots_adjust(right=0.98, left=0.02, bottom=0.02, top=0.95)
        if save_path:
            # Save each step as a separate image
            if not os.path.exists(save_path):
                os.makedirs(save_path, exist_ok=True)
            fig.savefig(
                os.path.join(save_path, f"step_{step_idx}.png"), dpi=400
            )
            step_id_to_path_mapping[step_idx] = os.path.join(save_path, f"step_{step_idx}.png")
        else:
            fig.show()
        fig.clear()
    plt.close()
    scene.cleanup()
    del scene
    return step_id_to_path_mapping


def get_episode_data_for_plot(args, episode_id, loaded_run_data=None):
    episode_data = load_episode_data(
        args.episode_data_dir, episode_id, args.episode_file_prefix
    )
    handle_to_recep = {
        v: k for k, v in episode_data["recep_to_handle"].items()
    }
    handle_to_object = {
        v: k for k, v in episode_data["object_to_handle"].items()
    }
    id_to_room = {v: k for k, v in episode_data["room_to_id"].items()}
    for receptacle_id in episode_data["recep_to_description"]:
        if not os.path.exists(
            f'receptacles/{"_".join(receptacle_id.split("_")[:-1])}@2x.png'
        ):
            raise NotImplementedError(
                f"Missing receptacle asset for receptacle ID: {receptacle_id}"
            )

    receptacle_icon_mapping = {
        receptacle_id: f'receptacles/{"_".join(receptacle_id.split("_")[:-1])}@2x.png'
        for receptacle_id in episode_data["recep_to_description"]
        if os.path.exists(
            f'receptacles/{"_".join(receptacle_id.split("_")[:-1])}@2x.png'
        )
    }
    cropped_receptacle_icon_mapping = {
        receptacle_id: f'cropped_receptacles/{"_".join(receptacle_id.split("_")[:-1])}@2x.png'
        for receptacle_id in episode_data["recep_to_description"]
        if os.path.exists(
            f'cropped_receptacles/{"_".join(receptacle_id.split("_")[:-1])}@2x.png'
        )
    }
    run_data = load_run_data(args.run_json, episode_id, loaded_run_data)
    # assert run_data["info"]["task_gen"] == "object_states", "Not object state example"
    # Handle Propositions
    propositions = run_data["evaluation_propositions"]
    # all_functions = set(proposition["function_name"] for proposition in propositions)
    # assert "is_next_to" in all_functions, "is_next_to not in episode data"
    for proposition in propositions:
        if proposition["function_name"] not in [
            "is_on_top",
            "is_inside",
            "is_on_floor",
            "is_in_room",
            "is_next_to",
            "is_filled",
            "is_powered_on",
            "is_powered_off",
            "is_clean",
            
        ]:
            raise NotImplementedError(
                f'Not implemented for function_name {proposition["function_name"]}'
            )
        if "object_handles" in proposition["args"]:
            # if (
            #     proposition["args"]["number"] > 1
            #     and len(proposition["args"]["object_handles"])
            #     != proposition["args"]["number"]
            # ):
            #     raise NotImplementedError(
            #         f'Given number {proposition["args"]["number"]} does not match number of objects {len(proposition["args"]["object_handles"])} in proposition. Not handled currently.'
            #     )
            proposition["args"]["object_names"] = []
            for object_handle in proposition["args"]["object_handles"]:
                proposition["args"]["object_names"].append(
                    handle_to_object[object_handle]
                )
        if "receptacle_handles" in proposition["args"]:
            proposition["args"]["receptacle_names"] = []
            for recep_handle in proposition["args"]["receptacle_handles"]:
                proposition["args"]["receptacle_names"].append(
                    handle_to_recep[recep_handle]
                )

        if "room_ids" in proposition["args"]:
            proposition["args"]["room_names"] = []
            for room_id in proposition["args"]["room_ids"]:
                proposition["args"]["room_names"].append(id_to_room[room_id])
        if "entity_handles_a" in proposition["args"]:
            for entity_index in ["a", "b"]:
                proposition["args"][
                    f"entity_handles_{entity_index}_names_and_types"
                ] = []
                for entity_handle in proposition["args"][
                    f"entity_handles_{entity_index}"
                ]:
                    if entity_handle in handle_to_object:
                        proposition["args"][
                            f"entity_handles_{entity_index}_names_and_types"
                        ].append((handle_to_object[entity_handle], "object"))
                    elif entity_handle in handle_to_recep:
                        proposition["args"][
                            f"entity_handles_{entity_index}_names_and_types"
                        ].append(
                            (handle_to_recep[entity_handle], "receptacle")
                        )
                    else:
                        raise ValueError(
                            f"Unknown entity type for handle {entity_handle}. Should be either object or receptacle."
                        )

    # Handle Constraints
    constraints = run_data["evaluation_constraints"]
    for idx, constraint in enumerate(constraints):
        if constraint["type"] == "TemporalConstraint":
            digraph = nx.DiGraph(constraint["args"]["dag_edges"])
            constraint["toposort"] = [
                sorted(generation)
                for generation in nx.topological_generations(digraph)
            ]
        elif constraint["type"] == "TerminalSatisfactionConstraint":
            unique_terminal_constraints = len(
                np.unique(constraint["args"]["proposition_indices"])
            )
            if len(propositions) != unique_terminal_constraints:
                print(
                    f"For episode_id:{episode_id}, len of propositions: {len(propositions)} and unique terminal constraints {unique_terminal_constraints}"
                )
        elif constraint["type"] == "SameArgConstraint":
            same_args = []
            for proposition_index, arg_name in zip(constraint["args"]["proposition_indices"], constraint["args"]["arg_names"]):
                if arg_name == "object_handles" or arg_name == "receptacle_handles":
                    if arg_name == "object_handles":
                        left_name = "object_names"
                        if "receptacle_names" in propositions[proposition_index]["args"]:
                            right_name = "receptacle_names"
                        elif "room_names" in propositions[proposition_index]["args"]:
                            right_name = "room_names"
                        else:
                            raise NotImplementedError(f"Not implemented for `arg_name`: {arg_name} and no receptacle or room names.")
                    elif arg_name == "receptacle_handles":
                        left_name = "receptacle_names"
                        right_name = "object_names"

                    same_args.append({
                        'common_entities': [(item, left_name.split("_")[0]) for item in propositions[proposition_index]["args"][left_name]],
                        'corresponding_entities': [(item, right_name.split("_")[0]) for item in propositions[proposition_index]["args"][right_name]],
                        'line_style': 'dotted' if propositions[proposition_index]["args"]["number"] < len(propositions[proposition_index]["args"]["object_names"]) else 'solid',
                        'global_proposition_index': proposition_index,
                        
                    })
                elif arg_name == "entity_handles_a" or arg_name == "entity_handles_b":
                    entity_index = arg_name.split('_')[-1]
                    opposite_entity_index = "b" if entity_index == "a" else "a"
                    same_args.append(
                        {
                            'common_entities': propositions[proposition_index]["args"][f"entity_handles_{entity_index}_names_and_types"],
                            'corresponding_entities': propositions[proposition_index]["args"][f"entity_handles_{opposite_entity_index}_names_and_types"],
                            'line_style': 'dotted' if propositions[proposition_index]["args"]["number"] < len(propositions[proposition_index]["args"]["entity_handles_a"]) else 'solid',
                            'global_proposition_index': proposition_index,
                        }
                    )
                elif arg_name == "room_ids":
                    right_name = "object_names"
                    same_args.append(
                        {
                            'common_entities': [(item, arg_name.split("_")[0]) for item in propositions[proposition_index]["args"][arg_name]],
                            'corresponding_entities': [(item, right_name.split("_")[0]) for item in propositions[proposition_index]["args"][right_name]],
                            'line_style': 'dotted' if propositions[proposition_index]["args"]["number"] < len(propositions[proposition_index]["args"]["object_names"]) else 'solid',
                            'global_proposition_index': proposition_index,
                        }
                    )
                else:
                    raise NotImplementedError(
                        f"Not implemented SameArg for arg name: {arg_name}"
                    )
            constraint["same_args_data"] = {
                "proposition_indices": constraint["args"]["proposition_indices"],
                "data": same_args
            }
        elif constraint["type"] == "DifferentArgConstraint":
            diff_args = []
            for proposition_index, arg_name in zip(constraint["args"]["proposition_indices"], constraint["args"]["arg_names"]):
                if arg_name == "object_handles" or arg_name == "receptacle_handles":
                    if arg_name == "object_handles":
                        left_name = "object_names"
                        if "receptacle_names" in propositions[proposition_index]["args"]:
                            right_name = "receptacle_names"
                        elif "room_names" in propositions[proposition_index]["args"]:
                            right_name = "room_names"
                        else:
                            raise NotImplementedError(f"Not implemented for `arg_name`: {arg_name} and no receptacle or room names.")
                    elif arg_name == "receptacle_handles":
                        left_name = "receptacle_names"
                        right_name = "object_names"

                    diff_args.append(
                        {
                            'different_entities': [(item, left_name.split("_")[0]) for item in propositions[proposition_index]["args"][left_name]],
                            'corresponding_entities': [(item, right_name.split("_")[0]) for item in propositions[proposition_index]["args"][right_name]],
                            'line_style': 'dotted' if propositions[proposition_index]["args"]["number"] < len(propositions[proposition_index]["args"]["object_names"]) else 'solid',
                            'global_proposition_index': proposition_index,
                        }
                    )
                elif arg_name == "entity_handles_a" or arg_name == "entity_handles_b":
                    entity_index = arg_name.split('_')[-1]
                    opposite_entity_index = "b" if entity_index == "a" else "b"
                    diff_args.append(
                        {
                            'different_entities': propositions[proposition_index]["args"][f"entity_handles_{entity_index}_names_and_types"],
                            'corresponding_entities': propositions[proposition_index]["args"][f"entity_handles_{opposite_entity_index}_names_and_types"],
                            'line_style': 'dotted' if propositions[proposition_index]["args"]["number"] < len(propositions[proposition_index]["args"]["object_names"]) else 'solid',
                            'global_proposition_index': proposition_index,
                        }
                    )
                elif arg_name == "room_ids":
                    right_name = "object_names"
                    diff_args.append(
                        {
                            'different_entities': [(item, arg_name.split("_")[0]) for item in propositions[proposition_index]["args"][arg_name]],
                            'corresponding_entities': [(item, right_name.split("_")[0]) for item in propositions[proposition_index]["args"][right_name]],
                            'line_style': 'dotted' if propositions[proposition_index]["args"]["number"] < len(propositions[proposition_index]["args"]["object_names"]) else 'solid',
                            'global_proposition_index': proposition_index,
                        }
                    )
                else:
                    raise NotImplementedError(
                        f"Not implemented SameArg for arg name: {arg_name}"
                    )
            constraint["diff_args_data"] = {
                "proposition_indices": constraint["args"]["proposition_indices"],
                "data": diff_args
            }
        else:
            raise NotImplementedError(
                f"Constraint type {constraint['type']} is not handled currently."
            )
    return (
        episode_data,
        run_data,
        receptacle_icon_mapping,
        cropped_receptacle_icon_mapping,
        propositions,
        constraints,
    )


def parse_arguments():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Plot scene")
    parser.add_argument("--run-json", type=str, help="Path to run JSON file")
    parser.add_argument(
        "--episode-data-dir",
        type=str,
        help="Directory containing the episode metadata JSON files",
    )
    parser.add_argument("--episode-id", type=int, help="Index of episode")
    parser.add_argument(
        "--object-id", type=str, help="ID of a specific object to plot"
    )
    parser.add_argument(
        "--receptacle-id", type=str, help="ID of a specific receptacle to plot"
    )
    parser.add_argument(
        "--room-id", type=str, help="ID of a specific room to plot"
    )
    parser.add_argument(
        "--save-path", type=str, help="Directory to save the figures"
    )
    parser.add_argument(
        "--episode-file-prefix",
        type=str,
        help="Prefix for episode data files",
        default="episode_",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        help="If only a random subset of all the episodes is to be visualized, the sample size.",
    )
    parser.add_argument(
        "--single-image",
        action="store_true",
        help="If True, save the entire scene as a single image. If False, save each step as a separate image.",
    )
    return parser.parse_args()


def main():
    """
    Main function to plot scenes based on provided arguments.
    """
    args = parse_arguments()
    config = load_configuration()
    sheet_id = None

    current_dir = os.path.dirname(__file__)
    font_dirs = [os.path.join(current_dir, "fonts")]
    font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    plt.rcParams["font.family"] = "Inter"
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["text.color"] = "white"

    with open(args.run_json) as f:
        loaded_run_data = json.load(f)

    if args.episode_id is not None:
        episode_ids = [args.episode_id]
    else:
        if args.sample_size:
            # Group episodes by scene_id
            grouped_episodes = {}
            for episode in loaded_run_data["episodes"]:
                scene_id = episode["scene_id"]
                if scene_id not in grouped_episodes:
                    grouped_episodes[scene_id] = []
                grouped_episodes[scene_id].append(episode)

            # Shuffle scene IDs to ensure random order
            scene_ids = list(grouped_episodes.keys())
            random.shuffle(scene_ids)
            print("Total unique scenes: ", scene_ids)
            # Sample one episode from each scene until reaching the desired sample size
            sampled_episodes = []
            while len(sampled_episodes) < args.sample_size:
                for scene_id in scene_ids:
                    episodes = grouped_episodes[scene_id]
                    if not episodes:
                        continue  # If there are no more episodes for this scene, skip to the next scene
                    selected_episode = random.choice(episodes)
                    try:
                        (
                            temp_episode_data,
                            temp_run_data,
                            temp_receptacle_icon_mapping,
                            temp_cropped_receptacle_icon_mapping,
                            temp_propositions,
                            temp_constraints,
                        ) = get_episode_data_for_plot(
                            args,
                            selected_episode["episode_id"],
                            loaded_run_data,
                        )
                        sampled_episodes.append(selected_episode)
                        # Remove the selected episode from the list of episodes for its scene
                        episodes.remove(selected_episode)
                    except Exception as e:
                        print(scene_id, selected_episode["episode_id"], e)
                        continue

                    # Check if enough episodes have been sampled
                    if len(sampled_episodes) >= args.sample_size:
                        break

                # Break out of the outer while loop if enough episodes have been sampled
                if len(sampled_episodes) >= args.sample_size:
                    break

            # Extract episode_ids
            episode_ids = [
                episode["episode_id"] for episode in sampled_episodes
            ]
            unique_scenes = np.unique(
                [episode["scene_id"] for episode in sampled_episodes]
            )
            print("Sampled episodes unique scenes: ", unique_scenes)
            print("Missing scenes: ", set(scene_ids) - set(unique_scenes))
        else:
            episode_ids = sorted(
                [
                    int(filename.split("_")[-1].split(".")[0])
                    for filename in os.listdir(args.episode_data_dir)
                    if filename.startswith("episode_")
                ]
            )

    # Create a dictionary to store run data for episod es with correct visualizations
    run_data_dict = {"config": None, "episodes": []}

    for episode_id in tqdm(episode_ids):
        try:
            (
                episode_data,
                run_data,
                receptacle_icon_mapping,
                cropped_receptacle_icon_mapping,
                propositions,
                constraints,
            ) = get_episode_data_for_plot(args, episode_id, loaded_run_data)

            save_directory = (
                args.save_path
                if args.save_path
                else f"visualization_{episode_id}"
            )
            os.makedirs(save_directory, exist_ok=True)

            # Save episode_data as JSON inside the folder
            with open(
                os.path.join(
                    save_directory, f"episode_data_{episode_id}.json"
                ),
                "w",
            ) as episode_file:
                json.dump(episode_data, episode_file, indent=4)

            if args.object_id:
                plot_object(
                    config,
                    args.object_id,
                    os.path.join(save_directory, f"viz_{episode_id}.png"),
                )
            elif args.receptacle_id:
                plot_receptacle(
                    config,
                    args.receptacle_id,
                    receptacle_icon_mapping[args.receptacle_id],
                    os.path.join(save_directory, f"viz_{episode_id}.png"),
                )
            elif args.room_id:
                plot_room(
                    config,
                    args.room_id,
                    episode_data,
                    receptacle_icon_mapping,
                    os.path.join(save_directory, f"viz_{episode_id}.png"),
                )
            else:
                step_id_to_path_mapping = plot_scene(
                    config,
                    episode_data,
                    propositions,
                    constraints,
                    receptacle_icon_mapping,
                    cropped_receptacle_icon_mapping,
                    single_image=args.single_image,
                    instruction=run_data["instruction"],
                    save_path=os.path.join(
                        save_directory, f"viz_{episode_id}"
                    ),
                    object_to_recep=episode_data["object_to_recep"],
                    object_to_room=episode_data["object_to_room"],
                    object_to_states=episode_data.get("object_to_states", None),
                )

            # Add run data for the current episode to the dictionary
            run_data["viz_paths"] = step_id_to_path_mapping
            run_data_dict["episodes"].append(run_data)

            # Save the run data dictionary to a JSON file
            with open(f"{save_directory}_run_data.json", "w") as f:
                json.dump(run_data_dict, f, indent=4)

        except Exception:
            print(f"Episode ID: {episode_id}")
            print(traceback.format_exc())


if __name__ == "__main__":
    main()
