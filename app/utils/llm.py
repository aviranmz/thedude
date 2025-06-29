import json
from .llm_provider import call_llm_agent
from datetime import datetime

async def extract_trip_info(message, prefs):
    LLM_TEMPLATE = """
You are Dude, a friendly and smart AI travel assistant in PLANNING MODE.

Your job is to extract structured trip information from the user's message.

User Message: {message}
User Preferences: {prefs}
Time: {now}

Extract the following fields:
- origin (departure city, e.g., "London")
- destination (arrival city, e.g., "Milan")
- dates: with fields 'start' and 'end' in format 'YYYY-MM-DD'
- type: list including any of ["flight", "hotel", "car"]
- budget: if mentioned, return as: {{ "flight": "€300", "hotel": "€400" }}
- updated_prefs: return changes in user preferences (like class, budget, etc.)
- follow_up: only include if key data (like destination or dates) is missing
- complete: true if destination, origin, and start date are present

✈️ If the user says something like "from Paris to Rome", extract:
  - origin = "Paris"
  - destination = "Rome"

🎯 Always return a valid JSON in this format:
{{
  "complete": true,
  "type": ["hotel", "flight"],
  "origin": "London",
  "destination": "Milan",
  "dates": {{"start": "2025-11-11", "end": "2025-11-14"}},
  "budget": {{"flight": "€300", "hotel": "€400"}},
  "updated_prefs": {{}},
  "follow_up": ""
}}
"""


    prompt = LLM_TEMPLATE.format(message=message, prefs=str(prefs), now=datetime.now().isoformat())
    raw_response = await call_llm_agent(prompt, prefs, tools=["hotel", "flight", "car"], mode="plan")

    try:
        return json.loads(raw_response)
    except json.JSONDecodeError:
        return {
            "complete": False,
            "type": [],
            "destination": None,
            "dates": {},
            "updated_prefs": {},
            "follow_up": "⚠️ Could not parse LLM response."
        }