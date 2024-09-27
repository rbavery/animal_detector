import torchvision.transforms as tf
import torch
from PIL import Image
ts_model = torch.jit.load("./model-weights/md_v5a.0.0.torchscript")

import torch_tensorrt
im_placeholder = torch.empty((1, 3, 960, 1280), dtype=torch.float32, device=torch.device("cuda:0"))

trt_ts_module = torch_tensorrt.compile(ts_model,
    # If the inputs to the module are plain Tensors, specify them via the `inputs` argument:
    inputs = [im_placeholder], truncate_long_and_double=True)

torch.jit.save(trt_ts_module, "./model-weights/trt_torchscript_module_960_1280.ts") # save the TRT embedded Torchscript