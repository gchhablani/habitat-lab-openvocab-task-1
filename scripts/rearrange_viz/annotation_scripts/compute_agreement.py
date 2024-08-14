from collections import defaultdict
import json
from sklearn.metrics import cohen_kappa_score
import numpy as np

# Function to compute inter-annotator agreement
def compute_inter_annotator_agreement(merged_episodes):
    agreement_scores = []
    
    # Group annotations by unique samples (episode_id + scene_id)
    samples = defaultdict(list)
    for episode in merged_episodes:
        episode_id = episode['episode_id']
        scene_id = episode['scene_id']
        sample_key = (episode_id, scene_id)
        for annotation in episode['annotations']:
            # if annotation['index']<180:
            #     continue
            # print(annotation['index'], annotation['task_correctness'])
            if annotation['task_correctness'] == 'yes':
                samples[sample_key].extend([1])
            elif annotation['task_correctness'] == 'no':
                samples[sample_key].extend([0])
            else:
                raise ValueError(annotation['task_correctness'])
    
    # Calculate inter-annotator agreement for each unique sample
    annotator_1 = []
    annotator_2 = []
    for sample_key, annotations in samples.items():
        if len(annotations) > 1:  # Compute only when there are more than one annotation
            annotator_1.append(annotations[0])
            annotator_2.append(annotations[1])
    # print(np.abs(np.array(annotator_1) - np.array(annotator_2)).sum(), len(annotator_1))
    # print(np.sum(annotator_1), np.sum(annotator_2))
    task_agreement_score = cohen_kappa_score(annotator_1, annotator_2)
    
    # Group annotations by unique samples (episode_id + scene_id)
    samples = defaultdict(list)
    for episode in merged_episodes:
        episode_id = episode['episode_id']
        scene_id = episode['scene_id']
        sample_key = (episode_id, scene_id)
        annots_agree_task_correct = True
        for annotation in episode['annotations']:
            if annotation['task_correctness'] == 'no':
                annots_agree_task_correct = False
        if annots_agree_task_correct:
            for annotation in episode['annotations']:
                if annotation['eval_correctness'] == 'yes':
                    samples[sample_key].extend([1])
                elif annotation['eval_correctness'] == 'no':
                    samples[sample_key].extend([0])
                else:
                    raise ValueError(annotation['eval_correctness'])
            
    
    # Calculate inter-annotator agreement for each unique sample
    annotator_1 = []
    annotator_2 = []
    for sample_key, annotations in samples.items():
        if len(annotations) > 1:  # Compute only when there are more than one annotation
            annotator_1.append(annotations[0])
            annotator_2.append(annotations[1])
    # print(np.abs(np.array(annotator_1) - np.array(annotator_2)).sum(), len(annotator_1))
    # print(np.sum(annotator_1), np.sum(annotator_2))
    eval_agreement_score = cohen_kappa_score(annotator_1, annotator_2)

    return task_agreement_score, eval_agreement_score

# Main function
def main():
    # Load merged episodes from JSON file
    with open('all_annotations.json', 'r') as f:
        merged_episodes = json.load(f)
    
    # Compute inter-annotator agreement
    task_agreement_score, eval_agreement_score = compute_inter_annotator_agreement(merged_episodes)
    
    # Print the agreement scores
    print("Inter-Annotator Task Agreement Score:")
    print(task_agreement_score)
    print("Inter-Annotator Eval Agreement Score:")
    print(eval_agreement_score)
if __name__ == '__main__':
    main()
