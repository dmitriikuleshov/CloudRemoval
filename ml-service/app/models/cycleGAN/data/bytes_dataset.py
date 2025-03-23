from io import BytesIO
from PIL import Image

from .base_dataset import BaseDataset, get_transform
from .image_folder import make_dataset


class BytesDataset(BaseDataset):
    """
    This dataset is designed specifically to be created on each endpoint request
    and dynamically extended with PIL image objects.
    """

    def __init__(self, opt):
        BaseDataset.__init__(self, opt)
        self.A_paths = []
        input_nc = self.opt.output_nc if self.opt.direction == 'BtoA' else self.opt.input_nc
        self.transform = get_transform(opt, grayscale=(input_nc == 1))

    def append(self, image: bytes):
        self.A_paths.append(image)

    def __getitem__(self, index):
        image_bytes = self.A_paths[index]
        image = Image.open(BytesIO(image_bytes)).convert('RGB')
        A = self.transform(image)
        return {'A': A, 'A_paths': []}

    def __len__(self):
        """Return the total number of images in the dataset."""
        return len(self.A_paths)
