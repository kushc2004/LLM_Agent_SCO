import base64
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models


def multiturn_generate_content():
    vertexai.init(project="llm-finetuning-427205", location="us-central1") # Replace with your project ID and region 
    model = GenerativeModel(
        "projects/llm-finetuning-427205/locations/us-central1/endpoints/386550904930697216", # Replace with your endpoint ID
        system_instruction=[textsi_1]
    )
    chat = model.start_chat()
    print(chat.send_message(
        [text1_1],
        generation_config=generation_config,
        safety_settings=safety_settings
    ))
    print(chat.send_message(
        [text2_1],
        generation_config=generation_config,
        safety_settings=safety_settings
    )) 

text1_1 = """## Description
Location Allocation, Suppose that you are a flight planner for an airline. For a given day, you have sold tickets for flights across the country, and you have a plan for operating your aircraft fleet to service all of these flights. 
Let us say that on this day, there is a weather event (such as a snowstorm) that inhibits the airports from operating at full capacity. This means that some flights have to get cancelled. When a flight will be cancelled, the aircrafts assigned to these flights have to be re-routed. So the question becomes: how can airlines decide which flights to operate/cancel and how to best re-route the aircrafts?
"""

text2_1 = """Please formulate the objective function and constraints for this problem."""


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

multiturn_generate_content()