
import uuid
from utils.supabase import save_search_log, load_user_prefs, update_user_prefs, save_itinerary
from utils.llm import call_llm_agent
from fastapi.responses import JSONResponse

async def trip_agent(data):
    user_id = data["user_id"]
    message = data["message"]
    channel = data.get("channel", "telegram")

    # 1. Log the user's search intent
    await save_search_log(user_id, "trip", message, channel)

    # 2. Load preferences (memory)
    prefs = await load_user_prefs(user_id)

    # 3. Invoke LLM with tool awareness
    response = await call_llm_agent(
        message=message,
        prefs=prefs,
        tools=["hotelMCP", "web_search", "weatherMCP", "flightSearchMCP", "transportMCP"],
        mode="plan"
    )

    # 4. Update preferences if the LLM found new ones
    if "new_prefs" in response:
        await update_user_prefs(user_id, response["new_prefs"])

    # 5. Save generated itinerary
    if "itinerary" in response:
        await save_itinerary(user_id, response["itinerary"])

    return JSONResponse(content={
        "reply": response["text"],
        "photo_url": response.get("photo_url", "")
    })
