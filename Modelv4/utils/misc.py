import json
import google.generativeai as genai

def gemini_client():
    with open("config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY_ORIGINAL"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client1():
    with open("config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY1"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client2():
    with open("config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY2"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client3():
    with open("config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY3"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model