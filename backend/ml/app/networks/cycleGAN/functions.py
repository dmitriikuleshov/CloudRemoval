import os
from pathlib import Path
from io import BytesIO
from typing import List

from PIL import Image

from .options.test_options import TestOptions
from .data import create_dataset, CustomDatasetDataLoader
from .models import create_model
from .util.image import extract_photo


opt = TestOptions().parse()

opt.name = "cloud2cloud"
opt.checkpoints_dir = Path(__file__).parent / "checkpoints"
opt.dataset_mode = "bytes"
opt.model = "test"
opt.no_dropout = True
opt.isTrain = False

opt.num_threads = 0   # test code only supports num_threads = 0
opt.batch_size = 1    # test code only supports batch_size = 1
opt.serial_batches = True  # disable data shuffling; comment this line if results on randomly chosen images are needed.
opt.no_flip = True    # no flip; comment this line if results on flipped images are needed.
opt.display_id = -1   # no visdom display; the test code saves the results to a HTML file.

model = create_model(opt)      # create a model given opt.model and other options
model.setup(opt)               # regular setup: load and print networks; create schedulers
model.eval()


def remove_clouds_from_image(image: bytes):
    dataset = create_dataset(opt)
    dataset.dataset.append(image)

    for data in dataset:
        model.set_input(data)
        model.test()
        
        visuals = model.get_current_visuals()
        photo_data = extract_photo(visuals, opt.aspect_ratio)
        pil = photo_data['fake']
        
        output = BytesIO()
        pil.save(output, format="PNG")
        output.seek(0)
        
        return output