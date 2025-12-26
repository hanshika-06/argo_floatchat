# intelligence_layer/chatbot.py

def route_query(query: str):
    q = query.lower()

    # Map-related queries
    if "map" in q or "location" in q or "where" in q:
        return {"intent": "MAP"}

    # Profile / depth queries
    if "profile" in q or "depth" in q or "vertical" in q:
        for var in ["temperature", "salinity", "oxygen", "chlorophyll", "nitrate"]:
            if var in q:
                return {"intent": "PROFILE", "variable": var}
        return {"intent": "PROFILE", "variable": None}

    # Summary queries
    if "summary" in q or "mean" in q or "average" in q:
        return {"intent": "SUMMARY"}

    return {"intent": "UNKNOWN"}
