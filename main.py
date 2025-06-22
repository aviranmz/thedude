# main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.routers.flights import router as flight_router
from app.routers.hotels import router as hotel_router
from app.routers.esim import router as esim_router
from app.routers.cars import router as cars_router
from app.routers.insurance import router as insurance_router
from app.routers.redirect import router as redirect_router
from app.utils.auth import AuthMiddleware
from fastapi.staticfiles import StaticFiles
import logging

app = FastAPI(
    title="Dude MCP Affiliate API",
    description="Affiliate service for hotels, flights, cars, and insurance",
    version="1.0.0"
)
app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/home.html", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

logging.basicConfig(
    level=logging.INFO,  # or DEBUG
    format="%(asctime)s - %(levelname)s - %(message)s",
)


if os.getenv("ENV") != "local":
    from app.utils.auth import AuthMiddleware
    app.add_middleware(AuthMiddleware)

# # Allow CORS for local development
# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  # Adjust this in production
# #     allow_credentials=True,
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# Include routers
app.include_router(flight_router)
app.include_router(hotel_router)
app.include_router(cars_router)
app.include_router(insurance_router)
app.include_router(esim_router)
app.include_router(redirect_router)
