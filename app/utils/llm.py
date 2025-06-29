import json
import re
from datetime import datetime
from .llm_provider import call_llm_agent

# 🔧 Removes triple backticks and optional 'json' language tag
def clean_json_response(text: str) -> str:
    return re.sub(r"^```(?:json)?\n|\n```$", "", text.strip())

# 🔄 Streaming version (used by /agent-stream)
async def extract_trip_info_stream(message: str, prefs: dict):
    prompt_template = """
You are Dude, a friendly and smart AI travel assistant in PLANNING MODE.

Your job is to extract structured trip information from the user's message.

User Message: {message}
User Preferences: {prefs}
Time: {now}

Extract the following fields:
- origin (e.g., "London")
- destination (e.g., "Milan")
- dates: {{ "start": "YYYY-MM-DD", "end": "YYYY-MM-DD" }}
- type: list of ["flight", "hotel", "car"]
- budget: if mentioned, return as: {{ "flight": "€300", "hotel": "€400" }}
- updated_prefs: user preferences changed
- follow_up: ask for missing info
- complete: true if destination and dates.start exist; origin can be inferred from preferences if missing.
- If origin is missing in the user message, infer it from preferences["home_city"] if available.
- If still missing, leave it blank and include "origin" in "missing_fields".

🎯 Always return a valid JSON response like:
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
    prompt = prompt_template.format(
        message=message,
        prefs=json.dumps(prefs, ensure_ascii=False),
        now=datetime.now().isoformat()
    )

    yield {"stage": "llm_prompt_ready", "prompt_preview": prompt[:500] + "..."}

    try:
        raw_response = await call_llm_agent(prompt, prefs, tools=["hotel", "flight", "car"], mode="plan")
        yield {"stage": "llm_response_received", "raw_response": raw_response}
    except Exception as e:
        yield {"stage": "error", "error": f"LLM error: {str(e)}"}
        return

    try:
        cleaned = clean_json_response(raw_response)
        parsed = json.loads(cleaned)
        home_city = prefs.get("home_city")
        if not parsed.get("origin") and home_city:
            parsed["origin"] = home_city
            parsed.setdefault("updated_prefs", {})
            parsed["updated_prefs"]["origin_inferred"] = True
            if parsed.get("missing_fields") and "origin" in parsed["missing_fields"]:
                parsed["missing_fields"].remove("origin")
            yield {"stage": "inference_note", "note": f"Inferred origin from prefs: {home_city}"}

        yield {"stage": "trip_info_parsed", "data": parsed, "final_info": parsed}
    except Exception as e:
        yield {"stage": "error", "error": f"JSON parsing failed: {str(e)}"}
        return

# 🔁 Classic non-stream version (used by /agent)
async def extract_trip_info(message, prefs):
    prompt_template = """
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

🎯 Always return a valid JSON like:
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
    prompt = prompt_template.format(
        message=message,
        prefs=json.dumps(prefs, ensure_ascii=False),
        now=datetime.now().isoformat()
    )

    try:
        raw_response = await call_llm_agent(prompt, prefs, tools=["hotel", "flight", "car"], mode="plan")
        cleaned = clean_json_response(raw_response)
        parsed = json.loads(cleaned)
        if not parsed.get("origin") and prefs.get("home_city"):
            parsed["origin"] = prefs["home_city"]
            parsed.setdefault("updated_prefs", {})
            parsed["updated_prefs"]["origin_inferred"] = True
            if parsed.get("missing_fields") and "origin" in parsed["missing_fields"]:
                parsed["missing_fields"].remove("origin")
        return parsed
    except Exception as e:
        return {
            "complete": False,
            "type": [],
            "origin": None,
            "destination": None,
            "dates": {},
            "updated_prefs": {},
            "follow_up": f"⚠️ Could not parse LLM response: {str(e)}"
        }
