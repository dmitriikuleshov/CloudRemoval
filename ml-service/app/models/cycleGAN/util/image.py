from typing import Dict

import torch
import numpy as np
from PIL import Image


def extract_photo(visuals, aspect_ratio) -> Dict[str, Image]:
    images = {}

    for label, im_data in visuals.items():
        numpy_image = tensor_to_numpy_image(im_data)
        pil = numpy_image_to_pil(numpy_image, aspect_ratio)
        images[label] = pil

    return images


def tensor_to_numpy_image(input_image, imtype=np.uint8):
    if not isinstance(input_image, np.ndarray):
        if isinstance(input_image, torch.Tensor):  # get the data from a variable
            image_tensor = input_image.data
        else:
            return input_image
        image_numpy = image_tensor[0].cpu().float().numpy()  # convert it into a numpy array
        if image_numpy.shape[0] == 1:  # grayscale to RGB
            image_numpy = np.tile(image_numpy, (3, 1, 1))
        image_numpy = (np.transpose(image_numpy, (1, 2, 0)) + 1) / 2.0 * 255.0  # post-processing: tranpose and scaling
    else:  # if it is a numpy array, do nothing
        image_numpy = input_image
    return image_numpy.astype(imtype)


def numpy_image_to_pil(numpy_image, aspect_ratio=1.0):
    image_pil = Image.fromarray(numpy_image)
    h, w, _ = numpy_image.shape

    if aspect_ratio > 1.0:
        image_pil = image_pil.resize((h, int(w * aspect_ratio)), Image.BICUBIC)
    if aspect_ratio < 1.0:
        image_pil = image_pil.resize((int(h / aspect_ratio), w), Image.BICUBIC)
    
    return image_pil
