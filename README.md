### Animal Detector

This is a project for locally running Megadetector, a wildife object detection model from the  Microsoft AI for Earth program.

This app was initially developed with Megadetector v4 for a bit of consulting work for an environmental consulting company in California. I gave this presentation in early Novemember 2020 to show how I used open models and open source tools (streamlit, tensorflow) to remove tens of thousands of uninteresting camera trap photos that did not contain animals. Check it out here: https://docs.google.com/presentation/d/17tPORZ7CcgLbayio6YC0d-D_242F9rX3R0BQ33nWmBA/edit?pli=1#slide=id.ga6c6ba30c0_1_34

This new iteration uses Megadetector V5 compiled with TensorRt for fast inference which can process about half a terabyte of imagery in about 11 hours.

# Running Megadetector with Torchserve

You can run the container in `mdv5app` to start a Torchserve model server. See that README for details.

Once it is running, you can adapt and run the `app/detect.sh` and `animal_detector_process.py` script depending on your imagery archive location and folder structure.

### Pipeline for filtering a directory of images by both animal presence and species

The species model is not as robust as the wildlife object detection model. There are too many classes used to train the model, so overly specific species categories get confused with each other. Still, it can be used as a manually crafted filter if you want to weed out photos of sheep/cattle etc, which tend to get classified as livestock or ungulate species reliably, whereas other species of interest get classified as a different range of species.

NOTE: This model is very old. It uses an ancient version of Tensorflow, which depends on old CUDA drivers, which only work with old GPUs. This means I can't test GPU functionality on my Nvidia 3090, Nvidia 1080 Ti works but I don't have one anymore!

I have tested with CPU and the model can still run, but slowly. Also, there's an annoying bug where because this uses an old bas eimage for CUDA+torch, importing torch requires NVIDIA drivers and docker to be run with the `--gpus all` flag, even to run the CPU version. This could be addressed with a different base image probably but at this point there are hopefully better species classification models out there in the wild or the literature.

To run the species detection, you'll need to build the Species detection container:

```
docker build -t species_detector -f Dockerfile-species .
```

To run detection on a folder of imagery:

```
docker run -it --rm --gpus all -v "$(pwd)"/data:/data -v "$(pwd)"/SpeciesClassification:/app species_detector --images_to_classify /data/SampleAnimalPics --classification_output_file /data/results.csv --taxonomy_path /app/species_classification.2019.12.00.taxa.csv --classification_model_path /app/species_classification.2019.12.00.pytorch


sudo chmod -R a+rwx data/species_results/
python filter_common_animals.py --csv_path data/species_results/ --common_to_filter "sheep" --threshold .2
```

make sure to download the model files and other data for species classification referenced here and place them in the `SpeciesClassification` folder: https://github.com/microsoft/SpeciesClassification

```
se_resnext101_32x4d-3b2fe3d8.pth
species_classification.2019.12.00.pytorch
inceptionv4-8e4777a0.pth
species_classification.2019.12.00.taxa.csv
```
The .pth files are downloaded automatically during the `classify_images.py` script every time it is run if they are not copied during the docker build.
