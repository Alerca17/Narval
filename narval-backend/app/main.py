from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.security_middleware import SecurityHeadersMiddleware
from app.core.database import engine
from app.models.base import Base
from app.api.v1.router import api_v1_router
from app.api.v1.endpoints.health import health_check
from app.schemas.health import HealthResponse
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure tables exist on startup if not already created
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="Narval MVP — API de Monitoreo de Agua",
    description="Sistema IoT de monitoreo de pH, turbidez y temperatura para acueductos rurales en Colombia, con Semáforo Virtual y Gemini.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cybersecurity & Rate Limiting Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Root Health Check as required by spec (GET /health)
@app.get("/health", response_model=HealthResponse, tags=["Salud"], summary="Chequeo de salud del backend")
def root_health(db: Session = Depends(get_db)):
    return health_check(db)

# API v1 Router
app.include_router(api_v1_router, prefix="/api/v1")
