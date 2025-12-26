import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import argopy
import google.generativeai as genai
import pandas as pd

# Setup Gemini
genai.configure(api_key="AIzaSyDfSjl5uq3fPSPujE6q75yNLqUCP5anVdg")
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

# Allow Frontend to talk to Backend
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class UserRequest(BaseModel):
    text: str

SYSTEM_PROMPT = """
You are an Oceanographic API Agent. Extract parameters from the user's request.
Return ONLY a Python dictionary.
Example 1: "Float 5906914" -> {"type": "float", "id": 5906914}
Example 2: "Temperature in Arabian Sea" -> {"type": "region", "bounds": [60, 75, 10, 25]} 
Bounds format: [min_lon, max_lon, min_lat, max_lat]
"""

@app.post("/query")
async def process_query(request: UserRequest):
    # 1. AI interprets the user's intent
    ai_resp = model.generate_content([SYSTEM_PROMPT, request.text]).text.strip()
    params = eval(ai_resp) # Convert string response to dict

    try:
        # 2. Argopy fetches data from the Cloud (ERDDAP)
        if params['type'] == 'float':
            fetcher = argopy.DataFetcher().float(params['id'])
        else:
            # Default to a 1-month window for regions to keep it fast
            b = params['bounds']
            fetcher = argopy.DataFetcher().region([b[0], b[1], b[2], b[3], 0, 500, '2023-01', '2023-02'])
        
        # 3. Clean and return data
        ds = fetcher.to_xarray()
        # Rename columns to be frontend-friendly
        df = ds.to_dataframe().reset_index()
        df = df[['PLATFORM_NUMBER', 'PRES', 'TEMP', 'PSAL', 'LATITUDE', 'LONGITUDE']].head(1000)
        
        return {
            "status": "success",
            "parameters": params,
            "data": df.to_dict(orient="records")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)