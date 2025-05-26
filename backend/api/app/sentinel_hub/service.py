from datetime import datetime, date
from typing import Tuple, Dict
from uuid import uuid4
from io import BytesIO

import numpy as np
from PIL import Image

from sentinelhub import (
    SHConfig, BBox, CRS, SentinelHubRequest,
    DataCollection, MimeType, bbox_to_dimensions,
    DownloadFailedException
)

from common.settings import Credentials, S3
from common.connectors.s3 import get_s3_client


RGB_EVALSCRIPT = """
function setup() {
    return {
        input: [{
            bands: ["B02", "B03", "B04"],
            units: "DN"
        }],
        output: {
            bands: 3,
            sampleType: "UINT8"
        }
    };
}

function evaluatePixel(sample) {
    var r = Math.min(Math.max(0, (sample.B04 / 10000) * 255), 255);
    var g = Math.min(Math.max(0, (sample.B03 / 10000) * 255), 255);
    var b = Math.min(Math.max(0, (sample.B02 / 10000) * 255), 255);

    return [r, g, b];
}
"""

SAR_EVALSCRIPT = """
function setup() {
  return {
    input: [{
      bands: ["VV"],
      units: "LINEAR_POWER"
    }],
    output: {
      bands: 1,
      sampleType: "UINT8"
    }
  };
}

function evaluatePixel(sample) {
    var value = Math.log(sample.VV) * 10.0 + 100;
    return [Math.min(Math.max(value, 0), 255)];
}
"""


class SentinelHubService:
    def __init__(self):
        self.config = SHConfig()
        self.config.sh_client_id = Credentials.Sentinel.client_id
        self.config.sh_client_secret = Credentials.Sentinel.client_secret
        self.s3_client = get_s3_client()

    def search_and_save_images(self, search_date, coords) -> Dict[str, str]:
        bbox = BBox(bbox=coords, crs=CRS.WGS84)

        requests = {
            "rgb": SentinelHubRequest(
                evalscript=RGB_EVALSCRIPT,
                input_data=[SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL2_L2A,
                    time_interval=search_date
                )],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=bbox,
                size=bbox_to_dimensions(bbox, resolution=20),
                config=self.config
            ),
            "sar": SentinelHubRequest(
                evalscript=SAR_EVALSCRIPT,
                input_data=[SentinelHubRequest.input_data(
                    data_collection=DataCollection.SENTINEL1_IW,
                    time_interval=search_date
                )],
                responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
                bbox=bbox,
                size=bbox_to_dimensions(bbox, resolution=20),
                config=self.config
            )
        }

        s3_keys = {}

        for src, req in requests.items():
            try:
                buf = BytesIO()
                array = req.get_data()[0]
                image = Image.fromarray(np.uint8(array))
                image.save(buf, format="JPEG")
                buf.seek(0)
            except DownloadFailedException:
                print(f"No {src} image found")
                return {}

            s3_keys[src] = f"{str(uuid4())}.jpg"
            self.s3_client.upload_fileobj(
                buf,
                S3.bucket,
                s3_keys[src],
                ExtraArgs={'ContentType': 'image/jpeg'}
            )

        return s3_keys
