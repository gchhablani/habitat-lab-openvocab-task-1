import os
import json
from sys import platform

def get_creation_time(file_path):
    """
    Get the creation time of the file. If creation time is not available, use the modification time.
    """
    if platform == "win32":
        # On Windows, getctime() returns the creation time.
        return os.path.getctime(file_path)
    else:
        # On Unix-based systems, getmtime() returns the last modification time.
        return os.path.getmtime(file_path)

def merge_annotations(folder_path, episodes_file, output_file):
    merged_data = {}
    
    # Get a list of all JSON files in the folder
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    
    # Sort files by creation time
    json_files.sort(key=lambda x: get_creation_time(os.path.join(folder_path, x)))
    
    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            data_list = json.load(file)
            
            for data in data_list:
                index = data["index"]
                # Only add to merged_data if index is not already present
                if index not in merged_data and data.get("task_correctness", "") and data.get("eval_correctness", ""):
                    merged_data[index] = data

    # Convert merged_data back to a list
    merged_list = list(merged_data.values())

    # Load the episodes file and verify indices
    with open(episodes_file, 'r') as file:
        episodes_data = json.load(file)
        episode_indices = set(range(len(episodes_data['episodes'])))
    
    merged_indices = set(data["index"] for data in merged_list)

    # Check if all episode indices are covered
    missing_indices = episode_indices - merged_indices
    if missing_indices:
        print(f"Warning: Missing indices in merged data: {missing_indices}")
    else:
        print("All episode indices are covered in the merged data.")

    # Check if task_correctness and eval_correctness are non-empty for all indices
    missing_correctness = []
    for data in merged_list:
        if "task_correctness" not in data or "eval_correctness" not in data:
            missing_correctness.append(data["index"])
        elif not data["task_correctness"] or not data["eval_correctness"]:
            missing_correctness.append(data["index"])
    
    if missing_correctness:
        print(f"Warning: Missing task_correctness or eval_correctness for indices: {missing_correctness}")
    else:
        print("All entries have non-empty task_correctness and eval_correctness fields.")
    
    # Write the merged list to the output file
    with open(output_file, 'w') as output:
        json.dump(merged_list, output, indent=4)

# Specify the folder containing JSON files, the episodes file, and the output file
folder_path = '/Users/gunjanchhablani/Downloads/sample_0_all_annotations/'
episodes_file = 'viz_rearrange_30k_1k_v3_5_splits/sample_0/sample_episodes.json'  # Update this path
output_file = 'merged_annotations.json'

# Call the function to merge JSON files and verify indices
merge_annotations(folder_path, episodes_file, output_file)
