# Setup Instructions

## Download weights and torchscript model

https://github.com/microsoft/CameraTraps/releases/tag/v5.0

## Export yolov5 weights in compiled model formats
Clone the [yolov5 repository](https://github.com/ultralytics/yolov5)

then, export the model in multiple formats
```
 python yolov5_recent/export.py --imgsz 960 1280 --weights model-weights/md_v5a.0.0.pt --include onnx torchscript --device 0
```

The torchscript file can be compiled to a TensorRT model file that works with the Dockerfile in this folder.

Run `torchscript_to_tensorrt.py`, which will produce `./model-weights/trt_torchscript_module_960_1280.ts`

We'll use that since it's fastest on a GPU. To run the model on a CPU, use the ONNX model file.

## Run model archiver

```
torch-model-archiver -f --model-name mdv5a --version 1.0.0 --serialized-file model-weights/trt_torchscript_module_960_1280.ts --extra-files index_to_name.json --handler mdv5_handler_tensorrt.py
```

The .mar file is what is served by torchserve.

Make sure it is in the model store directory before starting the model server

```
mv mdv5a.mar model_store_trt/mdv5a.mar
```

## Serve the torchscript model with torchserve

```
bash docker_mdv5_trt.sh
```

## Return prediction in normalized coordinates with category integer and confidence score

```
curl http://127.0.0.1:8080/predictions/mdv5 -T ../data/SampleAnimalPics/sheep.JPG
```
