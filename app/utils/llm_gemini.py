
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

LLM_PROMPT_TEMPLATE = """
You are Dude, a warm, funny, and helpful AI travel planner.
User message: {message}
User preferences: {prefs}
Available tools: {tools}
"""

async def call_gemini(message, prefs, tools, mode="plan"):
    model = genai.GenerativeModel("gemini-pro")
    prompt = LLM_PROMPT_TEMPLATE.format(message=message, prefs=str(prefs), tools=", ".join(tools))
    response = model.generate_content(prompt)
    return {
        "text": response.text,
        "new_prefs": {"last_message": message},
        "itinerary": {"days": [], "summary": "Generated trip plan"},
        "photo_url": "https://example.com/sample.jpg"
    }
