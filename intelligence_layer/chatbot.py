import os
import json
from langchain_groq import ChatGroq

# ---------------------------------------
# Initialize LLM
# ---------------------------------------
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

SUPPORTED_VARIABLES = [
    "temperature", "salinity",
    "oxygen", "nitrate", "ph",
    "chlorophyll", "backscattering"
]

# ---------------------------------------
# LLM-based intent router
# ---------------------------------------
def route_query(user_query: str) -> dict:
    prompt = f"""
You are an oceanography assistant.

Given a user query, extract intent and variable.

Valid intents:
- PROFILE
- PROFILE_RANGE
- MAP
- SUMMARY
- CONDITION

Valid variables:
{SUPPORTED_VARIABLES}

Return ONLY valid JSON.

Examples:
User: Show oxygen profile
{{"intent":"PROFILE","variable":"oxygen"}}

User: Show oxygen between 0 and 500 dbar
{{"intent":"PROFILE_RANGE","variable":"oxygen","min_depth":0,"max_depth":500}}

User: Where are the floats?
{{"intent":"MAP"}}

User: What is the ocean condition in Indian Ocean?
{{"intent":"CONDITION"}}

User query:
{user_query}
"""

    try:
        response = llm.invoke(prompt).content.strip()
        return json.loads(response)
    except Exception:
        return {"intent": "UNKNOWN"}
