import logging
from io import BytesIO
from typing import List
from PIL import Image

import torch

if cuda.is_available():
    logging.info("remover: CUDA is available. Attempting to use it.")
    pipeline = pipeline.to("cuda")
else:
    logging.warning("remover: no supported accelerators found. Defaulting to software inference.")
    pipeline = pipeline.to("cpu")
    
def upscale_image(image_bytes: bytes):
    # Firstly, open the image inside Pillow
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    # For testing purposes, downscale the image to be 128 pixels wide
    width, height = image.size
    new_size = (128, height * 128 // width)

    logging.info(f"Resizing the image to {new_size}")
    image = image.resize(new_size)

    # And now we do the upscale
    logging.info("upscaler: starting the upscale")
    upscaled = pipeline(prompt=prompt, image=image)

    # Save the resulting image in a buffer and return it
    output = BytesIO()
    upscaled.images[0].save(output, format="JPEG")

    output.seek(0)
    return output