from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routers import router as auth_router
from app.user.routers import router as user_router
from app.storage.routers import router as storage_router

from app.dependencies.s3 import test_s3
from app.dependencies.database import engine, Base, test_db


app = FastAPI()

# Firstly, testing connections to dependencies
test_db()
test_s3()

# To prevent websites from complaining about
# sources, force CORS to accept any domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add routes
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(storage_router)

# Initialize the database
Base.metadata.create_all(bind=engine)