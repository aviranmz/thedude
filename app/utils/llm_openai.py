
from openai import OpenAI

client = OpenAI()  # No proxies argument

async def call_openai(message, prefs, tools, mode="plan"):
    system_prompt = (
        "You are Dude, a warm, funny, and helpful AI travel planner. that supports multiple languages including Hebrew."
        "Help the user plan a trip by understanding their message and preferences.Extract structured trip information even from Hebrew text."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content
