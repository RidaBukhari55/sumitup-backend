# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Existing routes
from routes.upload import router as upload_router
from routes.processing import router as processing_router
from routes.transcript import router as transcript_router

# ✅ NEW: Auth routes
from routes.auth_routes import router as auth_router

app = FastAPI(title="SumItUp API")

# =========================
# CORS settings (React frontend)
# =========================
origins = [
    "http://localhost:5173",   # Vite default port
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# Static files (uploads)
# =========================
app.mount(
    "/uploads",
    StaticFiles(directory="temp/videos"),
    name="uploads"
)

# =========================
# Routes
# =========================
app.include_router(upload_router, prefix="/api")
app.include_router(processing_router, prefix="/api")
app.include_router(transcript_router, prefix="/api")

# ✅ NEW: Auth routes
app.include_router(auth_router)
