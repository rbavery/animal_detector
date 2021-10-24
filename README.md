### Animal Detector

This is a functional streamlit app for applying Microsoft AI for Earth's Megadetector to images of animals. The app currently runs locally.

This app was developed for a bit of consulting work for an environmental consulting company in California. I gave this presentation in early Novemember 2020 to show them how I used open models and open source tools (streamlit, tensorflow) to remove tens of thousands of uninteresting camera trap photos that did not contain animals. Check it out here: https://docs.google.com/presentation/d/17tPORZ7CcgLbayio6YC0d-D_242F9rX3R0BQ33nWmBA/edit?pli=1#slide=id.ga6c6ba30c0_1_34
 

# Running the app
`docker build -t animal_detector_app .`

`docker run -it --gpus all --rm -v "$(pwd)"/data:/data -v "$(pwd)"/app:/app animal_detector_app bash`

 Make sure the model is downloaded from here https://lilablobssc.blob.core.windows.net/models/camera_traps/megadetector/md_v4.1.0/md_v4.1.0.pb and placed in the same directory from where you are running the script.

 You can select a folder of images to run the model on and the name of an output folder that will be created where images will be saved. Inference will be run twice on all images, once to profile the time it takes and another to save out the visuals of boxes on images (see the code to comment out the extra step you don't want.)

 After dockerizing the app, I hit issues where the app would run on the first input folder in the selector as soon as it was opened, so the `animal_detector_process.py` cli is more ready to use.
