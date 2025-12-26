import json

def parse_llm_response(response):
    try:
        return json.loads(response)
    except Exception:
        return {"intent": "UNKNOWN", "variable": None}
