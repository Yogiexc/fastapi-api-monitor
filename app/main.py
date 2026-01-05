from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import monitoring


# Create database tables
# Ini bikin semua tabel yang ada di models/
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="API Monitoring Service",
    description="Simple service monitoring API untuk cek uptime dan response time",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# CORS middleware (optional, kalau mau akses dari frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ganti dengan domain specific di production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(monitoring.router)


@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {
        "message": "API Monitoring Service is running! 🚀",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """
    Simple health check endpoint untuk monitoring service itu sendiri.
    """
    return {"status": "healthy", "service": "api-monitor"}