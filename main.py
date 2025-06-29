# ==============================
# 🚀 Pydantic Models for Swagger
# ==============================
import asyncio
import json
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi.responses import StreamingResponse


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

@app.get("/agent-stream")
async def agent_stream(user_id: int, message: str, channel: str = "telegram"):
    async def event_generator():
        yield "data: ✅ Request received. Starting processing...\n\n"
        await asyncio.sleep(0.5)

        # Step 1: Load preferences
        from app.utils.memory import get_user_preferences
        prefs = await get_user_preferences(user_id)
        yield f"data: 🗂️ Loaded preferences: {json.dumps(prefs)}\n\n"
        await asyncio.sleep(0.5)

        # Step 2: Extract trip info using LLM (partial stream if supported)
        from app.utils.llm import extract_trip_info_stream

        update = None  # Initialize before the loop

        try:
            async for step in extract_trip_info_stream(message, prefs):
                update = step
                yield f"data: {json.dumps(step, ensure_ascii=False)}\n\n"
                await asyncio.sleep(0.05)
        except Exception as e:
            yield f"data: ❌ Error extracting trip info: {str(e)}\n\n"
            yield "event: close\ndata: error\n\n"
            return


        # Step 3: Once complete info is detected
        trip_info = update.get("final_info", {}) if update else {}

        trip_info = update.get("final_info")
        if not trip_info or not trip_info.get("complete"):
            yield f"data: ⚠️ Missing fields: {trip_info.get('missing_fields')}\n\n"
            yield f"event: close\ndata: incomplete\n\n"
            return

        # Step 4: Call API gateway
        yield "data: 🚀 Calling flight/hotel APIs...\n\n"
        from app.utils.api_gateway import call_trip_api
        results = await call_trip_api(trip_info)

        # Step 5: Stream response preview
        reply = results.get("formatted_reply", "✅ Done, here are your options.")
        yield f"data: 💬 Final reply: {reply}\n\n"

        # Step 6: Full payload as JSON
        response_data = {
            "reply": reply,
            "can_search": trip_info.get("complete", False),
            "search_types": trip_info.get("type", []),
            "missing_fields": trip_info.get("missing_fields", []),
            "flights": results.get("flights", []),
            "hotels": results.get("hotels", []),
            "origin": trip_info.get("origin"),
            "destination": trip_info.get("destination"),
            "dates": trip_info.get("dates", {}),
            "adults": trip_info.get("adults", 1),
            "children": trip_info.get("children", 0)
        }

        yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
        yield "event: close\ndata: end\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Content-Encoding": "identity"}
    )

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
