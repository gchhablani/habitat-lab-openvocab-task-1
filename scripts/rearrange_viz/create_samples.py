import os
import json
import shutil
import random
import numpy as np

def create_samples(json_file, output_dir, sample_set_size, num_directories, overlap_samples):
    with open(json_file, 'r') as f:
        data = json.load(f)

    episodes = data['episodes']
    sample_set = random.sample(episodes, sample_set_size)
    
    # Shuffle the episodes
    random.shuffle(sample_set)

    # Divide the episodes into common and exclusive sets
    common_examples = sample_set[:overlap_samples]
    exclusive_examples = sample_set[overlap_samples:]
    print(len(exclusive_examples), len(common_examples))
    # Divide the exclusive examples into the specified number of lists
    exclusive_lists = []
    start_index = 0
    # Calculate the number of exclusive examples per list
    num_examples_per_list = len(exclusive_examples) // num_directories
    for i in range(num_directories):
        end_index = start_index + num_examples_per_list
        if i < len(exclusive_examples) % num_directories:
            end_index += 1  # Distribute the remainder examples among the first few lists
        exclusive_lists.append(exclusive_examples[start_index:end_index])
        start_index = end_index

    for list_idx, exclusive_example_list in enumerate(exclusive_lists):
        sample_dir = os.path.join(output_dir, f"sample_{list_idx}")
        os.makedirs(sample_dir, exist_ok=True)
        assets_dir = os.path.join(sample_dir, "assets")
        os.makedirs(assets_dir, exist_ok=True)

        new_episodes = []
        for episode_idx, episode in enumerate(exclusive_example_list):
            new_episode = {}
            for key, value in episode.items():
                if key == 'viz_path':
                    # Copy images to assets directory
                    image_name = os.path.basename(value)
                    current_idx = episode_idx
                    new_episode["idx"] = current_idx
                    new_image_name = image_name.split('_')[0] + f"_{current_idx}.png"
                    new_image_path = os.path.join(assets_dir, f"{new_image_name}")
                    shutil.copy(value, new_image_path)

                    # Update viz_path in new_episode
                    new_episode[key] = f"assets/{new_image_name}"
                else:
                    new_episode[key] = value
            new_episodes.append(new_episode)

        for episode_idx, episode in enumerate(common_examples):
            new_episode = {}
            for key, value in episode.items():
                if key == 'viz_path':
                    # Copy images to assets directory
                    image_name = os.path.basename(value)
                    current_idx = episode_idx + len(exclusive_example_list)
                    new_episode["idx"] = current_idx
                    new_image_name = image_name.split('_')[0] + f"_{current_idx}.png"
                    new_image_path = os.path.join(assets_dir, f"{new_image_name}")
                    shutil.copy(value, new_image_path)

                    # Update viz_path in new_episode
                    new_episode[key] = f"assets/{new_image_name}"
                else:
                    new_episode[key] = value
            new_episodes.append(new_episode)
        # Calculate the length of new episodes
        len_new_episodes = len(new_episodes)
        print(len_new_episodes)
        print("Unique scenes:", len(np.unique([ep['scene_id'] for ep in new_episodes])))
        # Read the HTML file
        html_file_path = "scripts/rearrange_viz/interface/interface.html"
        with open(html_file_path, 'r') as f:
            html_content = f.read()

        # Replace the placeholder with the length of new episodes
        html_content = html_content.replace("NUMBER_OF_IMAGES_IN_SAMPLE", str(len_new_episodes-1))

        # Save the modified HTML file
        modified_html_file_path = os.path.join(sample_dir, "interface.html")
        with open(modified_html_file_path, 'w') as f:
            f.write(html_content)

        # Copy the README file
        readme_file_path = "scripts/rearrange_viz/interface/README.md"
        shutil.copy(readme_file_path, os.path.join(sample_dir, "README.md"))

        # Copy the README image file
        image_file = "scripts/rearrange_viz/interface/image.png"
        shutil.copy(image_file, os.path.join(sample_dir, "image.png"))

        # Copy the README receptacle collage file
        image_file = "scripts/rearrange_viz/interface/receptacle_collage.png"
        shutil.copy(image_file, os.path.join(sample_dir, "receptacle_collage.png"))

        # Save sampled episodes to new JSON file
        new_json_file = os.path.join(sample_dir, "sample_episodes.json")
        with open(new_json_file, 'w') as f:
            json.dump({'episodes': new_episodes}, f, indent=4)
        

if __name__ == "__main__":
    json_file = "spatial_30_july12_200_run_data.json"
    output_dir = "spatial_30_july12_200_2_splits"
    sample_set_size = 198 # out of all, pick 1k
    num_directories = 2 # make 3 sample directories
    overlap_samples = 0
    
    create_samples(json_file, output_dir, sample_set_size, num_directories, overlap_samples)
