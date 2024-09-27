docker run --gpus all -it -p 8080:8080 -p 8081:8081 -p 8082:8082 -v $(pwd)/model_store_trt:/home/model-server/model-store torchserve-mdv5a
