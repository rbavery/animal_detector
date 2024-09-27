FROM pytorch/torchserve:latest-gpu
RUN whoami
RUN ls -la /home/venv/bin/pip
USER root
# RUN pip install --upgrade pip && pip install opencv-python ipython
# commit id https://github.com/ultralytics/yolov5/blob/9286336cb49d577873b2113739788bbe3b90f83c/requirements.txt
RUN pip install "numpy==1.23.4" "opencv-python==4.6.0.66" \
    "Pillow==9.2.0" "torchvision" "onnxruntime==1.14.1" "onnx==1.13.1" "tensorrt==10.1.0" "tensorrt-cu12==10.4.0" "torch_tensorrt==2.4.0" "nvgpu"
RUN chmod +x /usr/local/bin/dockerd-entrypoint.sh
RUN mkdir -p /home/model-server/ && mkdir -p /home/model-server/tmp
WORKDIR /home/model-server
ENV TEMP=/home/model-server/tmp
ENV YOLOv5_AUTOINSTALL=False
ENV ENABLE_TORCH_PROFILER=TRUE
ENV CUDA_MODULE_LOADING=LAZY
ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
COPY ./config.properties /home/model-server/config.properties
CMD ["serve"]
