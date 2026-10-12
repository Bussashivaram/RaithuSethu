import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio
from contextlib import asynccontextmanager

from routes import auth, farmer, buyer, bookings, chat, notifications, flash_sales, admin, upload
from sockets.chat_socket import sio
from scheduler.main_scheduler import start_scheduler, shutdown_scheduler
from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    shutdown_scheduler()


fastapi_app = FastAPI(title="AgriMarket API", version="1.0.0", lifespan=lifespan)

# ponytail: FRONTEND_URL env in prod, open * for review demo. allow_credentials
# must be False with "*" or browsers reject socket/API calls.
_origins = [o.strip() for o in settings.FRONTEND_URL.split(",") if o.strip()] or ["*"]
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False if _origins == ["*"] else True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register HTTP Routers
fastapi_app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
fastapi_app.include_router(farmer.router, prefix="/api/farmer", tags=["Farmer"])
fastapi_app.include_router(buyer.router, prefix="/api", tags=["Buyer"])
fastapi_app.include_router(bookings.router, prefix="/api/bookings", tags=["Bookings"])
fastapi_app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
fastapi_app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
fastapi_app.include_router(flash_sales.router, prefix="/api/flash-sales", tags=["Flash Sales"])
fastapi_app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
fastapi_app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])


@fastapi_app.get("/")
async def root():
    return {"message": "AgriMarket API is running"}


@fastapi_app.get("/health")
async def health():
    return {"status": "ok"}

# Serve uploaded files
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
fastapi_app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Mount Socket.IO
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)