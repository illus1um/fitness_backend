from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.session import Base, engine
import logging

from routers.auth import auth_router
from routers.users import users_router
from routers.password_reset import password_reset_router
from routers.progress import router as progress_router
from routers.plan import router as plan_router

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS
origins = [
    "http://localhost",
    "http://10.0.2.2:8000",
    "http://192.168.1.76:8000",
    "http://192.168.1.76",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router, prefix="/auth", tags=["Authentification"])
app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(password_reset_router, prefix="/password", tags=["Reset Password"])
app.include_router(progress_router, prefix="/progress", tags=["Progress"])
app.include_router(plan_router, prefix="/plan", tags=["Plan"])
