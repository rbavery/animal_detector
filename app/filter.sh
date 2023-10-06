#!/bin/bash
# 1 for animal, 2 for person, 3 for vehicle
for i in {2..13}
do
    echo "Filtering detections and saving new json results..."
    python "filter_and_save_results.py" "../data/outputs_antelope_oct4_$i" --valid_classes "1"
done

echo "All folders processed."
