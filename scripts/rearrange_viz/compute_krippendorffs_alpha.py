from collections import defaultdict
import json
import numpy as np
import krippendorff
from statsmodels.stats.inter_rater import fleiss_kappa

def compute_inter_annotator_agreement(merged_episodes):
    def prepare_annotations(samples, annotators):
        # Initialize a matrix with NaNs
        reliability_data = np.full((len(annotators), len(samples)), np.nan)
        
        sample_index = 0
        for sample_key, annot_dict in samples.items():
            for annotator, value in annot_dict.items():
                annotator_index = annotators.index(annotator)
                reliability_data[annotator_index, sample_index] = value
            sample_index += 1
        return reliability_data

    def prepare_fleiss_annotations(samples):
        grouped_samples = defaultdict(list)
        for sample_key, annot_dict in samples.items():
            annot_list = list(annot_dict.values())
            grouped_samples[len(annot_list)].append(annot_list)
        return grouped_samples

    task_samples = defaultdict(lambda: defaultdict(lambda: np.nan))
    eval_samples = defaultdict(lambda: defaultdict(lambda: np.nan))
    annotators = set()
    
    for episode in merged_episodes:
        episode_id = episode['episode_id']
        scene_id = episode['scene_id']
        sample_key = (episode_id, scene_id)
        
        task_all_yes = True
        
        for annotation in episode['annotations']:
            annotator = annotation['subdir_path']
            annotators.add(annotator)
            if "task_correctness" in annotation:
                if annotation['task_correctness'] == 'yes':
                    task_samples[sample_key][annotator] = 1
                elif annotation['task_correctness'] == 'no':
                    task_samples[sample_key][annotator] = 0
                    task_all_yes = False
                else:
                    raise ValueError(f"Invalid task_correctness value: {annotation['task_correctness']}")
            else:
                print(f"{episode['episode_id']} does not have task correctness")

        if task_all_yes:
            for annotation in episode['annotations']:
                if "eval_correctness" in annotation:
                    annotator = annotation['subdir_path']
                    if annotation['eval_correctness'] == 'yes':
                        eval_samples[sample_key][annotator] = 1
                    elif annotation['eval_correctness'] == 'no':
                        eval_samples[sample_key][annotator] = 0
                    else:
                        raise ValueError(f"Invalid eval_correctness value: {annotation['eval_correctness']}")
                else:
                    print(f"{episode['episode_id']} does not have eval correctness")

    annotators = list(annotators)
    task_annotations = prepare_annotations(task_samples, annotators)
    eval_annotations = prepare_annotations(eval_samples, annotators)
    
    task_agreement_score = krippendorff.alpha(reliability_data=task_annotations, level_of_measurement='nominal')
    eval_agreement_score = krippendorff.alpha(reliability_data=eval_annotations, level_of_measurement='nominal')

    task_fleiss_annotations = prepare_fleiss_annotations(task_samples)
    eval_fleiss_annotations = prepare_fleiss_annotations(eval_samples)
    
    task_fleiss_scores = {}
    eval_fleiss_scores = {}
    
    for n_annotators, annotations in task_fleiss_annotations.items():
        if len(annotations) > 0:
            data = np.array(annotations)
            # Convert annotations to Fleiss' Kappa format
            table = np.zeros((data.shape[0], 2))  # Assuming binary outcomes (0 and 1)
            for i, row in enumerate(data):
                counts = np.bincount(row.astype(int), minlength=2)
                table[i, :] = counts
            task_fleiss_scores[n_annotators] = fleiss_kappa(table)

    for n_annotators, annotations in eval_fleiss_annotations.items():
        if len(annotations) > 0:
            data = np.array(annotations)
            # Convert annotations to Fleiss' Kappa format
            table = np.zeros((data.shape[0], 2))  # Assuming binary outcomes (0 and 1)
            for i, row in enumerate(data):
                counts = np.bincount(row.astype(int), minlength=2)
                table[i, :] = counts
            eval_fleiss_scores[n_annotators] = fleiss_kappa(table)

    return task_agreement_score, eval_agreement_score, task_fleiss_scores, eval_fleiss_scores

def main():
    # Load merged episodes from JSON file
    with open('all_annotations.json', 'r') as f:
        merged_episodes = json.load(f)
    
    # Compute inter-annotator agreement
    task_agreement_score, eval_agreement_score, task_fleiss_scores, eval_fleiss_scores = compute_inter_annotator_agreement(merged_episodes)
    
    # Print the agreement scores
    print("Inter-Annotator Task Agreement Score:")
    print(task_agreement_score)
    print("Possible range for Krippendorff's Alpha: -1 to 1")
    print("Inter-Annotator Eval Agreement Score:")
    print(eval_agreement_score)
    print("Possible range for Krippendorff's Alpha: -1 to 1")
    
    print("Fleiss' Kappa Task Agreement Scores:")
    for n_annotators, score in task_fleiss_scores.items():
        print(f"For {n_annotators} annotators: {score}")
    print("Possible range for Fleiss' Kappa: -1 to 1")

    print("Fleiss' Kappa Eval Agreement Scores:")
    for n_annotators, score in eval_fleiss_scores.items():
        print(f"For {n_annotators} annotators: {score}")
    print("Possible range for Fleiss' Kappa: -1 to 1")

if __name__ == '__main__':
    main()
