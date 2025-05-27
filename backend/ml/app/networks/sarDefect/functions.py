from io import BytesIO
from pathlib import Path

import torch
from PIL import Image
from torchvision import transforms

from common import settings
from .network import RestormerFusion

# choose device
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# init model
_model = RestormerFusion()
# load checkpoint (you can feed this via an env var or settings.ML)

_ckpt = Path(__file__).resolve().parent / "checkpoints/v1.pth"
_state = torch.load(_ckpt, map_location=_device)
_model.load_state_dict(_state)
_model.to(_device).eval()

# preprocessing
_tf = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor()
])

# dummy meta stats (override via settings.ML if needed)

def sarDefect_remove(
    rgb_bytes: bytes,
    sar_bytes: bytes,
    latitude: float,
    longitude: float,
    month: float
) -> BytesIO:
    """
    1) Decode the two input JPEG/PNG byte streams
    2) Preprocess, stack through RestormerFusion(rgb, sar, meta)
    3) Return a PNG in a BytesIO buffer
    """
    _meta_mean = torch.tensor([latitude, longitude, month], device=_device)
    _meta_std  = torch.tensor([1.0, 1.0, 1.0], device=_device)

    # load PIL images
    rgb = Image.open(BytesIO(rgb_bytes)).convert("RGB")
    sar = Image.open(BytesIO(sar_bytes)).convert("RGB")

    # to tensor
    rgb_t = _tf(rgb).unsqueeze(0).to(_device)
    sar_t = _tf(sar).unsqueeze(0).to(_device)

    # build meta
    meta = torch.tensor([[latitude, longitude, month]],
                        dtype=torch.float32, device=_device)
    meta = (meta - _meta_mean) / _meta_std

    # inference
    with torch.no_grad():
        out = _model(rgb_t, sar_t, meta)[0].cpu().clamp(0,1)

    # to PIL + BytesIO
    pil = transforms.ToPILImage()(out)
    buf = BytesIO()
    pil.save(buf, format="PNG")
    buf.seek(0)
    return buf
