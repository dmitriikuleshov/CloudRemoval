import zipfile
from io import BytesIO
from typing import List

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from app.models.cycleGAN.functions import remove_clouds_from_image


router = APIRouter(
    prefix="/cloud-remove",
    tags=["Cloud removal"]
)


@router.post("/")
async def photo_cloud_removal(file: UploadFile = File(...)):
    image_bytes = await file.read()
    clouds_removed = remove_clouds_from_image(image_bytes)
    return StreamingResponse(clouds_removed, media_type="image/png")


@router.post("/batch")
async def batch_cloud_removal(files: List[UploadFile] = File(...)):
    # Create a zip file to store the processed versions
    zip_buffer = BytesIO()

    # Start polulating the ZIP with modified images
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for i, file in enumerate(files):
            image_bytes = await file.read()
            clouds_removed = remove_clouds_from_image(image_bytes)
            zipf.writestr(f"output_{i+1}.png", clouds_removed.getvalue())

    zip_buffer.seek(0);

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=clouds_removed.zip"}
    )


@router.post("/batch/stream")
async def streamed_batch_cloud_removal(files: List[UploadFile] = File(...)):
    # This variable defines how to differenciate between different
    # pictures that are streamed over an HTTP connection
    boundary = "entry_boundary"

    # To prevent FastAPI from prematurely closing files, read them in advance
    read_files = [await file.read() for file in files]

    # Starting the streaming loop
    return StreamingResponse(
        stream_loop(read_files, boundary),
        media_type="multipart/mixed; boundary=batch_boundary"
    )


async def stream_loop(images: List[bytes], boundary: str):
    f"--{boundary}\r\n".encode()

    for i, image in enumerate(images):
        clouds_removed = remove_clouds_from_image(image)

        yield "Content-Type: image/png\r\n".encode()
        yield f"Content-Disposition: attachment; filename=output_{i+1}.png\r\n\r\n".encode()
        yield clouds_removed.getvalue()
        yield f"\r\n--{boundary}\r\n".encode()
