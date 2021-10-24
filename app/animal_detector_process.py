from animal_detector.detection.run_tf_detector import ImagePathUtils
from animal_detector.detection.run_tf_detector_batch import *
from animal_detector.detection.run_tf_detector import load_and_run_detector
import os
import click
import shutil

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
        image_file_names = ImagePathUtils.find_images(input_folder, False)
        print("{} image files found in the input directory".format(len(image_file_names)))
    # A json list of image paths
    elif os.path.isfile(input_folder) and input_folder.endswith(".json"):
        with open(input_folder) as f:
            image_file_names = json.load(f)
        print("{} image files found in the json list".format(len(image_file_names)))
    # A single image file
    elif os.path.isfile(input_folder) and ImagePathUtils.is_image_file(input_folder):
        image_file_names = [input_folder]
        print("A single image at {} is the input file".format(input_folder))
    else:
        raise ValueError(
            "image_file specified is not a directory, a json list, or an image file, "
            "(or does not have recognizable extensions)."
        )

    assert len(image_file_names) > 0, "Specified image_file does not point to valid image files"
    assert os.path.exists(
        image_file_names[0]
    ), "The first image to be scored does not exist at {}".format(image_file_names[0])

    print("Starting detection. One image requires a bit less than one second When using a GPU...")
    start_time = time.time()

    results = load_and_run_detector_batch(
        model_file="./md_v4.1.0.pb",
        image_file_names=image_file_names,
        checkpoint_path=None,
        confidence_threshold=0.65,
        checkpoint_frequency=-1,
        results=[],
        n_cores=0,
    )

    elapsed = time.time() - start_time
    write_results_to_file(results, os.path.join(out_folder, "results.json"))
    print("Finished inference in {}".format(humanfriendly.format_timespan(elapsed)))


    print("Generating and saving detection images...")
    animal_images = []
    for i in results:
        if "detections" in i:
            high_conf_dets = list(filter(lambda det: det["conf"] >= 0.9, i["detections"]))
            if len(high_conf_dets) < 3:
                for j in high_conf_dets:
                    # no conf and animal filter
                    # animal_images.append(i["file"])
                    if j["category"] == "1":
                        animal_images.append(i["file"])
                        break

    if no_boxes:
        # no boxes around animal detections
        for i in animal_images:
            fname = os.path.basename(i)
            shutil.copyfile(i, os.path.join(out_folder, fname))
    else:
        # boxes around animal detections
        load_and_run_detector(
            model_file="./md_v4.1.0.pb",
            image_file_names=animal_images,
            output_dir=out_folder,
        )

    # Notify the reader that the data was successfully loaded.
    print(
        f"Running detections is done! Results are saved at {out_folder}. Restart the app to run another station."
    )

if __name__ == "__main__":
    main()
