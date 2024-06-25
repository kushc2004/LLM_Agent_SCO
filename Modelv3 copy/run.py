import json
import os
import sys
import re
from utils import misc
from utils.add_constraints import *
from utils.transform_snop import *
from agents.formulator import Formulator
from agents.agent import Agent
from agents.manager import GroupChatManager
from agents.programmer import Programmer
from agents.evaluator import Evaluator


def generate_snop(path):
    transform_problem(path)
    generate_constraints(path)

def run_formulator(self, path):
    with open(path + "/input.json", "r") as f:
            state = json.load(f)
    Formulator(client=None).generate_reply(task="formulate",state=state, sender=self)

# run_formulator(self=Agent)

def run_manager(self, path):
    
    with open(path + "/input_wc.json", "r") as f:
            state = json.load(f)
    #intialise logging
    state["log_folder"] = f"{path}/log"
    formulator = Formulator(Agent)
    programmer = Programmer(Agent)
    evaluator = Evaluator(Agent)

    manager = GroupChatManager(
        agents=[
            formulator,
            programmer,
            evaluator
        ],
    )
    manager.solve(state)

def run_programmer(self, path):
    with open(path+ "/input_formulated.json", "r") as f:
            state = json.load(f)
    
    program = Programmer(Agent)
    program._generate_code_from_formulation(state=state)

def run_evaluator(self, path):
    with open(path+ "/output_code.json", "r") as f:
            state = json.load(f)
    evaluate=Evaluator(Agent)
    evaluate.generate_reply(state=state, sender=self ,task="Evaluate, Your responsibility is to run the code and evaluate the performance and correctness of the code.")

def test():
    with open("config.json") as f:
        config = json.load(f)
    
    genai.configure(api_key = config["GEMINI_API_KEY1"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    for i in range(100):
        output = model.generate_content("Hi how are you")
        print(output.text)


# run_programmer(self=Agent)
path="data/problem_3"
# generate_snop(path)
# run_manager(Agent, path)
run_evaluator(Agent, path)
# test()
