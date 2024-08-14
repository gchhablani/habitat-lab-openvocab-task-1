import json
import os
import shutil
import copy
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.widgets as widgets

def load_run_data(run_data_path):
    """
    Load run data from JSON file.
    """
    with open(run_data_path) as f:
        return json.load(f)

def load_episode_data(episode_data_path):
    """
    Load episode data from JSON file.
    """
    with open(episode_data_path) as f:
        return json.load(f)

def show_image(episode_id, image_path, propositions, constraints):
    """
    Display image alongside propositions using matplotlib.
    """
    # cols = len(propositions)+1
    cols = 3
    fig, ax = plt.subplots(1, cols, figsize=(30, 8), gridspec_kw={'width_ratios': [0.4, 0.4/(cols-1), 0.4/(cols-1)]})  # Adjust figsize here
    
    # Show image
    image = Image.open(image_path)
    ax[0].imshow(image, interpolation='nearest')
    ax[0].axis('off')
    ax[0].set_title(f'Image: episode_id: {episode_id}')
    
    # # Show propositions
    # for i, proposition in enumerate(propositions):
    #     ax[i+1].axis('off')
    #     ax[i+1].text(0.1, 0.1, json.dumps(proposition, indent=4), fontsize=8)
    #     ax[i+1].set_title(f'Proposition {i+1}')
    new_propositions = copy.deepcopy(propositions)
    for proposition in new_propositions:
        if "object_handles" in proposition["args"]: 
            del proposition["args"]["object_handles"]
        if "receptacle_handles" in proposition["args"]:
            del proposition["args"]["receptacle_handles"]
    ax[1].axis('off')
    ax[1].text(0.1, 0.5, json.dumps(new_propositions, indent=4), fontsize=8, va="center")
    ax[1].set_title(f'Propositions')
    
    
    ax[2].axis('off')
    ax[2].text(0.1, 0.5, json.dumps(constraints, indent=4), fontsize=8, va="center")
    ax[2].set_title(f'Constraints')
    
    # Function to handle key press event
    global user_input
    user_input = ''
    def on_key(event):
        global user_input
        if event.key.lower() == 'k':
            plt.close(fig)
            user_input = 'k'
        elif event.key.lower() == 'd':
            plt.close(fig)
            user_input = 'd'
        elif event.key.lower() == 'q':
            plt.close(fig)
            exit()
        else:
            raise NotImplementedError(f"Not implemented for user input : {user_input}")

    fig.canvas.mpl_connect('key_press_event', on_key)
    plt.show()
    return user_input

def manual_filter(run_data, images_folder, output_folder):
    """
    Manually filter the data.
    """
    filtered_data = {
        "config": None,
        "episodes": []
    }
    for episode_data in run_data["episodes"]:
        episode_id = episode_data["episode_id"]
        image_path = os.path.join(images_folder, f"viz_{episode_id}.png")
        episode_data_path = os.path.join(images_folder, f"episode_data_{episode_id}.json")
        
        if os.path.exists(image_path) and os.path.exists(episode_data_path):
            print(f"Episode ID: {episode_id}")
            user_input = show_image(episode_id, image_path, episode_data["evaluation_propositions"], episode_data["evaluation_constraints"])
            print(user_input)
            if user_input == 'k':
                # Create output folder if it doesn't exist
                os.makedirs(output_folder, exist_ok=True)
                # Copy image and episode data to the output folder
                shutil.copy(image_path, output_folder)
                shutil.copy(episode_data_path, output_folder)
                print(f"Episode data and image for Episode ID {episode_id} copied to {output_folder}.")
                filtered_data["episodes"].append(episode_data)
            elif user_input == 'd':
                print(f"Episode data and image for Episode ID {episode_id} skipped.")
            else:
                print("Invalid input. Skipping this episode data.")
        else:
            print(f"Image or episode data not found for Episode ID {episode_id}. Skipping.")

        # Save the filtered data
        with open(os.path.join(output_folder, 'filtered_run_data.json'), 'w') as f:
            json.dump(filtered_data, f, indent=4)
        print("Filtered data saved.")

    return filtered_data

def main():
    # run_data_path = input("Enter path to run data JSON file: ")
    # images_folder = input("Enter path to folder containing images and episode data JSON files: ")
    # output_folder = input("Enter path to output folder for filtered data: ")
    run_data_path = '2024_05_01_test_hitl_run_data.json'
    images_folder = 'study_data'
    output_folder = 'study_data_filter'
    
    run_data = load_run_data(run_data_path)
    filtered_data = manual_filter(run_data, images_folder, output_folder)
    


if __name__ == "__main__":
    main()
