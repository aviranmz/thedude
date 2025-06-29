from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # Make sure this is set

async def call_openai(message, prefs, tools, mode="plan"):
    system_prompt = (
        "You are Dude, a warm, funny, and helpful AI travel planner that supports multiple languages including Hebrew. "
        "Help the user plan a trip by understanding their message and preferences. "
        "Extract structured trip information even from Hebrew text. "
        "Respond ONLY with JSON."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    response = await client.chat.completions.create(
        model="gpt-4o",  # or gpt-3.5-turbo if you're not using GPT-4
        messages=messages,
        temperature=0.7  # Use this for structured JSON replies if using GPT-4o
    )

    return response.choices[0].message.content
