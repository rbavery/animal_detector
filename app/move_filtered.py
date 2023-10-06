import os
import json
import shutil
import glob

image_folder = "/home/rave/Desktop/Antelope Plains Mitigation Site/Camera Station Photos_September 2023"
detection_folder = "data/outputs_antelope_oct4_"
output_folder = "data/filtered_result_images"

for i in list(range(2,14)):
    station_folder = f"{image_folder}/Camera {i}B"
    det_folder = f"{detection_folder}{i}"
    detjson = os.path.join(det_folder, "resultsfiltered.json")

    # If the filtered_results.json exists, process it
    if os.path.exists(detjson):
        with open(detjson, 'r') as f:
            results = json.load(f)

        # Create a new subdirectory in the output folder with the same name
        new_folder_path = os.path.join(det_folder, "filtered_images")
        os.makedirs(new_folder_path, exist_ok=True)

        # Move each image in the results to the new folder
        for image in results:
            # If the image is found, copy it
            if image:
                new_name = "_".join(image.split("/")[-4:])
                dest = os.path.join(new_folder_path, new_name)
                shutil.copy(image, dest)




