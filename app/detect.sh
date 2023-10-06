#!/bin/bash
BASE_INPUT_FOLDER="/home/rave/Desktop/Antelope Plains Mitigation Site/Camera Station Photos_September 2023/Camera"
BASE_OUT_FOLDER="../data/outputs_Antelope_Oct4"

# Other arguments
NO_BOXES="True"

# Loop over station numbers 1 through 10
for i in {2..13}
do
    # Construct the specific input and output folder paths for the current station
    INPUT_FOLDER="$BASE_INPUT_FOLDER $iB"
    OUT_FOLDER="$BASE_OUT_FOLDER_$i"

    # Execute the Python script with arguments
    python animal_detector_process.py --input_folder "$INPUT_FOLDER" --out_folder "$OUT_FOLDER" --no_boxes "$NO_BOXES"

    echo "Script executed for Station $i."
done
