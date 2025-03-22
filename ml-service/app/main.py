import logging

from fastapi import FastAPI

from app.api.upscaler import router as upscaler_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()
app.include_router(upscaler_router)
