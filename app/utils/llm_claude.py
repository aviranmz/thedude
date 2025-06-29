
import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

LLM_PROMPT_TEMPLATE = """
You are Dude, a warm, funny, and helpful AI travel planner.
User message: {message}
User preferences: {prefs}
Available tools: {tools}
"""

async def call_claude(message, prefs, tools, mode="plan"):
    prompt = LLM_PROMPT_TEMPLATE.format(message=message, prefs=str(prefs), tools=", ".join(tools))
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return {
        "text": response.content[0].text,
        "new_prefs": {"last_message": message},
        "itinerary": {"days": [], "summary": "Generated trip plan"},
        "photo_url": "https://example.com/sample.jpg"
    }
