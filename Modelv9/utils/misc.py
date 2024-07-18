import json
import google.generativeai as genai
import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

def gemini_client():    #pro model used in transform_snop, formulator
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY_ORIGINAL"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client1():
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY1"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client2():
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY2"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client3():
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY3"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client4():
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY4"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client5():
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY5"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model

def gemini_client6():   
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY6"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model


def vertexai_client():
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    vertexai.init(project = config["PROJECT_ID"], location="us-central1") # Replace with your project ID and region 
    model = GenerativeModel(
        f"""projects/{config["PROJECT_ID"]}/locations/us-central1/endpoints/{config["ENDPOINT_ID"]}""", # Replace with your endpoint ID
    )
    # print(f"""projects/{config["PROJECT_ID"]}/locations/us-central1/endpoints/{config["ENDPOINT_ID"]}""")

    return model

def vertex_ai_llm_call(prompt):
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.2,
        "top_p": 1,
    }

    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    model = vertexai_client()
    
    responses = model.generate_content(
    prompt,
    )
    
    output = responses.text
    return output

def gemini_client_pro():    #pro model used in add_constraints
    with open("/home/jiosaavn9/LLM_Agent_SCO/Modelv9/config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY_PRO"])
    model = genai.GenerativeModel('gemini-1.5-flash')

    return model

def test(prompt):
    model = gemini_client_pro()
    
    output = model.generate_content(prompt)
    output = output.text
    print(output)

# test("what is your token limit? how many words can you take as input?")


