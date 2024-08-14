import os
import json

# Function to process each subdirectory
def process_subdirectory(subdir):
    sample_episodes_path = os.path.join(subdir, 'sample_episodes.json')
    merged_annotations_path = os.path.join(subdir, 'merged_annotations.json')
    output_path = os.path.join(subdir, 'annotated_sample_episodes.json')
    
    # Check if both JSON files exist
    if not os.path.exists(sample_episodes_path) or not os.path.exists(merged_annotations_path):
        return
    
    # Load sample_episodes.json
    with open(sample_episodes_path, 'r') as f:
        sample_episodes = json.load(f)
    
    # Load merged_annotations.json
    with open(merged_annotations_path, 'r') as f:
        merged_annotations = json.load(f)
    
    # Create a mapping of index to annotation
    annotation_map = {annotation['index']: annotation for annotation in merged_annotations}
    
    # Annotate the sample episodes
    for episode in sample_episodes['episodes']:
        episode_index = sample_episodes['episodes'].index(episode)
        if episode_index in annotation_map:
            annotation = annotation_map[episode_index]
            annotation['subdir_path'] = subdir  # Add subdir path to annotation
            episode['annotations'] = [annotation]
    
    # Write the annotated episodes to the new JSON file
    with open(output_path, 'w') as f:
        json.dump(sample_episodes, f, indent=4)

# Main function to iterate through all subdirectories
def main():
    base_directory = 'spatial_30_july12_200_2_splits'  # Assuming the script runs in the base directory containing subdirectories
    
    for subdir in os.listdir(base_directory):
        subdir_path = os.path.join(base_directory, subdir)
        if os.path.isdir(subdir_path):
            process_subdirectory(subdir_path)

if __name__ == '__main__':
    main()
