# PrediViz

## Steps for Annotation Tests

1. Create the number of samples that you want from the dataset.

```sh
python scripts/rearrange_viz/viz.py --run-json <path to the json file> --episode-data-dir <path to the directory containing episode metadata> --save-path <directory that stores the visualizations> --sample-size <sample size>
```

The above command will create the directory to store the visualizations, and a `<*>_run_data.json` for the run containing the mapping of the indexes to the episodes.

2. Create samples for annotation:

There is a script which can be run by `python scripts/rearrange_viz/create_samples.py`.
In the script, before running, modify the details according to your requirements:

```python
    json_file = "temporal_test_samples_200_run_data.json" # the run data json file
    output_dir = "temporal_test_samples_200_2_splits" # save directory from previous step
    sample_set_size = -1  # out of all available, number of samples to pick. -1 picks everything
    num_directories = 2 # number of sample directories to make
    overlap_samples = 0 # how many samples should be common across the samples, useful for inter-annotator agreement
```

This will create different samples like so:

```sh
temporal_test_samples_200_2_splits/
├── sample_0
│   ├── README.md
│   ├── assets
│   │   ├── viz_0.png
│   │   ├── viz_1.png
│   │   └── viz_2.png
│   ├── image.png
│   ├── interface.html
│   ├── receptacle_collage.png
│   └── sample_episodes.json
├── sample_1
│   ├── README.md
│   ├── assets
│   │   ├── viz_0.png
│   │   ├── viz_1.png
│   │   └── viz_2.png
│   ├── image.png
│   ├── interface.html
│   ├── receptacle_collage.png
│   └── sample_episodes.json
```

3. After the annotations are done, each annotator should place all their annotations in a single folder. Then they should run the following script:

```sh 
python scripts/rearrange_viz/interface/merge_per_sample_annotations.py
```

In this script, they must specify the following:
```python
# Specify the folder containing JSON files, the episodes file, and the output file
folder_path = '~/Desktop/sample_0_all_annotations/' # The directory containing the annotations
episodes_file = 'viz_rearrange_30k_1k_v3_5_splits/sample_0/sample_episodes.json'  # Update this path to your sample episodes JSON path
output_file = 'merged_annotations.json' # DO NOT CHANGE THIS
```

4. After the above is done, the annotators should send the `merged_annotations.json` for collection. Please the respective JSON file in `*/sample_x/merged_annotations.json`. 

Once collected, run the following scripts:

- To calculate scores on individual `merged_annotations.json`:

```sh 
python scripts/rearrange_viz/interface/calculate_scores.py
```

Ensure that the path is correct:
```python
file_path = "spatial_30_july12_200_2_splits/sample_0/merged_annotations.json"  # Change this to your file path
```

5. Then create a combine annotation JSON file for all the samples using:
```sh
python scripts/rearrange_viz/annotation_scripts/combine_all_sample_annotations.py
```
Ensure that the base directory is correct:
```python
    base_directory = 'viz_rearrange_30k_1k_v3_5_splits'  # Assuming the script runs in the base directory containing subdirectories
```

6. Finally, compute different inter-annotator agreement scores using:

```python 
python scripts/rearrange_viz/annotation_scripts/compute_krippendorffs_alpha.py
```

**Note**: Step 5 and 6 only make sense when the common samples are greater than 0.