import json
import google.generativeai as genai

def gemini_client():
    with open("/home/g2021ume1126/LLM_Agent_SCO/LLM_Agent_SCO/Modelv5 copy/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model