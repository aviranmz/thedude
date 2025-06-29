# ==============================
# 🚀 Pydantic Models for Swagger
# ==============================
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AgentRequest(BaseModel):
    user_id: int
    message: str
    channel: Optional[str] = "telegram"

class AgentResponse(BaseModel):
    reply: str
    can_search: bool
    search_types: List[str]
    missing_fields: List[str]
    flights: List[Dict[str, Any]]
    hotels: List[Dict[str, Any]]
    origin: Optional[str]
    destination: Optional[str]
    dates: Dict[str, Optional[str]]
    adults: int
    children: int

# ====================
# 🌐 FastAPI Setup
# ====================
import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.routers.flights import router as flight_router
from app.routers.hotels import router as hotel_router
from app.routers.esim import router as esim_router
from app.routers.cars import router as cars_router
from app.routers.insurance import router as insurance_router
from app.routers.redirect import router as redirect_router
from app.services.agent import handle_user_request

# =============
# 🚀 App Config
# =============
app = FastAPI(
    title="Dude MCP Affiliate API",
    description="Affiliate service for hotels, flights, cars, and insurance",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ================================
# ✅ CORS Middleware for n8n/cloud
# ================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, use specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================
# 🔐 Auth Middleware (Prod)
# =====================
if os.getenv("ENV") != "local":
    from app.utils.auth import AuthMiddleware
    app.add_middleware(AuthMiddleware)

# =====================
# 📡 Main /agent Endpoint
# =====================
@app.post("/agent", response_model=AgentResponse)
async def travel_agent_entry(payload: AgentRequest):
    return await handle_user_request(payload.dict())

# 🔧 Respond to OPTIONS preflight (for n8n/parameter fetching)
@app.options("/agent")
async def options_handler():
    return Response(headers={"Allow": "OPTIONS, POST"}, status_code=204)

# =====================
# 🔍 Static Home Test Page
# =====================
@app.get("/home.html", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# =====================
# 🔧 Routers
# =====================
app.include_router(flight_router)
app.include_router(hotel_router)
app.include_router(cars_router)
app.include_router(insurance_router)
app.include_router(esim_router)
app.include_router(redirect_router)

# =====================
# 📋 Logging
# =====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
