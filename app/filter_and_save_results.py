import json
import click
from pathlib import Path

# Function to filter results based on confidence and class
def filter_results(data, confidence_threshold, valid_classes):
    filtered_data = {}
    for img, attributes in data.items():
        if attributes['confidence'] >= confidence_threshold and attributes['class'] in valid_classes:
            filtered_data[img] = attributes
    return filtered_data

# Function to process each results.json file
def process_results_file(file_path, confidence_threshold, valid_classes):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)

    filtered_data = filter_results(data, confidence_threshold, valid_classes)

    with open(str(file_path).split(".json")[0] + "filtered.json", 'w') as json_file:
        json.dump(filtered_data, json_file, indent=4)

# Function to traverse directories and process each results.json file
def traverse_and_filter(data_path, confidence_threshold, valid_classes):
    data_folder = Path(data_path)
    for results_file in data_folder.rglob('results.json'):
        process_results_file(results_file, confidence_threshold, valid_classes)

@click.command()
@click.argument('data_path', type=click.Path(exists=True))
@click.option('--confidence_threshold', default=0.9, help='Confidence threshold for filtering.', type=float)
@click.option('--valid_classes', default='1', help='Valid classes for filtering. Comma separated values.', type=str)
def main(data_path, confidence_threshold, valid_classes):
    """Process and filter results.json files in the data directory."""
    valid_classes = [int(x) for x in valid_classes.split(',')]
    traverse_and_filter(data_path, confidence_threshold, valid_classes)

if __name__ == "__main__":
    main()