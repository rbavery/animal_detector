import os
import click
import shutil
from pathlib import Path
import json
import time
import httpx

def find_images(folder_path):
    folder = Path(folder_path)
    extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    images = [img for img in folder.rglob('*') if img.suffix.lower() in extensions]

    return images

def is_image_file(filename):
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']
    return os.path.splitext(filename)[1].lower() in image_extensions

@click.command()
@click.option("--input_folder", help= "Folder with png or jpg images", type=str)
@click.option("--out_folder", help= "Folder to save detection results with png images", type=str)
@click.option("--no_boxes", help= "True if no_boxes, False if save with boxes.", type=bool)
def main(input_folder, out_folder, no_boxes):

    if os.path.isdir(input_folder):
        print("You selected the folder `%s`" %input_folder)
        print("This folder has `%s` files." % len(os.listdir(input_folder)))

    os.makedirs(out_folder, exist_ok=True)
    # Run batch detection

    # Find the images to score; images can be a directory, may need to recurse
    if os.path.isdir(input_folder):
        image_file_names = find_images(input_folder)
        print("{} image files found in the input directory".format(len(image_file_names)))
    # A json list of image paths
    elif os.path.isfile(input_folder) and input_folder.endswith(".json"):
        with open(input_folder) as f:
            image_file_names = json.load(f)
        print("{} image files found in the json list".format(len(image_file_names)))
    # A single image file
    elif os.path.isfile(input_folder) and is_image_file(input_folder):
        image_file_names = [input_folder]
        print("A single image at {} is the input file".format(input_folder))
    else:
        raise ValueError(
            "{input_folder} is not a directory, a json list, or an image file, "
            "(or does not have recognizable extensions)."
        )

    assert len(image_file_names) > 0, "Specified image_file does not point to valid image files"
    assert os.path.exists(
        image_file_names[0]
    ), "The first image to be scored does not exist at {}".format(image_file_names[0])

    start_time = time.time()
    # todo batching
    url = "http://127.0.0.1:8080/predictions/mdv5a"
    headers = {
        "Content-Type": "application/octet-stream",
    }

    ts_top_results = {}
    error_responses = {}
    for pth in image_file_names:
        with open(pth, "rb") as f:
            image_data = f.read()

        response = httpx.post(url, data=image_data, headers=headers)

        if response.status_code == 200 and len(response.json()) != 0:
            ts_top_results.update({str(pth): response.json()[0]})
        else:
            error_responses[str(pth)] = response.status_code


    with open(os.path.join(out_folder, "results.json"), 'w') as json_file:
        json.dump(ts_top_results, json_file, indent=4)

    # Save the error responses
    with open(os.path.join(out_folder, "errors.json"), 'w') as error_file:
        json.dump(error_responses, error_file, indent=4)

    # for pth, result in ts_top_results.items():
    #     request_image = Image.open(pth)
    #     draw_bounding_box_on_image(request_image, result['y1'], result['x1'], result['y2'], result['x2'], result['class'])
    #     request_image.show()


    elapsed = time.time() - start_time
    print(f"Finished inference in {elapsed}")


    # print("Generating and saving detection images...")
    # animal_images = []
    # for i in results:
    #     if "detections" in i:
    #         high_conf_dets = list(filter(lambda det: det["conf"] >= 0.9, i["detections"]))
    #         if len(high_conf_dets) < 3:
    #             for j in high_conf_dets:
    #                 # no conf and animal filter
    #                 # animal_images.append(i["file"])
    #                 if j["category"] == "1":
    #                     animal_images.append(i["file"])
    #                     break

    # for i in animal_images:
    #     fname = os.path.basename(i)
    #     shutil.copyfile(i, os.path.join(out_folder, fname))
    #write_results_to_file(results, os.path.join(out_folder, "results.json"))

    # Notify the reader that the data was successfully loaded.
    print(
        f"Running detections is done! Results are saved at {out_folder}."
    )
if __name__ == "__main__":
    main()
