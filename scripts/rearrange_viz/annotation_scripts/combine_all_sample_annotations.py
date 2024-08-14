import os
import json
from collections import defaultdict

# Function to process each annotated sample episodes file
def process_annotated_sample_episodes(file_path, all_episodes):
    with open(file_path, 'r') as f:
        annotated_episodes = json.load(f)
    for episode in annotated_episodes['episodes']:
        if "annotations" not in episode:
            episode["annotations"] = []
            # episode["annotations"] = [{
            #     "file_path": file_path
            # }]
        # else:
        #     episode["annotations"][0]["file_path"] = file_path
        episode_id = episode['episode_id']
        scene_id = episode['scene_id']
        
        # Check if episode ID and scene ID combination exists in all_episodes
        if (episode_id, scene_id) in all_episodes:
            # Append new annotations to existing annotations
            all_episodes[(episode_id, scene_id)]['annotations'].extend(episode['annotations'])
        else:
            # Add new entry to all_episodes
            all_episodes[(episode_id, scene_id)] = episode

# Function to merge annotations from all annotated sample episodes files
def combine_all_sample_annotations(base_directory):
    all_episodes = defaultdict(dict)
    
    for subdir in os.listdir(base_directory):
        subdir_path = os.path.join(base_directory, subdir)
        if os.path.isdir(subdir_path):
            annotated_sample_episodes_path = os.path.join(subdir_path, 'annotated_sample_episodes.json')
            if os.path.exists(annotated_sample_episodes_path):
                process_annotated_sample_episodes(annotated_sample_episodes_path, all_episodes)
    
    return list(all_episodes.values())

# Main function
def main():
    base_directory = 'viz_rearrange_30k_1k_v3_5_splits'  # Assuming the script runs in the base directory containing subdirectories
    
    merged_episodes = combine_all_sample_annotations(base_directory)
    
    # Write the merged episodes to a single JSON file
    with open('all_annotations.json', 'w') as f:
        json.dump(merged_episodes, f, indent=4)

if __name__ == '__main__':
    main()
