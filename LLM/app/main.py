import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.database import engine, Base
from app.api.routes import auth, users, course


  
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        logger.info("Creating all tables in the database")
        await conn.run_sync(Base.metadata.create_all)
        logger.info("All tables created successfully")
    yield

# ✅ Define FastAPI after lifespan is defined
app = FastAPI(
    title="Intelligent LMS API",
    description="A comprehensive Learning Management System with intelligent features",
    version="1.0.0",
    lifespan=lifespan ,
    openapi_url=f"/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc" # ✅ Now it works
)




# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(course.router ,prefix="/api/v1/course", tags=["courses"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Intelligent LMS API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
