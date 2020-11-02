"""Main module."""

import streamlit as st
from animal_detector.detection.run_tf_detector import ImagePathUtils
from animal_detector.detection.run_tf_detector_batch import *
from animal_detector.detection.run_tf_detector import load_and_run_detector
import os

st.title("Animal Detection App")

# import skimage.io as skio
# import pathlib
# import random

# results_path = pathlib.Path("./tests/output_imgs/s5results")
# all_imgs = list(results_path.glob("*jpg"))
# length = len(all_imgs)
# btn = st.button("Show example detection result.")
# if btn:
#     random_int = random.randint(0, length-1)
#     arr = skio.imread(all_imgs[random_int])
#     st.image(arr, use_column_width=True, caption = "Detection result where an animal was classified with over .9 confidence.")
# else:
#     st.stop()

# Get folder name from User

def file_selector(folder_path='.'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a folder or file', filenames)
    return os.path.join(folder_path, selected_filename)

filename = file_selector()
if os.path.isdir(filename):
    st.write('You selected the folder `%s`' % filename)
    st.write('This folder has `%s` files.' % len(os.listdir(filename)))

# filename = st.text_input("Enter a path to a station folder with only jpeg images in it (or a .json file referencing these jpegs) : ")
# filename = os.path.join("/home/rave/animal_detector/tests/data/", filename)
# if os.path.exists(filename) is False or "Station" not in filename:
#     st.warning('Warning: The input folder {} does not exist. Please choose a different name.'.format(filename))
#     st.stop()
# st.success("Great! The input folder name is valid.")

station_results_folder_name = st.text_input("Enter a name for the results folder where output detection images and statistics will be stored: ")
station_results_folder_name = os.path.join(station_results_folder_name)
if len(station_results_folder_name) < 2:
    st.warning('Select an output folder path.'.format(station_results_folder_name))
    st.stop()

if os.path.exists(station_results_folder_name):
    st.warning('Warning: The results folder {} already exists and would be overwritten. Please choose a different name.'.format(station_results_folder_name))
    st.stop()

st.success("Great! The input folder name is valid.")

os.mkdir(station_results_folder_name)
# Run batch detection

# Find the images to score; images can be a directory, may need to recurse
if os.path.isdir(filename ):
    image_file_names = ImagePathUtils.find_images(filename, False)
    st.text('{} image files found in the input directory'.format(len(image_file_names)))
# A json list of image paths
elif os.path.isfile(filename) and filename.endswith('.json'):
    with open(filename) as f:
        image_file_names = json.load(f)
    st.text('{} image files found in the json list'.format(len(image_file_names)))
# A single image file
elif os.path.isfile(filename) and ImagePathUtils.is_image_file(filename):
    image_file_names = [filename]
    print('A single image at {} is the input file'.format(filename))
else:
    raise ValueError('image_file specified is not a directory, a json list, or an image file, '
                        '(or does not have recognizable extensions).')

assert len(image_file_names) > 0, 'Specified image_file does not point to valid image files'
assert os.path.exists(image_file_names[0]), 'The first image to be scored does not exist at {}'.format(image_file_names[0])

st.text('Starting detection. One image requires a bit less than one second When using a GPU...')
start_time = time.time()

results = load_and_run_detector_batch(model_file="./md_v4.1.0.pb",
                                        image_file_names=image_file_names,
                                        checkpoint_path=None,
                                        confidence_threshold=.65,
                                        checkpoint_frequency=-1,
                                        results=[],
                                        n_cores=1)

elapsed = time.time() - start_time
write_results_to_file(results, os.path.join(station_results_folder_name, "results.json"))
st.text('Finished inference in {}'.format(humanfriendly.format_timespan(elapsed)))


st.text("Generating and saving detection images...")
animal_images = []
for i in results:
    if 'detections' in i:
        for j in i['detections']:
            # no conf and animal filter
            animal_images.append(i['file'])
            # if j['category'] == '1' and j['conf'] > .90:
            #     animal_images.append(i['file'])
import shutil         
# no boxes around animal detections
# for i in animal_images:
#     fname = os.path.basename(i)
#     shutil.copyfile(i, os.path.join(station_results_folder_name, fname))

# boxes around animal detections
load_and_run_detector(model_file="./md_v4.1.0.pb",
                         image_file_names=animal_images,
                         output_dir = station_results_folder_name)

# Notify the reader that the data was successfully loaded.
st.text(f'Running detections is done! Results are saved at {station_results_folder_name}. Restart the app to run another station.')

