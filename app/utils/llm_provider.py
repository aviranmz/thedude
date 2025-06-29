
import os

PROVIDER = os.getenv("LLM_PROVIDER", "openai").lower()

if PROVIDER == "openai":
    from .llm_openai import call_openai as _call_llm
elif PROVIDER == "gemini":
    from .llm_gemini import call_gemini as _call_llm
elif PROVIDER == "claude":
    from .llm_claude import call_claude as _call_llm
else:
    raise ValueError(f"Unsupported LLM_PROVIDER: {PROVIDER}")

async def call_llm_agent(message, prefs, tools, mode="plan"):
    return await _call_llm(message, prefs, tools, mode)
