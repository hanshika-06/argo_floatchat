import os
from langchain_groq import ChatGroq

def route_query(user_query: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Please set it as an environment variable."
        )

    llm = ChatGroq(
        api_key=api_key,
        model="llama3-8b-8192"
    )

    prompt = (
        "Classify the user intent into one of the following labels:\n"
        "TREND, PROFILE, DEPTH, SUMMARY.\n\n"
        f"User query: {user_query}\n"
        "Return ONLY the label."
    )

    return llm.invoke(prompt).content.strip()
