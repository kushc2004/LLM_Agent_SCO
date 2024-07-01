import json
import google.generativeai as genai

def gemini_client():
    with open("/home/ckushj/LLM_Agent_SCO/modelv8/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model