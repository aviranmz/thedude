
import logging
from app.utils.memory import get_user_preferences, save_user_preferences, log_interaction
from app.utils.llm import extract_trip_info
from app.utils.api_gateway import call_trip_api

async def handle_user_request(data):
    user_id = data.get("user_id")
    message = data.get("message")
    channel = data.get("channel", "telegram")
    logging.info(f"Handling request from user {user_id} in channel {channel}: {message}")

    # Step 1: Log input
    await log_interaction(user_id, message, "input", channel)

    # Step 2: Load preferences
    prefs = await get_user_preferences(user_id)
    logging.info(f"Loaded preferences for user {user_id}: {prefs}")
    logging.info(f"User {user_id} preferences: {prefs}")
    # Step 3: Extract trip intent from LLM
    trip_info = await extract_trip_info(message, prefs)
    logging.info(f"Extracted trip info for user {user_id}: {trip_info}")
    # Step 4: If info missing, ask for more
    if not trip_info.get("complete"):
        reply = trip_info.get("follow_up", "Can you clarify your travel destination or dates?")
        await log_interaction(user_id, reply, "output")
        return {"reply": reply}

    # Step 5: Call relevant API (hotels, flights, cars)
    logging.info(f"DEBUG trip_info keys: {trip_info.keys()}")
    logging.info(f"DEBUG origin: {trip_info.get('origin')}")
    results = await call_trip_api(trip_info)

    # Step 6: Format response and log
    reply = results.get("formatted_reply", "Here are your trip details!")
    await log_interaction(user_id, reply, "output")

    # Step 7: Save updated preferences if any
    if trip_info.get("updated_prefs"):
        await save_user_preferences(user_id, trip_info["updated_prefs"])

    return {"reply": reply}
