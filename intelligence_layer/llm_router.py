from langchain_groq import ChatGroq

llm = ChatGroq(
    groq_api_key="YOUR_GROQ_API_KEY",
    model_name="llama3-70b-8192"
)

def llm_route_query(user_query):
    prompt = f"""
You are an ocean data assistant.

User query:
"{user_query}"

Classify the intent and output JSON ONLY in this format:

{{
  "intent": "MAP | PROFILE | SUMMARY",
  "variable": "temperature | salinity | oxygen | nitrate | ph | chlorophyll | backscattering | null"
}}

Rules:
- MAP → location / where / map
- PROFILE → depth / profile / vertical
- SUMMARY → summary / overview
- variable is null for MAP and SUMMARY
"""

    response = llm.invoke(prompt).content
    return response
