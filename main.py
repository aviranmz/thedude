# ==============================
# 🚀 Pydantic Models for Swagger
# ==============================
import asyncio
from datetime import datetime
from http.client import HTTPException
import json
from aiohttp import request
from fastapi.params import Header
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi.responses import JSONResponse, StreamingResponse


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

@app.get("/status")
async def mcp_status(request: Request):
    # Example only — skip this in local or dev environments
    token = request.headers.get("Authorization", "")
    if not token or "supersecretkey123" not in token:
        return Response(status_code=401)
    return {
        "status": "ok",
        "tools": ["flight", "hotel", "car", "insurance", "esim"]
    }


@app.get("/tools")
async def get_tools(
    request: Request,
    authorization: Optional[str] = Header(None),
    Authorization: Optional[str] = Header(None)
):
    print("HEADERS:", request.headers)

    token = authorization or Authorization    
    print("GET /tools called")
    if token != "Bearer supersecretkey123":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"tools": ["flight", "hotel", "car", "insurance", "esim"]}


@app.options("/agent-stream")
async def options_handler_stream():
    return Response(headers={"Allow": "OPTIONS, POST, GET"}, status_code=204)

@app.post("/agent-stream")
async def agent_stream_post(request: Request):
    data = await request.json()
    user_id = data.get("user_id")
    message = data.get("message")
    channel = data.get("channel", "telegram")
    return await agent_stream(user_id=user_id, message=message, channel=channel)

@app.get("/agent-stream")
async def agent_stream(user_id: int, message: str, channel: str = "telegram"):
    async def event_generator():
        processing = True
        queue = asyncio.Queue()

        # 👂 Background keep-alive sender
        async def keep_alive():
            while processing:
                await queue.put(f"data: 🟢 keep-alive {datetime.utcnow().isoformat()}\n\n")
                await asyncio.sleep(10)

        # 📦 Main processing logic
        async def main_flow():
            nonlocal processing
            await queue.put("data: ✅ Request received. Starting processing...\n\n")
            await asyncio.sleep(0.5)

            # Step 1: Load user preferences
            from app.utils.memory import get_user_preferences
            prefs = await get_user_preferences(user_id)
            await queue.put(f"data: 🗂️ Loaded preferences: {json.dumps(prefs)}\n\n")
            await asyncio.sleep(0.5)

            # Step 2: Extract trip info
            from app.utils.llm import extract_trip_info_stream
            update = None

            try:
                async for step in extract_trip_info_stream(message, prefs):
                    update = step
                    await queue.put(f"data: {json.dumps(step, ensure_ascii=False)}\n\n")
                    await asyncio.sleep(0.05)
            except Exception as e:
                await queue.put(f"data: ❌ Error extracting trip info: {str(e)}\n\n")
                await queue.put("event: close\ndata: error\n\n")
                processing = False
                return

            trip_info = update.get("final_info", {}) if update else {}

            if not trip_info or not trip_info.get("complete"):
                await queue.put(f"data: ⚠️ Missing fields: {trip_info.get('missing_fields')}\n\n")
                await queue.put("event: close\ndata: incomplete\n\n")
                processing = False
                return

            # Step 4: Call API Gateway
            await queue.put("data: 🚀 Calling flight/hotel APIs...\n\n")
            from app.utils.api_gateway import call_trip_api
            results = await call_trip_api(trip_info)

            # Step 5: Stream final reply
            reply = results.get("formatted_reply", "✅ Done, here are your options.")
            await queue.put(f"data: 💬 Final reply: {reply}\n\n")

            # Step 6: Send structured response
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
            await queue.put(f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n")
            await queue.put("event: close\ndata: end\n\n")
            processing = False

        # 🔁 Start both keep-alive and main logic in parallel
        asyncio.create_task(keep_alive())
        asyncio.create_task(main_flow())

        # 🔄 Yield events from the queue
        while True:
            item = await queue.get()
            if item is None:
                break
            yield item

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Content-Encoding": "identity",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*"
        }
    )

@app.get("/agent-stream-debug")
async def agent_stream_debug(user_id: int, message: str, channel: str = "telegram"):
    from starlette.background import BackgroundTask
    from starlette.responses import PlainTextResponse

    buffer = []

    async def capture_stream():
        async for chunk in agent_stream(user_id, message, channel):
            buffer.append(chunk)

    await capture_stream()
    return PlainTextResponse("".join(buffer))



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
