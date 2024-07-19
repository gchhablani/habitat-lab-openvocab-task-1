import json
from collections import Counter

def calculate_scores(data):
    data = [entry for entry in data if "task_correctness" in entry and entry["task_correctness"] and "eval_correctness" in entry and entry["eval_correctness"]]
    total_tasks = len(data)
    all_indices = [entry['index'] for entry in data if "task_correctness" in entry and entry["task_correctness"] and "eval_correctness" in entry and entry["eval_correctness"]]
    missing_indices = set(list(range(0, 99))).difference(all_indices)
    print(missing_indices)
    
    correct_tasks = sum(1 for entry in data if entry["task_correctness"] == "yes")
    task_correctness_score = (correct_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    incorrect_task_remarks = [tuple(entry["task_remarks"]) for entry in data if entry["task_correctness"] == "no"]
    top_incorrect_task_remarks = Counter(incorrect_task_remarks).most_common(3)

    correct_evaluations = sum(1 for entry in data if entry["eval_correctness"] == "yes" and entry["task_correctness"] == "yes")
    eval_correctness_score = (correct_evaluations / correct_tasks) * 100 if correct_tasks > 0 else 0

    incorrect_eval_remarks = [tuple(entry["eval_remarks"]) for entry in data if entry["eval_correctness"] == "no" and entry["task_correctness"] == "yes" and ",".join(entry["eval_remarks"]).strip()]
    top_incorrect_eval_remarks = Counter(incorrect_eval_remarks).most_common(3)

    return total_tasks, task_correctness_score, eval_correctness_score, top_incorrect_task_remarks, top_incorrect_eval_remarks

def main():
    file_path = "spatial_30_july12_200_2_splits/sample_0/merged_annotations.json"  # Change this to your file path
    with open(file_path, "r") as file:
        data = json.load(file)

    total_tasks, task_correctness_score, eval_correctness_score, top_incorrect_task_remarks, top_incorrect_eval_remarks = calculate_scores(data)
    print("Completed Annotations (both eval and task complete): ", total_tasks)
    print("Task Correctness Score: {:.2f}%".format(task_correctness_score))
    print("Evaluation Correctness Score: {:.2f}%".format(eval_correctness_score))
    print("\nTop 3 Task Remarks for Incorrect Tasks:")
    for remark, count in top_incorrect_task_remarks:
        print("- {}: {}".format(remark, count))
    print("\nTop 3 Evaluation Remarks for Incorrect Evaluations:")
    for remark, count in top_incorrect_eval_remarks:
        print("- {}: {}".format(remark, count))

if __name__ == "__main__":
    main()
