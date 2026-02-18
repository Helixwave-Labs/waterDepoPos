
import os
import logging
from fastapi import FastAPI, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api_router import api_router

# Production-ready logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True,  # Ensures our config is used even if Uvicorn sets up logging first
)
# Use a dedicated logger for the application
logger = logging.getLogger("water_depot_pos")



app = FastAPI(title="Water Depot POS")
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Log every request and response
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code} {request.method} {request.url}")
    return response

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    logger.info("Application started successfully. Waiting for requests...")




@app.api_route("/", methods=["GET", "HEAD"])
def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to Water Depot POS API"}