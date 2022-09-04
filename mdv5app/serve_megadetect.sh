# https://github.com/pytorch/serve/tree/master/examples/object_detector/fast-rcnn
# https://github.com/pytorch/serve/blob/master/examples/README.md#creating-mar-file-for-torchscript-mode-model
# https://github.com/pytorch/serve 
# setup https://github.com/pytorch/serve

#mkdir model_store

# torch-model-archiver --model-name mdv5 --version 1.0.0 --serialized-file ../models/megadetectorv5/md_v5a.0.0.torchscript --extra-files index_to_name.json --handler ../api/megadetectorv5/mdv5_handler.py
# mv mdv5.mar model_store/megadetectorv5-yolov5-1-batch-2048-2048.mar
torchserve --start --model-store /app/model_store --no-config-snapshots --models mdv5=/app/megadetectorv5-yolov5-1-batch-640-640.mar
#curl http://127.0.0.1:8080/predictions/mdv5 -T ../input/sample-img-fox.jpg
